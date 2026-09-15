package main

import (
	"net/http"
	"puzzles/api"
	"puzzles/config"
	"puzzles/puzzle"

	"github.com/sirupsen/logrus"
	log "github.com/sirupsen/logrus"
)

func main() {
	config.ReadConfig()

	log.SetFormatter(&logrus.TextFormatter{
		ForceColors: true,
	})

	log.Infof("loaded configuration")

	puzzle.InitPuzzles()
	puzzle.InitUsers()
	puzzle.MakeAdminAccount()
	http.HandleFunc("/api/newpuzzle", api.NewPuzzle)
	http.HandleFunc("/api/checkanswer", api.CheckAnswer)
	http.HandleFunc("/api/getsolves", api.GetSolves)
	http.HandleFunc("/api/getflag", api.GetFlag)
	http.HandleFunc("/api/setname", api.SetName)
	http.HandleFunc("/api/skippuzzle", api.SkipPuzzle)
	http.HandleFunc("/api/getplayers", api.GetPlayers)
	http.HandleFunc("/api/profile", api.GetProfile)
	http.HandleFunc("/css/styles.css", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "templates/css/styles.css")
	})
	http.HandleFunc("/js/font.js", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "templates/js/font.js")
	})
	http.HandleFunc("/css/font.woff2", func(w http.ResponseWriter, r *http.Request) {
		http.ServeFile(w, r, "templates/css/font.woff2")
	})
	http.HandleFunc("/downloads/puzzles.zip", api.ChallengeHandout)
	http.HandleFunc("/puzzle", api.Puzzle)
	http.HandleFunc("/leaderboard", api.Leaderboard)
	http.HandleFunc("/help", api.Help)
	http.HandleFunc("/profile/", api.Profile)

	http.HandleFunc("/", api.Home)
	log.Print("Starting server...")
	log.Fatal(http.ListenAndServe(config.Config.General.BindAddress, nil))
}
