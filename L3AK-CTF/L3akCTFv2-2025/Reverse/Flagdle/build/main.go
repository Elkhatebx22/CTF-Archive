package main

import (
	"flagdle/flagdle"
	"fmt"
)

func main() {
	err := flagdle.ReadConfig()
	if err != nil {
		fmt.Println(err)
		return
	}
	wg, err := flagdle.NewGame()
	if err != nil {
		fmt.Println(err)
		return
	}
	err = wg.Play()
	if err != nil {
		fmt.Println(err)
		return
	}
}
