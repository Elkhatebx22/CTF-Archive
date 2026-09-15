package main

import (
	"github.com/jmoiron/sqlx"
	_ "github.com/mattn/go-sqlite3"
)

var db *sqlx.DB

const (
	CREATE_USERS_TABLE   = `CREATE TABLE users (user_id text UNIQUE, username text COLLATE NOCASE, password text, display_name text, description text NULL, user_type integer, cheater integer, PRIMARY KEY (username, display_name));`
	CREATE_GUESSES_TABLE = `CREATE TABLE guesses (guess_id text PRIMARY KEY, guesser_id text, flag_holder_id text, correct integer);`
	INSERT_USER          = `INSERT INTO users (user_id, username, password, display_name, description, user_type, cheater) VALUES (?, ?, ?, ?, ?, ?, 0);`
	INSERT_GUESS         = `INSERT INTO guesses (guess_id, guesser_id, flag_holder_id, correct) VALUES (?, ?, ?, 0);`
	FIND_USER            = `SELECT * FROM users WHERE user_id = ?;`
	LOGIN_USER           = `SELECT * FROM users WHERE username = ? AND password = ?;`
	UPDATE_DESCRIPTION   = `UPDATE users SET description = ? WHERE user_id = ?;`
	MARK_CHEATER         = `UPDATE users SET cheater = 1 WHERE user_id = ;`
	MARK_CORRECT         = `UPDATE guesses SET correct = 1 WHERE guess_id = ?;`
	GET_TOTAL_GUESSES    = `SELECT count(*) FROM guesses WHERE guesser_id = ?;`
	GET_CORRECT_GUESSES  = `SELECT count(*) FROM guesses WHERE guesser_id = ? AND correct = 1;`
	CHECK_FOUND_FLAG     = `SELECT count(*) FROM guesses WHERE guesser_id = ? AND flag_holder_id = ? AND correct = 1;`
	GET_USER_GUESSES     = `SELECT * FROM guesses WHERE guesser_id = ?;`
	FIND_GUESS           = `SELECT * FROM guesses WHERE guesser_id = ? AND guess_id = ?;`
)

func ConnectDB() error {
	var err error
	db, err = sqlx.Open("sqlite3", ":memory:")
	db.SetMaxOpenConns(1)
	if err != nil {
		return err
	}
	err = db.Ping()
	return err
}

func InitializeDB() {
	db.MustExec(CREATE_USERS_TABLE)
	db.MustExec(CREATE_GUESSES_TABLE)
}

func (u *User) CheckUsernameAvailable() (bool, error) {
	existing, err := GetUsers()
	if err != nil {
		return false, err
	}
	for _, e := range existing {
		if e.Username == u.Username {
			return false, nil
		}
	}
	return true, nil
}

func (u *User) CollectStats() error {
	var total, correct int
	err := db.Get(&total, GET_TOTAL_GUESSES, u.UserID)
	if err != nil {
		return err
	}
	err = db.Get(&correct, GET_CORRECT_GUESSES, u.UserID)
	if err != nil {
		return err
	}
	u.FlagsChecked = total
	u.FlagsFound = correct
	return nil
}

func (u *User) InsertUser() error {
	_, err := db.Exec(INSERT_USER, u.UserID, u.Username, u.Password, u.DisplayName, u.Description, u.UserType)
	return err
}

func GetUsers() ([]User, error) {
	users := []User{}
	err := db.Select(&users, "SELECT * FROM users;")
	if err != nil {
		return nil, err
	}
	userStats := []User{}
	for _, u := range users {
		u.CollectStats()
		userStats = append(userStats, u)
	}
	return userStats, nil
}

func FindUser(userID string) (*User, error) {
	var u User
	err := db.Get(&u, FIND_USER, userID)
	if err != nil {
		return nil, err
	}
	u.CollectStats()
	return &u, nil
}

func LoginUser(username, password string) (*User, error) {
	var u User
	err := db.Get(&u, LOGIN_USER, username, password)
	if err != nil {
		return nil, err
	}
	return &u, nil
}

func UpdateUserDescription(userID, desc string) error {
	_, err := db.Exec(UPDATE_DESCRIPTION, desc, userID)
	return err
}

func (g *Guess) InsertGuess() error {
	_, err := db.Exec(INSERT_GUESS, g.GuessID, g.GuesserID, g.FlagHolderID)
	return err
}

func (g *Guess) MarkCorrect() error {
	_, err := db.Exec(MARK_CORRECT, g.GuessID)
	return err
}

func (g *Guess) MarkCheater() {
	db.MustExec(MARK_CHEATER, g.GuesserID)
}

func (g *Guess) CheckFound() (bool, error) {
	var found int
	err := db.Get(&found, CHECK_FOUND_FLAG, g.GuesserID, g.FlagHolderID)
	if err != nil {
		return false, err
	}
	if found > 0 {
		return true, nil
	}
	return false, nil
}

func (u *User) CheckHasFlag(flagHolderID string) (bool, error) {
	var found int
	err := db.Get(&found, CHECK_FOUND_FLAG, u.UserID, flagHolderID)
	if err != nil {
		return false, err
	}
	if found > 0 {
		return true, nil
	}
	return false, nil
}

func (u *User) GetGuesses() ([]Guess, error) {
	guesses := []Guess{}
	err := db.Select(&guesses, GET_USER_GUESSES, u.UserID)
	if err != nil {
		return nil, err
	}
	return guesses, nil
}

func (u *User) FindGuess(guessID string) (*Guess, error) {
	var guess Guess
	err := db.Get(&guess, FIND_GUESS, u.UserID, guessID)
	if err != nil {
		return nil, err
	}
	return &guess, nil
}

func (u *User) CheckFound(userID string) (bool, error) {
	var found int
	err := db.Get(&found, CHECK_FOUND_FLAG, u.UserID, userID)
	if err != nil {
		return false, err
	}
	if found > 0 {
		return true, nil
	}
	return false, nil
}
