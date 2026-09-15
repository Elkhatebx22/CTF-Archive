package main

import (
	"net/http"

	"github.com/golang-jwt/jwt/v5"
)

type UserKind int

const (
	UserKindStandard UserKind = iota
	UserKindAdmin
)

type User struct {
	UserID       string   `db:"user_id"`
	Username     string   `db:"username"`
	Password     string   `db:"password"`
	DisplayName  string   `db:"display_name"`
	Description  string   `db:"description"`
	UserType     UserKind `db:"user_type"`
	Cheater      int      `db:"cheater"`
	FlagsChecked int      `db:"flags_checked"`
	FlagsFound   int      `db:"flags_found"`
}

type Session struct {
	UserID     string            `json:"user_id"`
	Username   string            `json:"username"`
	UserKind   UserKind          `json:"user_kind"`
	Properties map[string]string `json:"properties"`
	LoggedIn   bool              `json:"logged_in"`
	jwt.RegisteredClaims
}

type Guess struct {
	GuessID      string `db:"guess_id" json:"guess_id"`
	GuesserID    string `db:"guesser_id" json:"guesser_id"`
	FlagHolderID string `db:"flag_holder_id" json:"flag_holder_id"`
	Correct      bool   `db:"correct" json:"correct"`
}

type Response struct {
	Body      any
	RespCode  int
	Writer    http.ResponseWriter
	Request   *http.Request
	Responded bool
}

type ErrorResponse struct {
	Error string `json:"error"`
}

type MessageResponse struct {
	Message string `json:"message"`
}

type ProfileResponse struct {
	Username     string   `json:"username"`
	UserID       string   `json:"user_id"`
	DisplayName  string   `json:"display_name"`
	Description  string   `json:"description,omitempty"`
	UserKind     UserKind `json:"user_kind"`
	FlagsChecked int      `json:"flags_checked"`
	FlagsFound   int      `json:"flags_found"`
}

type ProfileRequest struct {
	Description string `json:"description"`
}

type FlagCheckRequest struct {
	User string `json:"user"`
	Flag string `json:"flag"`
}

type FlagCheckResponse struct {
	Correct bool `json:"correct"`
}

type GuessesResponse struct {
	Guesses         []Guess `json:"guesses"`
	DownloadEnabled bool    `json:"download_enabled"`
}

type ReportRequest struct {
	URL string `json:"url"`
}

type LeaderboardUser struct {
	Username     string `json:"username"`
	UserID       string `json:"user_id"`
	FlagsChecked int    `json:"flags_checked"`
	FlagsFound   int    `json:"flags_found"`
}

type LeaderboardResponse struct {
	Users []LeaderboardUser `json:"users"`
}

type OtherUserProfile struct {
	FlagFound bool `json:"flag_found"`
	IsSelf    bool `json:"is_self"`
	LeaderboardUser
}
