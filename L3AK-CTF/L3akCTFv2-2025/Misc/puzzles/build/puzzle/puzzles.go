package puzzle

import (
	"fmt"
	"image/png"
	"os"
	"puzzles/config"
	"puzzles/utils"
	"slices"
	"time"

	"github.com/google/uuid"
	log "github.com/sirupsen/logrus"
)

type Puzzle struct {
	PuzzleID   string
	Name       string
	PuzzleImg  *config.PuzzleImage
	Difficulty int
	Answer     []int
	LastGuess  []int
	StartTime  time.Time
	EndTime    time.Time
	SolvedTime time.Time
	Tries      int
	Solved     bool
	Rows       int
	Cols       int
	Pieces     int
	NumCorrect int
}

type SolvedPuzzleStats struct {
	Difficulty  int
	TimeLimit   int
	TimeToSolve int
	Tries       int
	Points      int
}

func (p *Puzzle) String() string {
	id := utils.ColorString(p.PuzzleID[:8], utils.LIGHT_PINK)
	title := utils.ColorString(fmt.Sprintf("\"%s\"", p.Name), utils.LIGHT_GREEN)
	level := utils.ColorString(fmt.Sprintf("level %d", p.Difficulty+1), utils.HOT_PINK)
	tries := utils.ColorString(fmt.Sprintf("%d tries", p.Tries), utils.BLUE)

	started := utils.ColorString(fmt.Sprintf("started %s", utils.TimeHumanReadable(p.StartTime)), utils.ORANGE)
	expires := utils.ColorString(fmt.Sprintf(" expires %s", utils.TimeHumanReadable(p.EndTime)), utils.PURPLE)

	if p.Solved {
		expires = utils.ColorString(fmt.Sprintf("solved %s", utils.TimeHumanReadable(p.SolvedTime)), utils.PURPLE)
		started = ""
	}

	status := ""
	if p.Solved && p.SolvedTime.After(p.EndTime) {
		status = utils.ColorString("SOLVED ", utils.CYAN) + utils.ColorString("EXPIRED ", utils.RED)
	} else if p.Solved {
		status = utils.ColorString("SOLVED ", utils.CYAN)
	} else if time.Now().After(p.EndTime) {
		status = utils.ColorString("EXPIRED ", utils.RED)
	}

	solves := utils.ColorString(fmt.Sprintf("(%d/%d)", p.NumCorrect, p.Pieces), utils.LIGHT_PINK)

	return fmt.Sprintf("[%s%s %s %s %s %s%s %s]", status, id, title, level, tries, started, expires, solves)
}

func InitPuzzles() {
	for i, level := range config.Config.Levels {
		log.Infof("Splitting level %d images", i)
		for _, puzzleImg := range level.Images {
			log.Infof("		%s ", puzzleImg.FilePath)
			file, err := os.Open(fmt.Sprintf("images/%s", puzzleImg.FilePath))
			if err != nil {
				log.Error("Error opening file:", err)
				continue
			}
			defer file.Close()

			img, err := png.Decode(file)
			if err != nil {
				log.Error("Error decoding PNG:", err)
				continue
			}
			puzzleImg.ImageChunks, puzzleImg.TileWidth, puzzleImg.TileHeight, err = SplitImage(img, level.PuzzleWidth, level.PuzzleHeight)
			if err != nil {
				log.Error("Error splitting PNG:", err)
				continue
			}
		}
	}
}

func (u *User) GetSolvesForLevel(level int) int {
	u.PuzzleLock.Lock()
	defer u.PuzzleLock.Unlock()
	solves, exists := u.Solves[level]
	if !exists {
		return 0
	}
	return solves
}

func (u *User) IncrementSolvesForLevel(level int) {
	u.PuzzleLock.Lock()
	defer u.PuzzleLock.Unlock()
	u.ImageOrders[level] = u.ImageOrders[level][:len(u.ImageOrders[level])-1]
	_, exists := u.Solves[level]
	if !exists {
		u.Solves[level] = 1
		return
	}
	u.Solves[level] += 1
	u.TotalSolves += 1
	u.UpdateUserPoints()

}

func (u *User) CheckLevelComplete(level int) (bool, error) {
	if len(config.Config.Levels) <= level {
		return false, fmt.Errorf("level %d doesnt exist", level)
	}
	l := config.Config.Levels[level]
	if u.GetSolvesForLevel(level) >= l.SolvesRequired {
		return true, nil
	}
	return false, nil
}

func (u *User) GetCurrentLevel() int {
	currentLevel := 0
	for i := range config.Config.Levels {
		complete, err := u.CheckLevelComplete(i)
		if err != nil || !complete {
			return currentLevel
		}
		currentLevel += 1
	}
	u.Level = currentLevel
	return currentLevel
}

func (u *User) GetInProgressPuzzle() *Puzzle {
	u.CleanPuzzles()
	currentLevel := u.GetCurrentLevel()
	u.PuzzleLock.Lock()
	defer u.PuzzleLock.Unlock()
	for _, puzzle := range u.Puzzles {
		if puzzle.Difficulty != currentLevel || puzzle.Solved || time.Now().After(puzzle.EndTime) {
			continue
		}
		var correctOrder []int

		for i := range puzzle.Answer {
			correctOrder = append(correctOrder, slices.Index(puzzle.LastGuess, i))
		}

		puzzle.Answer = correctOrder
		return puzzle
	}
	return nil
}

func (u *User) DeletePuzzle(puzzleID string) error {
	u.PuzzleLock.Lock()
	defer u.PuzzleLock.Unlock()
	p, exists := u.Puzzles[puzzleID]

	if !exists {
		return fmt.Errorf("no such puzzle %s", puzzleID)
	}

	log.Infof("%v: %s %v", u, utils.ColorString("skipped puzzle", utils.YELLOW), p)
	delete(u.Puzzles, puzzleID)

	return nil
}

func (u *User) MakeNewPuzzle() (*Puzzle, error) {
	difficulty := u.GetCurrentLevel()
	levelConfig := config.Config.Levels[difficulty]
	rows := levelConfig.PuzzleWidth
	cols := levelConfig.PuzzleHeight

	puzzleImg, err := u.RandomImageByLevel(difficulty)
	if err != nil {
		return nil, err
	}

	u.PuzzleLock.Lock()
	defer u.PuzzleLock.Unlock()

	chunks := puzzleImg.ImageChunks

	shuffled := make([]*config.Chunk, len(chunks))

	copy(shuffled, chunks)

	for i := range shuffled {
		j := u.RNG.Intn(i + 1)
		shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
	}

	var correctOrder []int
	var originalOrder []int

	for i := range shuffled {
		originalOrder = append(originalOrder, shuffled[i].Index)
	}

	for i := range originalOrder {
		correctOrder = append(correctOrder, slices.Index(originalOrder, i))
	}

	puzzleID := uuid.NewString()
	newPuzzle := &Puzzle{
		PuzzleID:   puzzleID,
		PuzzleImg:  puzzleImg,
		Name:       puzzleImg.Title,
		Answer:     correctOrder,
		LastGuess:  originalOrder,
		Difficulty: difficulty,
		StartTime:  time.Now(),
		EndTime:    time.Now().Add(time.Second * time.Duration(levelConfig.TimeLimit)),
		SolvedTime: time.Now(),
		Solved:     false,
		Tries:      0,
		Rows:       rows,
		Cols:       cols,
		Pieces:     rows * cols,
		NumCorrect: 0,
	}

	for i := range newPuzzle.Answer {
		if newPuzzle.Answer[i] == i {
			newPuzzle.NumCorrect += 1
		}
	}

	u.Puzzles[puzzleID] = newPuzzle

	return newPuzzle, nil
}

func (u *User) RandomImageByLevel(level int) (*config.PuzzleImage, error) {
	u.PuzzleLock.Lock()
	defer u.PuzzleLock.Unlock()
	allImages := config.Config.Levels[level].Images
	if len(allImages) < 1 && len(u.ImageOrders[level]) == len(allImages) {
		return nil, fmt.Errorf("no images configured for level %d", level)
	}
	if len(u.ImageOrders[level]) == 0 {
		return nil, fmt.Errorf("all puzzles solved")
	}
	var randomIndex int
	randomIndex, u.ImageOrders[level] = u.ImageOrders[level][0], u.ImageOrders[level][1:]
	u.ImageOrders[level] = append(u.ImageOrders[level], randomIndex)
	return allImages[randomIndex], nil
}

func (u *User) CleanPuzzles() {
	u.PuzzleLock.Lock()
	defer u.PuzzleLock.Unlock()
	for guid, puzzle := range u.Puzzles {
		delete_key := false
		if !puzzle.Solved {
			if time.Now().After(puzzle.EndTime) {
				delete_key = true
			}
			if puzzle.Tries < 1 && time.Now().After(puzzle.StartTime.Add(time.Minute*1)) {
				delete_key = true
			}
		}
		if delete_key {
			log.Infof("%v: %s %v", u, utils.ColorString("cleaned up puzzle", utils.YELLOW), puzzle)
			delete(u.Puzzles, guid)
		}
	}
}

func (s *SolvedPuzzleStats) CalcPoints() int {
	return config.Config.Levels[s.Difficulty].BasePoints*(2-s.TimeToSolve/s.TimeLimit) - s.Tries
}

func (p *Puzzle) GetStats() *SolvedPuzzleStats {
	stats := &SolvedPuzzleStats{
		Difficulty:  p.Difficulty,
		TimeLimit:   config.Config.Levels[p.Difficulty].TimeLimit * 1000,
		Tries:       p.Tries,
		TimeToSolve: 0,
	}
	if !p.Solved {
		return stats
	}

	if p.SolvedTime.After(p.EndTime) {
		return stats
	}

	stats.TimeToSolve = int(p.SolvedTime.Sub(p.StartTime).Milliseconds())

	return stats
}
