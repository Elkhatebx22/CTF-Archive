package main

import (
	"bytes"
	"crypto/md5"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"slices"
	"strings"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
)

var jwtKey []byte

func (r *Response) respond() {
	if r.Responded {
		return
	}
	r.Writer.Header().Set("Content-Type", "application/json")
	if r.RespCode == 0 {
		r.RespCode = http.StatusOK
	}
	r.Writer.WriteHeader(r.RespCode)
	json.NewEncoder(r.Writer).Encode(r.Body)
	r.Responded = true
}

func (r *Response) respondRaw() error {
	if r.Responded {
		return nil
	}
	if r.RespCode == 0 {
		r.RespCode = http.StatusOK
	}
	r.Writer.WriteHeader(r.RespCode)
	respBytes, ok := r.Body.([]byte)
	if !ok {
		return fmt.Errorf("invalid body")
	}
	_, err := r.Writer.Write(respBytes)
	r.Responded = true
	return err
}

func (r *Response) respondRedirect() error {
	if r.Responded {
		return nil
	}
	if r.RespCode == 0 || r.RespCode == 200 {
		r.RespCode = http.StatusSeeOther
	}
	respUrl, ok := r.Body.(string)
	if !ok {
		return fmt.Errorf("invalid redirect url")
	}
	http.Redirect(r.Writer, r.Request, respUrl, r.RespCode)
	r.Responded = true
	return nil
}

func (r *Response) respondFile() error {
	if r.Responded {
		return nil
	}
	if r.RespCode == 0 {
		r.RespCode = http.StatusOK
	}
	respFileName, ok := r.Body.(string)
	if !ok {
		return fmt.Errorf("invalid file name")
	}
	http.ServeFile(r.Writer, r.Request, respFileName)
	r.Responded = true
	return nil
}

func (r *Response) setError(err error, code int) {
	r.Body = ErrorResponse{
		Error: err.Error(),
	}
	r.RespCode = code
}

func (s *Session) Sign() string {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, s)
	tokenStr, _ := token.SignedString(jwtKey)
	return tokenStr
}

func (s *Session) UpdateSession(w http.ResponseWriter) {
	token := s.Sign()
	cookie := http.Cookie{
		Name:     "session",
		Value:    token,
		HttpOnly: true,
		Path:     "/",
	}
	http.SetCookie(w, &cookie)
}

func (s *Session) UpdateProfile(desc string) {
	s.Properties["description"] = desc
}

func (s *Session) ClearSession() {
	*s = Session{}
}

func (s *Session) InitSession(u *User) {
	s.Username = u.Username
	s.UserKind = u.UserType
	s.UserID = u.UserID
	s.Properties = map[string]string{"display_name": u.DisplayName}
	if u.Description != "" {
		s.Properties["description"] = u.Description
	}
	s.LoggedIn = true
}

func (g *Guess) GetFilePath() string {
	return fmt.Sprintf("./userdata/%s/uploads/%s", g.GuesserID, g.GuessID)
}

func (g *Guess) CheckGuess() (bool, string, string) {
	flag, err := os.ReadFile(fmt.Sprintf("./userdata/%s/flag.txt", g.FlagHolderID))
	if err != nil {
		return false, "", ""
	}
	guess, err := os.ReadFile(g.GetFilePath())
	if err != nil {
		return false, "", ""
	}
	flagMd5 := md5.Sum(flag)
	guessMd5 := md5.Sum(guess)
	md5Equal := bytes.Equal(flagMd5[:], guessMd5[:])
	flagSha := sha256.Sum256(flag)
	guessSha := sha256.Sum256(guess)
	shaEqual := bytes.Equal(flagSha[:], guessSha[:])
	if md5Equal != shaEqual {
		g.MarkCheater()
	}
	return md5Equal && shaEqual, hex.EncodeToString(guessMd5[:]), hex.EncodeToString(guessSha[:])
}

func (u *User) LeaderboardUser() LeaderboardUser {
	return LeaderboardUser{
		Username:     u.Username,
		UserID:       u.UserID,
		FlagsChecked: u.FlagsChecked,
		FlagsFound:   u.FlagsFound,
	}
}

func RequestMiddleware(w http.ResponseWriter, r *http.Request) (*Session, bool, *Response, error) {
	sessionCookie, err := r.Cookie("session")
	resp := &Response{
		Body: MessageResponse{
			Message: "ok",
		},
		RespCode:  200,
		Writer:    w,
		Request:   r,
		Responded: false,
	}
	if err != nil {
		if err == http.ErrNoCookie {
			return &Session{}, false, resp, nil
		} else {
			resp.setError(err, http.StatusBadRequest)
			return nil, false, resp, err
		}
	}
	var session Session
	token, _ := jwt.ParseWithClaims(sessionCookie.Value, &session, func(t *jwt.Token) (any, error) { return jwtKey, nil })
	valid := false
	if token != nil {
		valid = token.Valid
	}
	return &session, valid, resp, nil
}

func Register(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	resp.Body = "/register"
	defer resp.respondRedirect()
	if err != nil {
		resp.Body = "/register?e=bad request"
		return
	}
	if valid && session.LoggedIn {
		resp.Body = "/home"
		return
	}
	defer session.UpdateSession(w)

	flagFile, _, err := r.FormFile("flag")
	if err != nil {
		session.ClearSession()
		resp.Body = "/register?e=bad request"
		return
	}
	username := r.FormValue("username")
	password := r.FormValue("password")
	displayName := r.FormValue("display_name")
	if len(username) == 0 {
		session.ClearSession()
		resp.Body = "/register?e=missing username"
		return
	} else if len(password) == 0 {
		session.ClearSession()
		resp.Body = "/register?e=missing password"
		return
	} else if len(displayName) == 0 {
		session.ClearSession()
		resp.Body = "/register?e=missing display name"
		return
	}
	newUser := &User{
		Username:    strings.ToLower(username),
		DisplayName: displayName,
		Password:    password,
		UserType:    UserKindStandard,
		UserID:      uuid.NewString(),
	}
	available, err := newUser.CheckUsernameAvailable()
	if err != nil {
		session.ClearSession()
		resp.Body = "/register?e=bad request"
		return
	}
	if !available {
		session.ClearSession()
		resp.Body = "/register?e=username taken"
		return
	}
	err = os.MkdirAll(fmt.Sprintf("./userdata/%s/uploads", newUser.UserID), 0644)
	if err != nil {
		session.ClearSession()
		resp.Body = "/register?e=internal server error"
		return
	}
	f, err := os.OpenFile(fmt.Sprintf("./userdata/%s/flag.txt", newUser.UserID), os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		session.ClearSession()
		resp.Body = "/register?e=internal server error"
		return
	}
	defer f.Close()
	_, err = io.Copy(f, flagFile)
	if err != nil {
		session.ClearSession()
		resp.Body = "/register?e=internal server error"
		return
	}
	err = newUser.InsertUser()
	if err != nil {
		resp.Body = "/register?e=bad request"
		return
	}
	session.InitSession(newUser)
	resp.Body = "/home"
}

func Login(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	resp.Body = "/login"
	defer resp.respondRedirect()
	if err != nil {
		resp.Body = "/login?e=bad request"
		return
	}
	if valid && session.LoggedIn {
		resp.Body = "/home"
		return
	}
	defer session.UpdateSession(w)

	username := r.FormValue("username")
	password := r.FormValue("password")

	if len(username) == 0 {
		session.ClearSession()
		resp.Body = "/login?e=missing username"
		return
	} else if len(password) == 0 {
		session.ClearSession()
		resp.Body = "/login?e=missing password"
		return
	}
	u, err := LoginUser(username, password)
	if err != nil {
		session.ClearSession()
		resp.Body = "/login?e=username or password is incorrect"
		return
	}
	session.InitSession(u)
	resp.Body = "/home"
}

func Logout(w http.ResponseWriter, r *http.Request) {
	session, _, resp, err := RequestMiddleware(w, r)
	resp.Body = "/login"
	defer resp.respondRedirect()
	if err != nil {
		return
	}
	defer session.UpdateSession(w)
	session.ClearSession()
}

func Profile(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	u, err := FindUser(session.UserID)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	resp.Body = ProfileResponse{
		Username:     u.Username,
		UserID:       u.UserID,
		DisplayName:  u.DisplayName,
		Description:  u.Description,
		UserKind:     u.UserType,
		FlagsChecked: u.FlagsChecked,
		FlagsFound:   u.FlagsFound,
	}
}

func GetUser(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	u, err := FindUser(session.UserID)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}

	otherUserID := r.PathValue("id")
	otherUser, err := FindUser(otherUserID)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}

	lbUser := otherUser.LeaderboardUser()
	userProfile := OtherUserProfile{LeaderboardUser: lbUser}

	found, err := u.CheckFound(otherUser.UserID)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	userProfile.FlagFound = found
	userProfile.IsSelf = u.UserID == otherUser.UserID
	resp.Body = userProfile
}

func SetProfile(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	if r.ContentLength == 0 {
		resp.setError(fmt.Errorf("missing body"), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()
	var req ProfileRequest
	err = json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	err = UpdateUserDescription(session.UserID, req.Description)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	session.UpdateProfile(req.Description)
	resp.Body = MessageResponse{Message: "success"}
}

func CheckFlag(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	if r.ContentLength == 0 {
		resp.setError(fmt.Errorf("missing body"), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	flagGuess := r.FormValue("flag")
	flagHolderID := r.PathValue("id")

	u, err := FindUser(flagHolderID)
	if err != nil {
		resp.setError(fmt.Errorf("user not found"), http.StatusBadRequest)
		return
	}
	if u.UserID == session.UserID {
		resp.setError(fmt.Errorf("you can't guess your own flag"), http.StatusBadRequest)
		return
	}

	guess := Guess{
		GuessID:      uuid.NewString(),
		GuesserID:    session.UserID,
		FlagHolderID: u.UserID,
		Correct:      false,
	}
	alreadyFound, err := guess.CheckFound()
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	if alreadyFound {
		resp.setError(fmt.Errorf("you already found that flag"), http.StatusBadRequest)
		return
	}
	err = guess.InsertGuess()
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}

	guessPath := guess.GetFilePath()
	err = os.WriteFile(guessPath, []byte(flagGuess), 0644)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	correct, md5, sha := guess.CheckGuess()
	if correct {
		guess.MarkCorrect()
	}
	if !correct {
		os.Remove(guessPath)
	} else {
		os.WriteFile(guessPath, []byte(fmt.Sprintf("MD5: %s\nSHA256: %s", md5, sha)), 0644)
	}
	resp.Body = FlagCheckResponse{Correct: correct}
}

func UserGuesses(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	guesserID := r.PathValue("id")
	guesser, err := FindUser(guesserID)
	if err != nil {
		resp.setError(fmt.Errorf("user not found"), http.StatusBadRequest)
		return
	}

	guesses, err := guesser.GetGuesses()
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	resp.Body = GuessesResponse{Guesses: guesses, DownloadEnabled: session.UserKind == UserKindAdmin || session.UserID == guesser.UserID}
}

func OwnGuesses(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	resp.Body = "/login"
	defer resp.respondRedirect()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		return
	}
	defer session.UpdateSession(w)
	resp.Body = fmt.Sprintf("/users/%s", session.UserID)
}

func GetGuess(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	guesserID := r.PathValue("guesser_id")
	guessID := r.PathValue("guess_id")
	guesser, err := FindUser(guesserID)
	if err != nil {
		resp.setError(fmt.Errorf("user not found"), http.StatusBadRequest)
		return
	}
	guess, err := guesser.FindGuess(guessID)
	if err != nil {
		resp.setError(fmt.Errorf("guess not found"), http.StatusBadRequest)
		return
	}
	if session.UserKind != UserKindAdmin && guess.GuesserID != session.UserID {
		resp.setError(fmt.Errorf("only admins can see other users' guesses"), http.StatusBadRequest)
		return
	}
	guessPath := guess.GetFilePath()
	guessBytes, err := os.ReadFile(guessPath)
	if err != nil {
		resp.setError(fmt.Errorf("incorrect guesses not saved"), http.StatusBadRequest)
		return
	}
	resp.Body = guessBytes
	resp.respondRaw()
}

func MakeCert(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	cmd := exec.Command("./makecert", session.UserID)
	u, err := FindUser(session.UserID)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	cmd.Env = append(os.Environ(), fmt.Sprintf("correct_guesses=%d", u.FlagsFound))
	cmd.Env = append(cmd.Env, fmt.Sprintf("total_attempts=%d", u.FlagsChecked))
	for k, v := range session.Properties {
		cmd.Env = append(cmd.Env, fmt.Sprintf("%s=%s", k, v))
	}
	err = cmd.Run()
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	imgData, err := os.ReadFile(fmt.Sprintf("./userdata/%s/certificate.png", session.UserID))
	if err != nil {
		resp.setError(fmt.Errorf("image generation failed"), http.StatusBadRequest)
		return
	}
	resp.Body = imgData
	resp.Writer.Header().Set("Content-Type", "image/png")
	resp.respondRaw()
}

func ReportCheater(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	if r.ContentLength == 0 {
		resp.setError(fmt.Errorf("missing body"), http.StatusBadRequest)
		return
	}
	defer r.Body.Close()
	var req ReportRequest
	err = json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}

	playerProfile := req.URL

	adminID := uuid.NewString()
	adminUsername := fmt.Sprintf("Admin-%s", adminID)
	adminPassword := uuid.NewString()
	adminDisplayName := uuid.NewString()
	adminUser := User{
		Username:    adminUsername,
		DisplayName: adminDisplayName,
		Password:    adminPassword,
		UserType:    UserKindAdmin,
		UserID:      adminID,
	}
	err = adminUser.InsertUser()
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	err = os.MkdirAll(fmt.Sprintf("./userdata/%s/uploads", adminID), 0644)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	f, err := os.OpenFile(fmt.Sprintf("./userdata/%s/flag.txt", adminID), os.O_WRONLY|os.O_CREATE, 0644)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	defer f.Close()

	src, err := os.Open("./flag.txt")
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	defer src.Close()

	_, err = io.Copy(f, src)
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}

	go adminCheckUser(adminUsername, adminPassword, playerProfile)

	resp.Body = MessageResponse{Message: "looking into it"}
}

func GetLeaderboard(w http.ResponseWriter, r *http.Request) {
	session, valid, resp, err := RequestMiddleware(w, r)
	defer resp.respond()
	if err != nil {
		return
	}
	if !valid || !session.LoggedIn {
		session.ClearSession()
		session.UpdateSession(w)
		resp.setError(fmt.Errorf("not logged in"), http.StatusUnauthorized)
		return
	}
	defer session.UpdateSession(w)

	users, err := GetUsers()
	if err != nil {
		resp.setError(err, http.StatusBadRequest)
		return
	}
	var leaderboardUsers []LeaderboardUser
	for _, u := range users {
		leaderboardUsers = append(leaderboardUsers, u.LeaderboardUser())
	}
	slices.SortStableFunc(leaderboardUsers, func(i, j LeaderboardUser) int {
		if j.FlagsFound != i.FlagsFound {
			return j.FlagsFound - i.FlagsFound
		} else if j.FlagsChecked != i.FlagsChecked {
			return i.FlagsChecked - j.FlagsChecked
		} else if i.UserID < j.UserID {
			return -1
		} else if i.UserID > j.UserID {
			return 1
		} else {
			return 0
		}
	})

	resp.Body = LeaderboardResponse{Users: leaderboardUsers}
}

func StaticFile(w http.ResponseWriter, r *http.Request, fileName string, authGate bool) {
	session, valid, resp, err := RequestMiddleware(w, r)
	resp.Body = "/login"
	defer resp.respondRedirect()
	if err != nil {
		return
	}
	if !valid {
		session.ClearSession()
		session.UpdateSession(w)
	}
	if authGate && !session.LoggedIn {
		return
	}
	defer session.UpdateSession(w)

	resp.Body = fileName
	resp.respondFile()
}

func initUsers() {
	os.RemoveAll("./userdata")
	for range 5 {
		userID := uuid.NewString()
		username := uuid.NewString()
		password := uuid.NewString()
		displayName := uuid.NewString()
		user := User{
			Username:    username,
			DisplayName: displayName,
			Password:    password,
			UserType:    UserKindStandard,
			UserID:      userID,
		}
		err := user.InsertUser()
		if err != nil {
			return
		}
		err = os.MkdirAll(fmt.Sprintf("./userdata/%s/uploads", userID), 0644)
		if err != nil {
			return
		}
		userFlag := fmt.Sprintf("flag{%s}", uuid.NewString())
		err = os.WriteFile(fmt.Sprintf("./userdata/%s/flag.txt", userID), []byte(userFlag), 0644)
		if err != nil {
			return
		}
	}
}

func main() {
	fmt.Println("started")
	err := ConnectDB()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("connected")
	InitializeDB()
	initUsers()
	fmt.Println("initialized")

	jwtKey = make([]byte, 256)
	rand.Read(jwtKey)

	mux := http.NewServeMux()
	mux.HandleFunc("POST /register", Register)
	mux.HandleFunc("POST /login", Login)
	mux.HandleFunc("POST /logout", Logout)
	mux.HandleFunc("GET /logout", Logout)
	mux.HandleFunc("GET /api/profile", Profile)
	mux.HandleFunc("POST /api/profile", SetProfile)
	mux.HandleFunc("POST /api/users/{id}/checkflag", CheckFlag)
	mux.HandleFunc("GET /api/users/{id}", GetUser)
	mux.HandleFunc("GET /api/users/{id}/guesses", UserGuesses)
	mux.HandleFunc("GET /api/users/{guesser_id}/guesses/{guess_id}", GetGuess)
	mux.HandleFunc("POST /api/report", ReportCheater)
	mux.HandleFunc("GET /api/certificate", MakeCert)
	mux.HandleFunc("GET /api/leaderboard", GetLeaderboard)
	mux.HandleFunc("GET /home", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/home.html", true) })
	mux.HandleFunc("GET /profile", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/profile.html", true) })
	mux.HandleFunc("GET /leaderboard", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/leaderboard.html", true) })
	mux.HandleFunc("GET /login", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/login.html", false) })
	mux.HandleFunc("GET /register", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/register.html", false) })
	mux.HandleFunc("GET /guesses", OwnGuesses)
	mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/users.html", false) })
	mux.HandleFunc("GET /css/styles.css", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/css/styles.css", false) })
	mux.HandleFunc("GET /img/logo.png", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/img/logo.png", false) })
	mux.HandleFunc("GET /img/favicon.ico", func(w http.ResponseWriter, r *http.Request) { StaticFile(w, r, "templates/img/favicon.ico", false) })
	mux.HandleFunc("GET /css/font.ttf", func(w http.ResponseWriter, r *http.Request) {
		StaticFile(w, r, "templates/assets/ChakraPetch-Regular.ttf", false)
	})
	mux.HandleFunc("GET /", func(w http.ResponseWriter, r *http.Request) { http.Redirect(w, r, "/home", http.StatusSeeOther) })
	log.Fatal(http.ListenAndServe("0.0.0.0:5555", mux))
}
