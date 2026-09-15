package utils

import (
	"crypto/rand"
	"encoding/base64"
	"fmt"
	"puzzles/config"
	"strings"
	"unicode"
)

func isASCII(s string) bool {
	for i := range len(s) {
		if s[i] > unicode.MaxASCII {
			return false
		}
	}
	return true
}

func generateRandomBytes(n int) ([]byte, error) {
	b := make([]byte, n)
	_, err := rand.Read(b)

	if err != nil {
		return nil, err
	}

	return b, nil
}

func MakeRandomString(n int) (string, error) {
	b, err := generateRandomBytes(n)
	return base64.URLEncoding.EncodeToString(b), err
}

func MakeRandomUID() ([]byte, error) {
	b, err := generateRandomBytes(12)
	return b, err
}

func ValidateUsername(s string) (string, bool, error) {
	asUpper := strings.ToUpper(s)
	for _, c := range config.Config.General.UsernameBlacklist {
		if strings.Contains(asUpper, c) {
			return "", false, fmt.Errorf("%s", fmt.Sprintf("%s banned", c))
		}
	}
	if len(s) > config.Config.General.MaxUsernameChars || len(s) < config.Config.General.MinUsernameChars {
		return "", false, fmt.Errorf("%s", fmt.Sprintf("bad length %d", len(s)))
	}

	s = strings.ReplaceAll(s, "«", "<") // no XSS until getting the source plz
	s = strings.ReplaceAll(s, "»", ">")

	if !isASCII(s) {
		return "", false, fmt.Errorf("not ascii")
	}

	return s, true, nil
}
