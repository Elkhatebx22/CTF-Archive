package puzzle

import (
	"bytes"
	"encoding/base64"
	"fmt"
	"image"
	"image/color"
	"image/draw"
	"image/png"
	"math/rand"
	"puzzles/config"
)

func RandomPastelColor() color.RGBA {
	r := uint8(rand.Intn(128) + 127)
	g := uint8(rand.Intn(128) + 127)
	b := uint8(rand.Intn(128) + 127)

	return color.RGBA{R: r, G: g, B: b, A: 255}
}

func SplitImage(img image.Image, cols, rows int) ([]*config.Chunk, int, int, error) {

	originalBounds := img.Bounds()
	originalWidth, originalHeight := originalBounds.Dx(), originalBounds.Dy()

	borderWidth := config.Config.General.BorderWidth

	newWidth := ((originalWidth+borderWidth*2)/cols)*cols - borderWidth*2
	newHeight := ((originalHeight+borderWidth*2)/rows)*rows - borderWidth*2

	if newWidth == 0 || newHeight == 0 {
		return nil, 0, 0, fmt.Errorf("image is too small to be cropped to multiples of %d width and %d height", cols, rows)
	}

	cropRect := image.Rect(originalBounds.Min.X, originalBounds.Min.Y, originalBounds.Min.X+newWidth, originalBounds.Min.Y+newHeight)

	croppedImg := img.(interface {
		SubImage(r image.Rectangle) image.Image
	}).SubImage(cropRect)

	newBorderedWidth := newWidth + 2*borderWidth
	newBorderedHeight := newHeight + 2*borderWidth

	newImg := image.NewRGBA(image.Rect(0, 0, newBorderedWidth, newBorderedHeight))

	draw.Draw(newImg, newImg.Bounds(), &image.Uniform{RandomPastelColor()}, image.Point{}, draw.Src)

	draw.Draw(newImg, image.Rect(borderWidth, borderWidth, borderWidth+newWidth, borderWidth+newHeight), croppedImg, image.Point{X: 0, Y: 0}, draw.Over)

	img = newImg

	bounds := img.Bounds()
	width, height := bounds.Dx(), bounds.Dy()
	tileWidth := width / cols
	tileHeight := height / rows

	var pngChunks []*config.Chunk

	for y := 0; y < rows; y++ {
		for x := 0; x < cols; x++ {
			subImgBounds := image.Rect(
				x*tileWidth, y*tileHeight,
				(x+1)*tileWidth, (y+1)*tileHeight,
			)
			var subImg image.Image
			switch img := img.(type) {
			case *image.RGBA:
				subImg = img.SubImage(subImgBounds).(*image.RGBA)
			case *image.Paletted:
				subImg = img.SubImage(subImgBounds).(*image.Paletted)
			default:
				subImg = img.(*image.NRGBA).SubImage(subImgBounds).(*image.NRGBA)
			}
			buf := new(bytes.Buffer)
			if err := png.Encode(buf, subImg); err != nil {
				return nil, 0, 0, err
			}
			pngChunks = append(pngChunks, &config.Chunk{Data: base64.StdEncoding.EncodeToString(buf.Bytes()), Index: (cols * y) + x})
		}
	}
	return pngChunks, tileWidth, tileHeight, nil
}
