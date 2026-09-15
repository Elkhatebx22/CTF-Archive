package flagdle

import (
	"fmt"
)

const (
	BLACK          = "\033[0;30m"
	RED            = "\033[38;5;52m"
	GREEN          = "\033[38;5;120m"
	BLUE           = "\033[38;5;117m"
	PURPLE         = "\033[38;5;57m"
	LIGHT_PURPLE   = "\033[38;5;135m"
	CYAN           = "\033[0;36m"
	LIGHT_PINK     = "\033[38;5;219m"
	HOT_PINK       = "\033[38;5;198m"
	ORANGE         = "\033[38;5;208m"
	LIGHT_GREEN    = "\033[38;5;46m"
	LIGHT_RED      = "\033[38;5;196m"
	LIGHTER_RED    = "\033[38;5;197m"
	YELLOW         = "\033[38;5;227m"
	VIOLET         = "\033[38;5;99m"
	GREY           = "\033[38;5;238m"
	LIGHT_GREEN_BG = "\033[48;5;119m"
	GREY_BG        = "\033[48;5;242m"
	YELLOW_BG      = "\033[48;5;227m"
	END            = "\033[0m"
)

func ColorString(str, color string) string {
	return fmt.Sprintf("%s%s%s", color, str, END)
}

// func PKCS5UnPadding(origData []byte) []byte {
// 	length := len(origData)
// 	unpadding := int(origData[length-1])
// 	return origData[:(length - unpadding)]
// }

func stringIsASCII(s string) bool {
	for _, c := range s {
		if c > 127 || c < 32 {
			return false
		}
	}
	return true
}
