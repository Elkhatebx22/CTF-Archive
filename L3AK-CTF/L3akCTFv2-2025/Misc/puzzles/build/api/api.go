package api

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"puzzles/config"
	"puzzles/puzzle"
	"puzzles/utils"
	"slices"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
)

type CheckAnswerRequest struct {
	PuzzleID string `json:"puzzle_id"`
	Answer   []int  `json:"answer"`
}

type GetFlagRequest struct {
	Level int `json:"level"`
}

type SetNameRequest struct {
	Name string `json:"name"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

type SkipPuzzleRequest struct {
	PuzzleID string `json:"puzzle_id"`
}

type GetProfileRequest struct {
	Username string `json:"username"`
	UserID   int    `json:"uid"`
}

type PuzzleResponse struct {
	Title     string   `json:"title"`
	Level     int      `json:"level"`
	Artist    string   `json:"artist"`
	URL       string   `json:"url"`
	Pieces    []string `json:"pieces"`
	PuzzleID  string   `json:"puzzle_id"`
	Rows      int      `json:"rows"`
	Cols      int      `json:"cols"`
	Width     int      `json:"width"`
	Height    int      `json:"height"`
	TotalTime int      `json:"puzzle_time"`
	EndTime   int64    `json:"end_time"`
	ShowTimer bool     `json:"show_timer"`
}

type CheckAnswerResponse struct {
	Correct     bool   `json:"correct"`
	TimeExpired bool   `json:"expired,omitempty"`
	WinMessage  string `json:"winmessage,omitempty"`
}

type SetNameResponse struct {
	Name   string `json:"name"`
	UserID int    `json:"uid"`
}

type GetSolvesResponse struct {
	Solves    map[int]int `json:"solves"`
	Required  map[int]int `json:"required"`
	NumLevels int         `json:"n_levels"`
}

type GetFlagResponse struct {
	Flag string `json:"flag"`
}

type SkipPuzzleResponse struct {
	Success bool `json:"success"`
}

type UserResponse struct {
	Name       string `json:"name"`
	Level      int    `json:"level"`
	AccountAge string `json:"account_age"`
	Solves     int    `json:"solves"`
	Points     int    `json:"points"`
	UserID     int    `json:"uid"`
}

type LeaderboardUsersResponse struct {
	Users []UserResponse `json:"users"`
}

type SolveResponse struct {
	Title         string `json:"title"`
	Artist        string `json:"artist"`
	URL           string `json:"url"`
	Level         int    `json:"level"`
	SolvedTime    string `json:"solved_time"`
	SolveDuration string `json:"solve_duration"`
	Tries         int    `json:"tries"`
	Points        int    `json:"points"`
}

type GetProfileResponse struct {
	Name       string          `json:"name"`
	Ranking    int             `json:"ranking"`
	Level      int             `json:"level"`
	AccountAge string          `json:"account_age"`
	Solves     int             `json:"solves"`
	Points     int             `json:"points"`
	Puzzles    []SolveResponse `json:"puzzles"`
}

func jsonResponse(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(v)
}

func respondWithError(w http.ResponseWriter, err error) {
	jsonResponse(w, ErrorResponse{
		Error: err.Error(),
	})
}

func checkAuth(r *http.Request) (*puzzle.User, error) {
	var remoteIP string
	xForwardedForHeader, forwardedForExists := r.Header["X-Forwarded-For"]
	xRealIP, realIPExists := r.Header[http.CanonicalHeaderKey("X-Real-IP")]
	cfConnecting, cfExists := r.Header[http.CanonicalHeaderKey("CF-Connecting-IP")]
	if cfExists {
		remoteIP = cfConnecting[0]
	} else if forwardedForExists {
		remoteIP = xForwardedForHeader[0]
	} else if realIPExists {
		remoteIP = xRealIP[0]
	} else {
		remoteIP = r.RemoteAddr
	}

	session, err := r.Cookie("session")
	if err != nil {
		if errors.Is(err, http.ErrNoCookie) {
			return nil, fmt.Errorf("not logged in")
		}
		return nil, err
	}

	puzzle.UsersLock.Lock()
	user, exists := puzzle.Users[session.Value]
	puzzle.UsersLock.Unlock()

	if !exists {
		log.Infof("%s: %s (%s)", utils.ColorString(remoteIP, utils.LIGHT_GREEN), utils.ColorString("session not found", utils.ORANGE), utils.ColorString(session.Value, utils.PURPLE))
		return nil, fmt.Errorf("%s: session not found", remoteIP)
	}
	user.LastIPAddress = remoteIP
	if user.Name == "" {
		return user, fmt.Errorf("account not created")
	}

	user.PuzzleLock.Lock()
	defer user.PuzzleLock.Unlock()

	if strings.Contains(r.URL.Path, "/api/checkanswer") || strings.Contains(r.URL.Path, "/api/getflag") || strings.Contains(r.URL.Path, "/api/newpuzzle") || strings.Contains(r.URL.Path, "/api/getplayers") || strings.Contains(r.URL.Path, "/api/profile") {
		if time.Now().Before(user.LastRequestTime.Add(time.Duration(config.Config.General.RateLimitMillis) * time.Millisecond)) {
			log.Infof("%v %s at %s", utils.ColorString(user.Name, utils.HOT_PINK), utils.ColorString("rate limited", utils.ORANGE), utils.ColorString(r.URL.Path, utils.CYAN))
			return user, fmt.Errorf("rate limited")
		}
		user.LastRequestTime = time.Now()
	}

	return user, nil
}

func createUser(w http.ResponseWriter) (*puzzle.User, error) {
	u, err := puzzle.MakeUser()
	if err != nil {
		return nil, err
	}

	cookie := http.Cookie{
		Name:     "session",
		Value:    u.SessionToken,
		Expires:  time.Now().Add(24 * time.Hour),
		HttpOnly: true,
	}

	http.SetCookie(w, &cookie)

	return u, nil
}

func Home(w http.ResponseWriter, r *http.Request) {
	session, err := r.Cookie("session")
	var user *puzzle.User
	if err != nil {
		if errors.Is(err, http.ErrNoCookie) {
			user, err = createUser(w)
			if err != nil {
				respondWithError(w, err)
				return
			}
		} else {
			respondWithError(w, err)
			return
		}
	} else {
		var exists bool
		puzzle.UsersLock.Lock()
		user, exists = puzzle.Users[session.Value]
		puzzle.UsersLock.Unlock()
		if !exists {
			user, err = createUser(w)
			if err != nil {
				respondWithError(w, err)
				return
			}
		}
	}

	w.Header().Set("Cache-Control", "no-cache, no-store, must-revalidate")
	w.Header().Set("Pragma", "no-cache")
	w.Header().Set("Expires", "0")

	if user.Name == "" {
		http.ServeFile(w, r, "templates/setname.html")
	} else {
		http.ServeFile(w, r, "templates/index.html")
	}
}

func Puzzle(w http.ResponseWriter, r *http.Request) {
	_, err := checkAuth(r)
	if err != nil {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	http.ServeFile(w, r, "templates/puzzle.html")
}

func Leaderboard(w http.ResponseWriter, r *http.Request) {
	_, err := checkAuth(r)
	if err != nil {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	http.ServeFile(w, r, "templates/leaderboard.html")
}

func Help(w http.ResponseWriter, r *http.Request) {
	_, err := checkAuth(r)
	if err != nil {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	http.ServeFile(w, r, "templates/help.html")
}

func Profile(w http.ResponseWriter, r *http.Request) {
	_, err := checkAuth(r)
	if err != nil {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	http.ServeFile(w, r, "templates/profile.html")
}

func SetName(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	var setNameRequest SetNameRequest
	decodeErr := json.NewDecoder(r.Body).Decode(&setNameRequest)
	if decodeErr != nil {
		respondWithError(w, decodeErr)
		return
	}
	if err == nil {
		w.WriteHeader(http.StatusForbidden)
		respondWithError(w, fmt.Errorf("name already set"))
		log.Infof("%v: %s %s (uid %s)", u, utils.ColorString("failed to change name to", utils.CYAN), utils.ColorString(setNameRequest.Name, utils.PURPLE), utils.ColorString(fmt.Sprint(u.UserID), utils.VIOLET))
		return
	} else if err.Error() == "account not created" {
		s, validateName, err := utils.ValidateUsername(setNameRequest.Name)
		if !validateName {
			w.WriteHeader(http.StatusBadRequest)
			respondWithError(w, fmt.Errorf("invalid username"))
			log.Infof("%v: %s (%s) (uid %s)", utils.ColorString("name validation failed", utils.CYAN), utils.ColorString(setNameRequest.Name, utils.PURPLE), utils.ColorString(err.Error(), utils.LIGHT_PINK), utils.ColorString(fmt.Sprint(u.UserID), utils.VIOLET))
			return
		}
		setNameRequest.Name = s
		if slices.Contains(puzzle.Usernames, setNameRequest.Name) {
			w.WriteHeader(http.StatusBadRequest)
			respondWithError(w, fmt.Errorf("username already taken"))
			log.Infof("%v: %s (uid %s)", utils.ColorString("username taken", utils.CYAN), utils.ColorString(setNameRequest.Name, utils.PURPLE), utils.ColorString(fmt.Sprint(u.UserID), utils.VIOLET))
			return
		}

		u.Name = setNameRequest.Name
		puzzle.Usernames = append(puzzle.Usernames, setNameRequest.Name)
		w.WriteHeader(http.StatusAccepted)
		jsonResponse(w, SetNameResponse{
			Name:   setNameRequest.Name,
			UserID: u.UserID,
		})
		log.Infof("%v: %s (uid %s)", u, utils.ColorString("set username", utils.LIGHT_GREEN), utils.ColorString(fmt.Sprint(u.UserID), utils.VIOLET))
	} else {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}
}

func NewPuzzle(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}

	currentPuzzle := u.GetInProgressPuzzle()

	madePuzzleString := utils.ColorString("loaded puzzle", utils.VIOLET)
	if currentPuzzle == nil {
		var err error
		currentPuzzle, err = u.MakeNewPuzzle()
		if err != nil {
			log.Warnf("error making new puzzle: %v", err)
			respondWithError(w, err)
			return
		}
		madePuzzleString = utils.ColorString("created puzzle", utils.VIOLET)
	}

	var pieces []string

	for _, i := range currentPuzzle.LastGuess {
		pieces = append(pieces, currentPuzzle.PuzzleImg.ImageChunks[i].Data)
	}

	jsonResponse(w, PuzzleResponse{
		Title:     currentPuzzle.PuzzleImg.Title,
		Artist:    currentPuzzle.PuzzleImg.Artist,
		URL:       currentPuzzle.PuzzleImg.URL,
		Pieces:    pieces,
		PuzzleID:  currentPuzzle.PuzzleID,
		Rows:      currentPuzzle.Rows,
		Cols:      currentPuzzle.Cols,
		Width:     currentPuzzle.PuzzleImg.TileWidth,
		Height:    currentPuzzle.PuzzleImg.TileHeight,
		Level:     currentPuzzle.Difficulty,
		TotalTime: config.Config.Levels[currentPuzzle.Difficulty].TimeLimit,
		EndTime:   currentPuzzle.EndTime.UnixMilli(),
		ShowTimer: currentPuzzle.Difficulty >= 0,
	})

	log.Infof("%v: %s %v", u, madePuzzleString, currentPuzzle)
}

func ChallengeHandout(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}
	level4Done, err := u.CheckLevelComplete(4)
	if err != nil {
		respondWithError(w, err)
		return
	}
	if level4Done {
		respondWithError(w, fmt.Errorf("level too low"))
		log.Infof("%v: %s (level %d)", u, utils.ColorString("failed to download source", utils.ORANGE), u.Level)
		return
	}
	log.Infof("%v: %s", u, utils.ColorString("downloaded source", utils.CYAN))
	http.ServeFile(w, r, "puzzles.zip")
}

func CheckAnswer(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}

	var checkAnswerRequest CheckAnswerRequest
	err = json.NewDecoder(r.Body).Decode(&checkAnswerRequest)
	if err != nil {
		respondWithError(w, err)
		return
	}

	p, exists := u.Puzzles[checkAnswerRequest.PuzzleID]

	if !exists {
		respondWithError(w, fmt.Errorf("puzzle doesnt exist"))
		log.Warnf("puzzle %s doesnt exist", checkAnswerRequest.PuzzleID)
		return
	}

	for _, i := range checkAnswerRequest.Answer {
		if i < 0 || i >= len(checkAnswerRequest.Answer) {
			log.Infof("%v: %s", u, utils.ColorString("invalid guess values", utils.LIGHT_PINK))
			respondWithError(w, fmt.Errorf("stop it"))
			return
		}
	}

	p.Tries += 1

	wrong := false
	num_wrong := 0
	solvedStr := ""

	if p.Solved {
		log.Infof("%v: %s", u, utils.ColorString("puzzle already solved", utils.LIGHT_PINK))
		respondWithError(w, fmt.Errorf("puzzle already solved"))
		return
	}

	if len(checkAnswerRequest.Answer) != len(p.Answer) {
		wrong = true
		checkAnswerRequest.Answer = make([]int, len(p.Answer))
		log.Infof("%v: %s", u, utils.ColorString("bad request, resetting", utils.LIGHT_PINK))
		for i := range checkAnswerRequest.Answer {
			checkAnswerRequest.Answer[i] = i
		}
	}

	for i := range p.LastGuess {
		p.LastGuess[i] = slices.Index(p.Answer, checkAnswerRequest.Answer[i])
	}

	for i := range p.Answer {
		if p.Answer[i] != checkAnswerRequest.Answer[i] {
			wrong = true
			num_wrong += 1
		}
	}
	p.NumCorrect = p.Pieces - num_wrong
	winMessageLog := ""
	if wrong {
		w.WriteHeader(http.StatusNotAcceptable)
		jsonResponse(w, CheckAnswerResponse{
			Correct: false,
		})
		solvedStr = utils.ColorString("wrong", utils.LIGHT_RED)
	} else {
		outOfTime := time.Now().After(p.EndTime)
		var winMsg string
		if outOfTime {
			winMsg = config.Config.General.ExpiredWinMessages[u.RNG.Intn(len(config.Config.General.ExpiredWinMessages))].Text
			winMessageLog = fmt.Sprintf(" (%s)", utils.ColorString(winMsg, utils.YELLOW))
		} else {
			winMsg = config.Config.General.WinMessages[u.RNG.Intn(len(config.Config.General.WinMessages))].Text
			winMessageLog = fmt.Sprintf(" (%s)", utils.ColorString(winMsg, utils.GREEN))
		}
		jsonResponse(w, CheckAnswerResponse{
			Correct:     true,
			TimeExpired: outOfTime,
			WinMessage:  winMsg,
		})
		if !outOfTime {
			p.Solved = true
			p.SolvedTime = time.Now()
			u.IncrementSolvesForLevel(p.Difficulty)
			solvedStr = utils.ColorString("correct", utils.GREEN)
		} else {
			solvedStr = utils.ColorString("correct", utils.YELLOW)
		}

	}

	log.Infof("%v: %s %v %s", u, solvedStr, p, winMessageLog)
}

func GetSolves(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}

	req := make(map[int]int)
	for i, v := range config.Config.Levels {
		req[i] = v.SolvesRequired
	}
	jsonResponse(w, GetSolvesResponse{
		Solves:    u.Solves,
		Required:  req,
		NumLevels: len(config.Config.Levels),
	})
}

func SkipPuzzle(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}

	var skipPuzzleRequest SkipPuzzleRequest
	err = json.NewDecoder(r.Body).Decode(&skipPuzzleRequest)
	if err != nil {
		respondWithError(w, err)
		return
	}
	err = u.DeletePuzzle(skipPuzzleRequest.PuzzleID)

	if err != nil {
		log.Warnf("%v: skip error - %v", u, err)
		respondWithError(w, err)
		return
	}

	jsonResponse(w, SkipPuzzleResponse{Success: true})
}

func GetFlag(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}

	var getFlagRequest GetFlagRequest
	err = json.NewDecoder(r.Body).Decode(&getFlagRequest)
	if err != nil {
		respondWithError(w, err)
		return
	}

	if getFlagRequest.Level < 0 || getFlagRequest.Level >= len(config.Config.Levels) {
		respondWithError(w, fmt.Errorf("invalid level"))
		return
	}

	complete, err := u.CheckLevelComplete(getFlagRequest.Level)
	if err != nil {
		respondWithError(w, err)
		return
	}

	successString := ""
	if complete {
		successString = utils.ColorString("success", utils.LIGHT_GREEN)
	} else {
		successString = utils.ColorString("failure", utils.RED)
	}

	log.Infof("%v: %s %s %s", u, utils.ColorString("flag request", utils.LIGHT_PINK), successString, utils.ColorString(fmt.Sprintf("level %d", getFlagRequest.Level+1), utils.HOT_PINK))

	if !complete {
		respondWithError(w, fmt.Errorf("solve more puzzles"))
		return
	}

	jsonResponse(w, GetFlagResponse{
		Flag: config.Config.Levels[getFlagRequest.Level].Flag,
	})
}

func GetPlayers(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}

	leaderboardResponse := LeaderboardUsersResponse{
		Users: make([]UserResponse, 0),
	}

	topUsers := puzzle.GetTop100()

	for _, user := range topUsers {
		name := ""
		if len(user.Name) <= 20 {
			name = user.Name
		} else {
			name = fmt.Sprintf("user: %d", user.UserID)
		}
		leaderboardResponse.Users = append(leaderboardResponse.Users, UserResponse{
			Name:       name,
			Level:      user.GetCurrentLevel(),
			AccountAge: user.GetAgeString(),
			Solves:     user.TotalSolves,
			Points:     user.Points,
			UserID:     user.UserID,
		})
	}

	log.Infof("%v: %s", u, utils.ColorString("requested the leaderboard", utils.BLUE))

	jsonResponse(w, leaderboardResponse)
}

func GetProfile(w http.ResponseWriter, r *http.Request) {
	u, err := checkAuth(r)
	if err != nil {
		w.WriteHeader(http.StatusUnauthorized)
		respondWithError(w, err)
		return
	}

	var getProfileRequest GetProfileRequest
	err = json.NewDecoder(r.Body).Decode(&getProfileRequest)
	if err != nil {
		respondWithError(w, err)
		return
	}

	foundUser, err := puzzle.GetUserByID(getProfileRequest.UserID)

	foundUserString := ""
	if err != nil {
		foundUserString = utils.ColorString("not found", utils.RED)
	} else {
		foundUserString = utils.ColorString("found", utils.LIGHT_GREEN)
	}

	log.Infof("%v: %s %s %s", u, utils.ColorString("searched for user", utils.VIOLET), utils.ColorString(fmt.Sprint(getProfileRequest.UserID), utils.LIGHT_PINK), foundUserString)

	if err != nil {
		respondWithError(w, err)
		return
	}

	userSolvedPuzzles := foundUser.GetSolvedPuzzles()
	solvesList := []SolveResponse{}

	for _, p := range userSolvedPuzzles {
		solvesList = append(solvesList, SolveResponse{
			Title:         p.Name,
			Artist:        p.PuzzleImg.Artist,
			URL:           p.PuzzleImg.URL,
			SolvedTime:    p.SolvedTime.Format("1/2/2006 3:04pm"),
			Tries:         p.Tries,
			Points:        p.GetStats().CalcPoints(),
			SolveDuration: utils.DurationHumanReadable(p.SolvedTime.Sub(p.StartTime)),
			Level:         p.Difficulty + 1,
		})
	}

	jsonResponse(w, GetProfileResponse{
		Name:       foundUser.Name,
		Points:     foundUser.Points,
		Level:      foundUser.GetCurrentLevel(),
		Ranking:    foundUser.GetRanking(),
		Solves:     foundUser.TotalSolves,
		AccountAge: foundUser.GetAgeString(),
		Puzzles:    solvesList,
	})
}
