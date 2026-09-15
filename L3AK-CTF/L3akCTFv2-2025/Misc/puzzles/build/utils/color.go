package utils

import "fmt"

const (
	BLACK        = "\033[0;30m"
	RED          = "\033[38;5;52m"
	GREEN        = "\033[38;5;120m"
	BLUE         = "\033[38;5;117m"
	PURPLE       = "\033[38;5;57m"
	LIGHT_PURPLE = "\033[38;5;135m"
	CYAN         = "\033[0;36m"
	LIGHT_PINK   = "\033[38;5;219m"
	HOT_PINK     = "\033[38;5;198m"
	ORANGE       = "\033[38;5;208m"
	LIGHT_GREEN  = "\033[38;5;46m"
	LIGHT_RED    = "\033[38;5;196m"
	YELLOW       = "\033[38;5;227m"
	VIOLET       = "\033[38;5;99m"
	GREY         = "\033[38;5;238m"
	END          = "\033[0m"
)

func ColorString(str, color string) string {
	return fmt.Sprintf("%s%s%s", color, str, END)
}
