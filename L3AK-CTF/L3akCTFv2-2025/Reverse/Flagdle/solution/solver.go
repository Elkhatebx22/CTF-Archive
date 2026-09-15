package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/md5"
	pb "flagdlesolver/proto"
	"fmt"
	"io"
	"maps"
	"math"
	"net/http"
	"slices"

	"google.golang.org/protobuf/proto"
)

var GameConfig pb.Config

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

func (br *BoardRow) HashRow() []byte {
	var rowBytes []byte
	for _, c := range *br {
		rowBytes = append(rowBytes, byte(c.State))
	}
	hash := md5.Sum(rowBytes)
	return hash[:]
}

func ReadConfig() error {
	resp, err := http.Get("https://meow.sylvie.fyi/static/flagdle.dat")
	if err != nil {
		return fmt.Errorf("unable to read game settings")
	}
	defer resp.Body.Close()
	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("unable to read game settings")
	}
	var encryptedConfig pb.EncryptedSettings
	err = proto.Unmarshal(data, &encryptedConfig)
	if err != nil {
		return fmt.Errorf("invalid game settings")
	}

	encryptedPayload := encryptedConfig.GameSettings
	switch encryptedConfig.EncryptionMode {
	case pb.EncryptedSettings_EncryptionModeNone:
		err = proto.Unmarshal(encryptedPayload, &GameConfig)
	case pb.EncryptedSettings_EncryptionModeXOR:
		if len(encryptedConfig.Key) == 0 {
			return fmt.Errorf("invalid game settings")
		}
		for i, b := range encryptedPayload {
			encryptedPayload[i] = b ^ encryptedConfig.Key[i%len(encryptedConfig.Key)]
		}
		err = proto.Unmarshal(encryptedPayload, &GameConfig)
	case pb.EncryptedSettings_EncryptionModeAES:
		block, e := aes.NewCipher(encryptedConfig.Key)
		if e != nil {
			return fmt.Errorf("invalid game settings")
		}
		blockMode := cipher.NewCBCDecrypter(block, []byte{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0})
		origData := make([]byte, len(encryptedPayload))
		blockMode.CryptBlocks(origData, encryptedPayload)
		unpadding := int(origData[len(origData)-1])
		encryptedPayload = origData[:(len(origData) - unpadding)]
		err = proto.Unmarshal(encryptedPayload, &GameConfig)
	}
	if err != nil {
		return fmt.Errorf("invalid game settings")
	}
	return nil
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

func CalculateSearchSpace(options []map[byte]bool) float64 {
	var n float64
	for _, o := range options {
		n += math.Log10(float64(len(o)))
	}
	return n
}

func GetKnownFlag(options []map[byte]bool) string {
	flag := ""
	for _, o := range options {
		if len(o) == 1 {
			flag += string(slices.Collect(maps.Keys(o))[0])
		} else {
			flag += "?"
		}
	}
	return flag
}

func main() {
	ReadConfig()

	wordlist := GameConfig.Wordlist
	var flagByteOptions []map[byte]bool
	for range len(GameConfig.Games[0].FlagSelectors) {
		byteOption := map[byte]bool{}
		for i := range 96 {
			byteOption[byte(i+32)] = true
		}
		flagByteOptions = append(flagByteOptions, byteOption)
	}
	possible := CalculateSearchSpace(flagByteOptions)
	fmt.Printf("search space: %f\n\n", possible)

	for gameNum, game := range GameConfig.Games {
		targetWord := game.Target
		var guessOptions [][]string
		for _, row := range game.RowHashes {
			var possibleWords []string
			for _, word := range wordlist {
				if bytes.Equal(row, HashGuess(word, targetWord)) {
					possibleWords = append(possibleWords, word)
				}
			}
			guessOptions = append(guessOptions, possibleWords)
		}
		for i, selector := range game.FlagSelectors {
			wordChoices := guessOptions[selector.Row]
			keyByte := game.FlagKey[i]
			charOptions := map[byte]bool{}
			for _, w := range wordChoices {
				charOptions[w[selector.Col]] = true
			}
			var byteChoices []byte
			for _, c := range slices.Collect(maps.Keys(charOptions)) {
				b := c ^ keyByte
				if b >= 32 && b <= 127 {
					byteChoices = append(byteChoices, b)
				}
			}
			currentOptions := slices.Collect(maps.Keys(flagByteOptions[i]))
			for _, o := range currentOptions {
				if !slices.Contains(byteChoices, o) {
					delete(flagByteOptions[i], o)
				}
			}
		}
		possible := CalculateSearchSpace(flagByteOptions)
		knownFlag := GetKnownFlag(flagByteOptions)
		fmt.Printf("game #%d - search space: %f, known flag: %s\n", gameNum, possible, knownFlag)
		knownFlagHash := md5.Sum([]byte(knownFlag))
		if bytes.Equal(knownFlagHash[:], GameConfig.FlagHash) {
			fmt.Println("found flag:", knownFlag)
			break
		}
	}
}
