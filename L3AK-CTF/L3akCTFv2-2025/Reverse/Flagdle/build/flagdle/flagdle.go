package flagdle

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/md5"
	pb "flagdle/proto"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"slices"
	"strings"

	"google.golang.org/protobuf/proto"
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

type FlagdleGame struct {
	Target        string
	Guesses       []string
	Board         Board
	GameID        string
	MaxGuesses    int
	WordLength    int
	Wordlist      map[string]bool
	State         GameState
	FlagSelectors []CellID
	RowHashes     [][]byte
	FlagKey       []byte
}

var GameConfig pb.Config

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

func (g *FlagdleGame) ValidateBoard() (bool, error) {
	if len(g.Board) > len(g.RowHashes) {
		return false, fmt.Errorf("bad board size")
	} else if len(g.Board) < len(g.RowHashes) {
		return false, nil
	}
	for i, r := range g.Board {
		if !bytes.Equal(r.HashRow(), g.RowHashes[i]) {
			return false, nil
		}
	}
	return true, nil
}

func (g *FlagdleGame) SelectFlag() (string, error) {
	var flagBytes []byte
	for _, s := range g.FlagSelectors {
		if s.Col >= g.WordLength || s.Row >= len(g.Guesses) || s.Col >= len(g.Guesses[s.Row]) {
			return "", fmt.Errorf("invalid selector")
		}
		flagBytes = append(flagBytes, g.Guesses[s.Row][s.Col])
	}
	flagKey := g.FlagKey
	if len(flagKey) > 0 {
		for i, b := range flagBytes {
			flagBytes[i] = b ^ flagKey[i]
		}
	}
	flagStr := string(flagBytes)
	if !stringIsASCII(flagStr) {
		return "", fmt.Errorf("flag not ascii")
	}
	return flagStr, nil
}

func (br *BoardRow) HashRow() []byte {
	var rowBytes []byte
	for _, c := range *br {
		rowBytes = append(rowBytes, byte(c.State))
	}
	hash := md5.Sum(rowBytes)
	return hash[:]
}

func (b *Board) ToString() string {
	boardStr := "\n"
	for i, row := range *b {
		rowStr := ""
		for _, cell := range row {
			cellColor := END
			switch cell.State {
			case CellStatusGrey:
				cellColor = GREY_BG
			case CellStatusYellow:
				cellColor = YELLOW_BG
			case CellStatusGreen:
				cellColor = LIGHT_GREEN_BG
			}
			cellStr := ColorString(fmt.Sprintf(" %c ", cell.Letter), cellColor)
			rowStr += cellStr
		}
		boardStr += fmt.Sprintf("%-2d %s", i+1, rowStr)
		if i+1 < len(*b) {
			boardStr += "\n"
		}
	}
	if len(*b) == 0 {
		boardStr += ColorString("[ empty board ]", GREY_BG)
	}
	return boardStr
}

func (g *FlagdleGame) ToString() string {
	return g.Board.ToString()
}

func (g *FlagdleGame) MakeMove(move string) error {
	if len(g.Guesses) >= g.MaxGuesses {
		return fmt.Errorf("out of moves")
	} else if len(move) != g.WordLength {
		return fmt.Errorf("not %d letters long", g.WordLength)
	} else if _, ok := g.Wordlist[strings.ToUpper(move)]; !ok {
		return fmt.Errorf("not in dictionary")
	}
	move = strings.ToUpper(move)
	target := []rune(g.Target)
	states := []CellStatus{}
	for i, c := range move {
		if c == target[i] {
			states = append(states, CellStatusGreen)
			target[i] = '\x00'
		} else {
			states = append(states, CellStatusGrey)
		}
	}
	for i, c := range move {
		if states[i] != CellStatusGreen {
			if slices.Contains(target, c) {
				target[slices.Index(target, c)] = '\x00'
				states[i] = CellStatusYellow
			}
		}
	}
	newRow := BoardRow{}
	for i, c := range move {
		newRow = append(newRow, BoardCell{
			Letter: c,
			State:  states[i],
		})
	}

	g.Guesses = append(g.Guesses, move)
	g.Board = append(g.Board, newRow)

	if g.Target == move {
		g.State = GameState(GameStateWon)
	} else if len(g.Guesses) >= g.MaxGuesses {
		g.State = GameState(GameStateOutOfMoves)
	}

	return nil
}

func (g *FlagdleGame) ReviewGame() (int, string) {
	score := 0
	flag := ""
	if g.Guesses[len(g.Guesses)-1] == g.Target {
		score++
		if len(g.Guesses) == g.MaxGuesses {
			score++
			valid, err := g.ValidateBoard()
			if err == nil && valid {
				score++
				flag, err = g.SelectFlag()
				if err == nil {
					score++
					flagHash := md5.Sum([]byte(flag))
					if bytes.Equal(flagHash[:], GameConfig.FlagHash) {
						score++
					}
				}
			}
		}
	}
	return score, flag
}

func NewGame() (*FlagdleGame, error) {
	allGames := GameConfig.Games
	if len(allGames) == 0 {
		return nil, fmt.Errorf("no games configured")
	}
	selectedGame := allGames[rand.Intn(len(allGames))]
	wordlist := map[string]bool{}
	for _, w := range GameConfig.Wordlist {
		wordlist[w] = true
	}
	var selectors []CellID
	for _, s := range selectedGame.FlagSelectors {
		selectors = append(selectors, CellID{
			Row: int(s.Row),
			Col: int(s.Col),
		})
	}
	game := FlagdleGame{
		Target:        selectedGame.Target,
		GameID:        selectedGame.GameID,
		MaxGuesses:    int(selectedGame.AllowedGuesses),
		WordLength:    int(GameConfig.WordLength),
		Wordlist:      wordlist,
		State:         GameStateInProgress,
		FlagSelectors: selectors,
		RowHashes:     selectedGame.RowHashes,
		FlagKey:       selectedGame.FlagKey,
	}
	return &game, nil
}

func (g *FlagdleGame) Play() error {
	fmt.Printf("Flagdle Game ID: %s\n", g.GameID)
	fmt.Println(g.ToString())
	for {
		switch g.State {
		case GameStateInProgress:
			fmt.Printf("\nmove (%d/%d) > ", len(g.Guesses)+1, g.MaxGuesses)
			var move string
			fmt.Scanln(&move)
			err := g.MakeMove(move)
			if err != nil {
				fmt.Println(ColorString("\ninvalid move:", LIGHT_RED), ColorString(fmt.Sprint(err), LIGHTER_RED))
				continue
			}
			fmt.Println(g.ToString())
			continue
		case GameStateWon:
			fmt.Println(ColorString("\nyou won!", LIGHT_GREEN))
			var review string
			score, flag := g.ReviewGame()
			review += strings.Repeat("⭐ ", score)
			review += strings.Repeat("✖️  ", 5-score)
			fmt.Printf("\ngameplay review: %s\n", review)
			if score >= 4 {
				fmt.Printf("\nimpressive performance! here, have a flag: %s\n", flag)
			}
		case GameStateOutOfMoves:
			fmt.Println(ColorString("\ngame over", LIGHT_RED))
		default:
			fmt.Println("\ninvalid game state")
		}
		break
	}
	return nil
}
