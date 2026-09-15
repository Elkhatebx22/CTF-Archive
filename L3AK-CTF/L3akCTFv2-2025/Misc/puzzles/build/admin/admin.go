package admin

import (
	"context"
	"errors"
	"fmt"
	"puzzles/config"
	"puzzles/utils"
	"strings"
	"time"

	"github.com/go-rod/rod"
	"github.com/go-rod/rod/lib/launcher"
	"github.com/go-rod/rod/lib/proto"
	log "github.com/sirupsen/logrus"
)

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

func OpenBrowser(uid int, adminCookie string) {
	b, err := getBrowser()
	if err != nil {
		return
	}
	defer b.Close()
	BASE_URL := config.Config.General.ApplicationURL
	newPage := b.MustPage()
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(60*time.Second))
	defer cancel()
	page := newPage.Context(ctx)
	err = page.SetCookies([]*proto.NetworkCookieParam{{
		Name:   "session",
		Value:  adminCookie,
		Domain: strings.SplitAfter(BASE_URL, "://")[1],
		Path:   "/",
	}})
	if err != nil {
		log.Infof("%s: %s", utils.ColorString("browser error", utils.RED), utils.ColorString(fmt.Sprint(err), utils.ORANGE))
	}
	err = rod.Try(func() {
		page.MustNavigate(BASE_URL)
		time.Sleep(2 * time.Second)
		page.MustNavigate(BASE_URL + "/profile/" + fmt.Sprint(uid))
		time.Sleep(10 * time.Second)
		log.Infof("%s uid %s", utils.ColorString("finished browser for", utils.PURPLE), utils.ColorString(fmt.Sprint(uid), utils.HOT_PINK))
	})

	if errors.Is(err, context.DeadlineExceeded) {
		log.Info(utils.ColorString("browser timed out", utils.RED))
	} else if err != nil {
		log.Infof("%s: %s", utils.ColorString("browser error", utils.RED), utils.ColorString(fmt.Sprint(err), utils.ORANGE))
	}
}
