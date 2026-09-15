package main

import (
	"fmt"
	"image"
	"image/color"
	"image/png"
	"os"
	"os/exec"
	"strconv"

	"github.com/fogleman/gg"
)

type CertImage struct {
	TemplatePath string
	FontPath     string
	Username     string
	Description  string
	Attempts     int
	Correct      int
}

func (c *CertImage) DrawImage() (image.Image, error) {
	templateImg, err := gg.LoadImage(c.TemplatePath)
	if err != nil {
		return nil, err
	}
	width, height := templateImg.Bounds().Dx(), templateImg.Bounds().Dy()
	ctx := gg.NewContext(width, height)
	ctx.DrawImage(templateImg, 0, 0)

	err = ctx.LoadFontFace(c.FontPath, 25)
	if err != nil {
		return nil, err
	}
	ctx.SetColor(color.RGBA{R: 127, G: 127, B: 127, A: 255})
	ctx.DrawStringWrapped(c.Description, 512, 532, 0.5, 0.5, 800, 1.5, gg.AlignCenter)

	err = ctx.LoadFontFace(c.FontPath, 50)
	if err != nil {
		return nil, err
	}
	ctx.SetColor(color.RGBA{R: 95, G: 208, B: 167, A: 255})
	ctx.DrawStringWrapped(c.Username, 512, 460, 0.5, 0.5, 1000, 1.5, gg.AlignCenter)

	ctx.DrawString(fmt.Sprint(c.Attempts), 500, 850)
	ctx.DrawString(fmt.Sprint(c.Correct), 500, 910)
	if c.Attempts > 0 {
		ctx.DrawString(fmt.Sprintf("%.3f%%", float64(c.Correct)/float64(c.Attempts)*100), 500, 970)
	} else {
		ctx.DrawString("n/a", 500, 970)
	}
	return ctx.Image(), nil
}

func main() {
	if len(os.Args) < 2 {
		return
	}
	userID := os.Args[1]
	displayName := os.Getenv("display_name")
	description := os.Getenv("description")
	correctGuesses := os.Getenv("correct_guesses")
	attempts := os.Getenv("total_attempts")

	if displayName == "" {
		displayName = "Username Unknown"
	}
	if description == "" {
		description = "no description provided"
	}
	if correctGuesses == "" {
		correctGuesses = "0"
	}
	if attempts == "" {
		attempts = "0"
	}
	correctNum, err := strconv.Atoi(correctGuesses)
	if err != nil {
		return
	}
	attemptsNum, err := strconv.Atoi(attempts)
	if err != nil {
		return
	}
	c := CertImage{
		TemplatePath: "./templates/img/cert.png",
		FontPath:     "./templates/assets/ChakraPetch-Regular.ttf",
		Username:     displayName,
		Description:  description,
		Correct:      correctNum,
		Attempts:     attemptsNum,
	}

	img, err := c.DrawImage()
	if err != nil {
		return
	}

	output, err := os.CreateTemp("", "user-cert-*.png")
	if err != nil {
		return
	}
	defer os.Remove(output.Name())
	defer output.Close()

	err = png.Encode(output, img)
	if err != nil {
		return
	}
	cmd := exec.Command("cp", output.Name(), fmt.Sprintf("./userdata/%s/certificate.png", userID))
	err = cmd.Run()
	if err != nil {
		return
	}
}
