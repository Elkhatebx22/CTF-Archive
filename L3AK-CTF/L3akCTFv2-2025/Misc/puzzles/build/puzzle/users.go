package puzzle

import (
	"encoding/binary"
	"fmt"
	"math/rand"
	"puzzles/admin"
	"puzzles/config"
	"puzzles/utils"
	"sort"
	"sync"
	"time"

	log "github.com/sirupsen/logrus"
)

type User struct {
	Name            string
	SessionToken    string
	Puzzles         map[string]*Puzzle
	Solves          map[int]int
	ImageOrders     map[int][]int
	PuzzleLock      sync.Mutex
	UserID          int
	RNG             *rand.Rand
	LastRequestTime time.Time
	Points          int
	Level           int
	TotalSolves     int
	CreatedTime     time.Time
	UserVerified    bool
	LastIPAddress   string
}

type ByPoints []*User
type ByTime []*Puzzle

func (b ByPoints) Len() int           { return len(b) }
func (b ByPoints) Swap(i, j int)      { b[i], b[j] = b[j], b[i] }
func (b ByPoints) Less(i, j int) bool { return b[i].Points < b[j].Points }

func (b ByTime) Len() int           { return len(b) }
func (b ByTime) Swap(i, j int)      { b[i], b[j] = b[j], b[i] }
func (b ByTime) Less(i, j int) bool { return b[i].SolvedTime.Before(b[j].SolvedTime) }

var Users map[string]*User
var Usernames []string

var UsersLock sync.Mutex

var AdminAccount *User

func (u *User) String() string {
	return fmt.Sprintf("[%s %s %s]", utils.ColorString(u.Name, utils.HOT_PINK), utils.ColorString(fmt.Sprint(u.UserID), utils.HOT_PINK), utils.ColorString(u.LastIPAddress, utils.LIGHT_GREEN))
}

func InitUsers() {
	UsersLock.Lock()
	defer UsersLock.Unlock()
	Users = make(map[string]*User)
	Usernames = make([]string, 0)
}

func GetUserByName(name string) (*User, error) {
	UsersLock.Lock()
	defer UsersLock.Unlock()
	for _, u := range Users {
		if u.Name == name {
			return u, nil
		}
	}
	return nil, fmt.Errorf("user not found")
}

func GetUserByID(uid int) (*User, error) {
	UsersLock.Lock()
	defer UsersLock.Unlock()
	for _, u := range Users {
		if u.UserID == uid {
			return u, nil
		}
	}
	return nil, fmt.Errorf("user not found")
}

func (u *User) UpdateUserPoints() {
	UsersLock.Lock()
	defer UsersLock.Unlock()
	userPoints := 0
	for _, p := range u.Puzzles {
		userPoints += p.GetStats().CalcPoints()
	}
	u.Points = userPoints

	if userPoints > config.Config.General.VerifyPointsThreshold && !u.UserVerified {
		u.UserVerified = true
		go admin.OpenBrowser(u.UserID, AdminAccount.SessionToken)
		log.Infof("%v: %s, %s", u, utils.ColorString("thats a lot of points", utils.BLUE), utils.ColorString("asking the admin to make sure everything's alright", utils.VIOLET))
	}
}

func GetTop100() []*User {
	UsersLock.Lock()
	defer UsersLock.Unlock()
	usersList := []*User{}
	for _, u := range Users {
		if u.Name != "" {
			usersList = append(usersList, u)
		}
	}
	sort.Sort(sort.Reverse(ByPoints(usersList)))

	if len(usersList) > 100 {
		usersList = usersList[:100]
	}

	return usersList
}

func MakeUser() (*User, error) {
	UsersLock.Lock()
	defer UsersLock.Unlock()
	sessionId, err := utils.MakeRandomString(128)
	if err != nil {
		return nil, err
	}

	userID, err := utils.MakeRandomUID()

	if err != nil {
		return nil, err
	}

	u := &User{
		Puzzles:      make(map[string]*Puzzle),
		SessionToken: sessionId,
		Solves:       make(map[int]int),
		ImageOrders:  make(map[int][]int),
		UserID:       int(binary.BigEndian.Uint32(userID[:4])),
		RNG:          rand.New(rand.NewSource(int64(binary.BigEndian.Uint64(userID[4:])))),
		Points:       0,
		Level:        0,
		TotalSolves:  0,
		CreatedTime:  time.Now(),
		UserVerified: false,
	}
	for i, level := range config.Config.Levels {
		u.Solves[i] = 0
		for j := range level.Images {
			u.ImageOrders[i] = append(u.ImageOrders[i], j)
		}
		for k := range u.ImageOrders[i] {
			j := u.RNG.Intn(k + 1)
			u.ImageOrders[i][k], u.ImageOrders[i][j] = u.ImageOrders[i][j], u.ImageOrders[i][k]
		}
	}
	Users[sessionId] = u

	return u, nil
}

func (u *User) GetAgeString() string {
	accountAgeString := utils.TimeHumanReadable(u.CreatedTime)
	accountAgeString = accountAgeString[:len(accountAgeString)-4]
	return accountAgeString
}

func (u *User) GetSolvedPuzzles() []*Puzzle {
	puzzleList := []*Puzzle{}

	for _, p := range u.Puzzles {
		if p.Solved && p.SolvedTime.Before(p.EndTime) {
			puzzleList = append(puzzleList, p)
		}
	}
	sort.Sort(sort.Reverse(ByTime(puzzleList)))
	return puzzleList
}

func (u *User) GetRanking() int {
	users := GetTop100()
	for i, user := range users {
		if user.Name == u.Name {
			return i + 1
		}
	}
	return 0
}

func MakeAdminAccount() {
	adminUser, err := MakeUser()
	if err != nil {
		log.Errorf("couldnt make admin user: %v", err)
		return
	}
	AdminAccount = adminUser
	adminUser.UserVerified = true
	adminUser.Name = config.Config.General.AdminAccountName
	for range len(config.Config.Levels[0].Images) + len(config.Config.Levels[1].Images) + len(config.Config.Levels[2].Images) + len(config.Config.Levels[3].Images) + len(config.Config.Levels[4].Images) {
		currLevel := adminUser.GetCurrentLevel()
		p, err := adminUser.MakeNewPuzzle()
		if err != nil {
			log.Errorf("couldnt make admin puzzle: %v", err)
			return
		}
		p.Solved = true
		p.SolvedTime = time.Now()
		adminUser.IncrementSolvesForLevel(currLevel)
	}
	adminUser.Points += 621

	log.Infof("%s", utils.ColorString("made admin account", utils.LIGHT_PURPLE))
}
