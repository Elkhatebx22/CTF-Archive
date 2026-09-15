package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"net/http/cookiejar"
	"os"
	"os/exec"
	"slices"
	"strings"
	"sync"
	"time"
)

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

func invertFisherYates(shuffled []int) []int {
	n := len(shuffled)
	inverted := make([]int, n)
	for i := n - 1; i >= 0; i-- {
		swapPos := slices.Index(shuffled, i)
		inverted[i] = swapPos
		shuffled[i], shuffled[swapPos] = shuffled[swapPos], shuffled[i]
	}
	return inverted
}

func inversePermuteSlice(s []int) []int {
	inverted := make([]int, len(s))
	for i, val := range s {
		inverted[val] = i
	}
	return inverted
}

func searchForSeed(ctx context.Context, wg *sync.WaitGroup, found chan int, workerID, numWorkers int, target []int) {
	defer wg.Done()
	seed := int64(workerID)
	r := rand.New(rand.NewSource(seed))
	for {
		select {
		case <-ctx.Done():
			return
		default:
			broken := false
			for range 32 {
				r.Intn(2)
			}
			for i := range len(target) {
				if r.Intn(i+1) != target[i] {
					broken = true
					break
				}
			}
			if !broken {
				select {
				case found <- int(seed):
					return
				case <-ctx.Done():
					return
				}
			}
			seed += int64(numWorkers)
			r.Seed(seed)
			if seed%1000000 < int64(numWorkers) {
				fmt.Printf("\rsearching: [%s%s] (%d/%d)", strings.Repeat("#", int(seed/(1<<25))), strings.Repeat(" ", 64-int(seed/(1<<25))), seed, (1<<31)-1)
			}
			if seed >= ((1 << 31) - 1) {
				return
			}
		}
	}
}

func generateSolution(length int, RNG *rand.Rand) []int {
	order := []int{}
	for i := range length {
		order = append(order, i)
	}
	for i := range length {
		j := RNG.Intn(i + 1)
		order[i], order[j] = order[j], order[i]
	}
	return inversePermuteSlice(order)
}

func main() {

	const (
		ENDPOINT = "http://localhost:1353"
	)
	USERNAME := "meowmeow" + fmt.Sprint(rand.Intn(99999))
	jar, _ := cookiejar.New(nil)
	client := &http.Client{Jar: jar}

	createResp, _ := client.Get(ENDPOINT)
	fmt.Printf("created account, cookie is %v", jar.Cookies(createResp.Request.URL))
	jsonData, _ := json.Marshal(map[string]string{"name": USERNAME})
	client.Post(ENDPOINT+"/api/setname", "application/json", bytes.NewReader(jsonData))
	fmt.Printf("set name to %s\n", USERNAME)
	firstPuzzleResp, err := client.Get(ENDPOINT + "/api/newpuzzle")
	if err != nil || firstPuzzleResp.StatusCode != 200 {
		panic(err)
	}

	f, _ := os.Create("puzzledata.json")
	defer f.Close()
	tee := io.TeeReader(firstPuzzleResp.Body, f)

	var puzzleData PuzzleResponse
	json.NewDecoder(tee).Decode(&puzzleData)
	fmt.Printf("fetched puzzle %s, spawning python solver\n", puzzleData.PuzzleID)

	out, err := exec.Command("python3", "level5.py").Output()
	if err != nil {
		panic(err)
	}

	var solution []int
	if err := json.Unmarshal([]byte(out), &solution); err != nil {
		panic(err)
	}
	time.Sleep(350 * time.Millisecond)
	jsonData, _ = json.Marshal(map[string]any{"puzzle_id": puzzleData.PuzzleID, "answer": solution})
	checkAnswerResp, _ := client.Post(ENDPOINT+"/api/checkanswer", "application/json", bytes.NewReader(jsonData))

	if checkAnswerResp.StatusCode != 200 {
		panic("nope")
	}

	fmt.Printf("got solution: %v\n", solution)
	originalOrder := inversePermuteSlice(solution)
	fmt.Printf("inverted: %v\n", originalOrder)
	target := invertFisherYates(originalOrder)
	fmt.Printf("reconstructed random values: %v\n", target)

	fmt.Println("searching for seed:")

	const (
		numWorkers = 16
	)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	found := make(chan int)

	var wg sync.WaitGroup

	for i := range numWorkers {
		wg.Add(1)
		go searchForSeed(ctx, &wg, found, i, numWorkers, target)
	}

	seed := <-found

	cancel()

	wg.Wait()
	fmt.Println()
	fmt.Printf("Found seed: %d\n", seed)

	RNG := rand.New(rand.NewSource(int64(seed)))

	for range 16 + 32 + 1 {
		RNG.Intn(2)
	}

	for i := range 9 + 10 + 10 + 1 + 1 {
		puzzleResp, err := client.Get(ENDPOINT + "/api/newpuzzle")
		if err != nil {
			panic(err)
		}
		var puzzleData PuzzleResponse
		json.NewDecoder(puzzleResp.Body).Decode(&puzzleData)
		puzzleSize := puzzleData.Rows * puzzleData.Cols
		solution := generateSolution(puzzleSize, RNG)
		RNG.Intn(2)
		time.Sleep(350 * time.Millisecond)
		jsonData, _ = json.Marshal(map[string]any{"puzzle_id": puzzleData.PuzzleID, "answer": solution})
		checkAnswerResp, _ := client.Post(ENDPOINT+"/api/checkanswer", "application/json", bytes.NewReader(jsonData))
		if checkAnswerResp.StatusCode != 200 {
			panic("nope")
		}
		if i == 30 {
			m, _ := json.Marshal(solution)
			os.WriteFile("level5_order.json", []byte(m), 0644)
			m, _ = json.Marshal(puzzleData.Pieces)
			os.WriteFile("level5_data.json", []byte(m), 0644)
		}
		time.Sleep(350 * time.Millisecond)
	}

}
