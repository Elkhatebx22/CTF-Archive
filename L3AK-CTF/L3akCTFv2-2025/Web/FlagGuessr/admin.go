package main

import (
	"context"
	"fmt"
	"time"

	"github.com/go-rod/rod"
	"github.com/go-rod/rod/lib/launcher"
)

const baseURL = "http://127.0.0.1:5555"

func getBrowser() (*rod.Browser, error) {
	var b *rod.Browser

	path, _ := launcher.LookPath()
	l := launcher.New().Bin(path).Headless(true)
	u := l.MustLaunch()
	b = rod.New().ControlURL(u)

	err := b.Connect()
	if err != nil {
		return nil, fmt.Errorf("failed to connect to browser: %s", err)
	}
	err = b.IgnoreCertErrors(true)
	if err != nil {
		return nil, fmt.Errorf("failed to ignore cert errors: %s", err)
	}
	return b, nil
}

func adminCheckUser(adminUser, adminPass, url string) error {
	b, err := getBrowser()
	if err != nil {
		return err
	}
	defer b.Close()
	newPage := b.MustPage()
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(30*time.Second))
	defer cancel()
	page := newPage.Context(ctx)
	err = rod.Try(func() {
		page.MustNavigate(baseURL + "/login")
		userBox := page.MustElement("input[name=username]")
		passBox := page.MustElement("input[name=password]")
		submitButton := page.MustElement("input[type=submit]")
		userBox.MustInput(adminUser)
		passBox.MustInput(adminPass)
		submitButton.MustClick()
		time.Sleep(2 * time.Second)
		page.MustNavigate(baseURL + url)
		time.Sleep(10 * time.Second)
	})

	return err
}
