package main

import (
	"bufio"
	"crypto/aes"
	"crypto/cipher"
	"crypto/md5"
	cryptorand "crypto/rand"
	pb "flagdle/proto"
	"fmt"
	"math/rand"
	"os"
	"slices"
	"strings"

	"github.com/google/uuid"
	"google.golang.org/protobuf/proto"
)

type CellStatus int

const (
	CellStatusEmpty CellStatus = iota
	CellStatusGrey
	CellStatusYellow
	CellStatusGreen
)

type BoardCell struct {
	Letter rune
	State  CellStatus
}

type BoardRow []BoardCell

type Board []BoardRow

type CellID struct {
	Row int
	Col int
}

var usedSolutionWords []string

func GenerateRandomUppercaseString(length int) []byte {
	const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	b := make([]byte, length)
	for i := range b {
		b[i] = charset[rand.Intn(len(charset))]
	}
	return b
}
func (br *BoardRow) HashRow() []byte {
	var rowBytes []byte
	for _, c := range *br {
		rowBytes = append(rowBytes, byte(c.State))
	}
	hash := md5.Sum(rowBytes)
	return hash[:]
}
func GuesslistIsSufficient(guesses []string, target string) bool {
	for _, c := range target {
		existing := 0
		for _, w := range guesses {
			n := strings.Count(w, string(c))
			existing += n
		}
		if existing == 0 {
			return false
		}
	}
	return true
}

func GenerateSelectors(guesses []string, target string) []CellID {
	var selectors []CellID
	for _, c := range target {
		var allPossibleCells, desiredCells []CellID
		for row, w := range guesses {
			for col, letter := range w {
				if letter != c {
					continue
				}
				id := CellID{
					Row: row,
					Col: col,
				}
				allPossibleCells = append(allPossibleCells, id)
				if !slices.Contains(selectors, id) {
					desiredCells = append(desiredCells, id)
				}
			}
		}
		var selector CellID
		if len(desiredCells) > 0 {
			selector = desiredCells[rand.Intn(len(desiredCells))]
		} else {
			selector = allPossibleCells[rand.Intn(len(allPossibleCells))]
		}
		selectors = append(selectors, selector)
	}
	return selectors
}

func LoadDictionary(path string) (map[string]bool, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	set := make(map[string]bool)
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		word := strings.TrimSpace(scanner.Text())
		if word == "" {
			continue
		}
		set[strings.ToUpper(word)] = true
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}

	return set, nil
}

func HashGuess(guess, targetStr string) []byte {
	target := []rune(targetStr)
	states := []CellStatus{}
	for i, c := range guess {
		if c == target[i] {
			states = append(states, CellStatusGreen)
			target[i] = '\x00'
		} else {
			states = append(states, CellStatusGrey)
		}
	}
	for i, c := range guess {
		if states[i] != CellStatusGreen {
			if slices.Contains(target, c) {
				target[slices.Index(target, c)] = '\x00'
				states[i] = CellStatusYellow
			}
		}
	}
	newRow := BoardRow{}
	for i, c := range guess {
		newRow = append(newRow, BoardCell{
			Letter: c,
			State:  states[i],
		})
	}
	return newRow.HashRow()
}

func GenerateGame(flag string, wordlist []string) *pb.Game {
	flagLen := len(flag)
	numWords := len(wordlist)
	target := GenerateRandomUppercaseString(flagLen)
	targetStr := string(target)
	var flagKey []byte
	for i, b := range target {
		flagKey = append(flagKey, b^flag[i])
	}
	var guessWords []string
	var gameAnswer string
	for {
		guessWords = []string{}
		for {
			if GuesslistIsSufficient(guessWords, targetStr) {
				break
			}
			var newWord string
			for {
				newWord = wordlist[rand.Intn(numWords)]
				if !slices.Contains(guessWords, newWord) {
					break
				}
			}
			guessWords = append(guessWords, newWord)
		}
		gameAnswer = guessWords[len(guessWords)-1]
		if !slices.Contains(usedSolutionWords, gameAnswer) && len(guessWords) <= 32 {
			usedSolutionWords = append(usedSolutionWords, gameAnswer)
			break
		}
	}

	selectors := GenerateSelectors(guessWords, targetStr)
	var rowHashes [][]byte
	for _, guess := range guessWords {
		rowHashes = append(rowHashes, HashGuess(guess, gameAnswer))
	}
	var flagSelectors []*pb.CellID
	for _, selector := range selectors {
		flagSelectors = append(flagSelectors, &pb.CellID{
			Row: int32(selector.Row),
			Col: int32(selector.Col),
		})
	}

	game := pb.Game{
		Target:         gameAnswer,
		AllowedGuesses: int32(len(guessWords)),
		FlagKey:        flagKey,
		RowHashes:      rowHashes,
		FlagSelectors:  flagSelectors,
		GameID:         uuid.New().String(),
	}
	return &game
}

func PKCS5Padding(ciphertext []byte, blockSize int) []byte {
	padding := blockSize - len(ciphertext)%blockSize
	padtext := make([]byte, padding)
	for i := 0; i < padding; i++ {
		padtext[i] = byte(padding)
	}
	return append(ciphertext, padtext...)
}

func main() {
	dict, err := LoadDictionary("dict.txt")
	if err != nil {
		fmt.Println(err)
	}
	flagStr := "L3AK{m4yb3_th3_r341_w0rd_w45_th3_fr13nd5_w3_m4d3_al0ng_th3_w4y}"
	var wordlist []string
	for w := range dict {
		wordlist = append(wordlist, w)
	}
	flagHash := md5.Sum([]byte(flagStr))
	gameSettings := pb.Config{
		WordLength: 5,
		Wordlist:   wordlist,
		FlagHash:   flagHash[:],
	}
	for i := range 1000 {
		game := GenerateGame(flagStr, wordlist)
		gameSettings.Games = append(gameSettings.Games, game)
		fmt.Println(i + 1)
	}
	gameConfigBytes, err := proto.Marshal(&gameSettings)
	if err != nil {
		fmt.Println(err)
	}

	encryptionKey := make([]byte, 32)
	if _, err := cryptorand.Read(encryptionKey); err != nil {
		panic(err.Error())
	}
	encryptionIV := []byte{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}

	block, err := aes.NewCipher(encryptionKey)
	if err != nil {
		panic(err.Error())
	}
	blockSize := block.BlockSize()
	origData := PKCS5Padding(gameConfigBytes, blockSize)
	blockMode := cipher.NewCBCEncrypter(block, encryptionIV)
	crypted := make([]byte, len(origData))
	blockMode.CryptBlocks(crypted, origData)

	encryptedSettings := pb.EncryptedSettings{
		EncryptionMode: pb.EncryptedSettings_EncryptionModeAES,
		Key:            encryptionKey,
		GameSettings:   crypted,
	}

	encryptedGameConfig, err := proto.Marshal(&encryptedSettings)
	if err != nil {
		fmt.Println(err)
	}

	os.WriteFile("flagdle.dat", encryptedGameConfig, 0644)
}
