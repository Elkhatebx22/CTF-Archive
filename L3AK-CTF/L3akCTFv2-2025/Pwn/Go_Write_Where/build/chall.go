package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
	"unsafe"
)

func main() {
	reader := bufio.NewReader(os.Stdin)

	for i := 1; i > 0; i-- {
		fmt.Print("Read or Write? (r/w): ")
		mode, _ := reader.ReadString('\n')
		mode = strings.TrimSpace(mode)

		fmt.Print("Enter memory address (in hex, e.g., 0x12345678): ")
		addrStr, _ := reader.ReadString('\n')
		addrStr = strings.TrimSpace(addrStr)

		// Parse hex address string
		addr, err := strconv.ParseUint(strings.TrimPrefix(addrStr, "0x"), 16, 64)
		if err != nil {
			fmt.Println("Invalid address.")
			continue
		}
		ptr := unsafe.Pointer(uintptr(addr))

		if mode == "r" {
			// Read one byte from the address
			val := *(*byte)(ptr)
			fmt.Printf("Value at %s: 0x%02X\n", addrStr, val)
		} else if mode == "w" {
			fmt.Print("Enter byte to write (in hex, e.g., 0xAB): ")
			byteStr, _ := reader.ReadString('\n')
			byteStr = strings.TrimSpace(byteStr)

			value, err := strconv.ParseUint(strings.TrimPrefix(byteStr, "0x"), 16, 8)
			if err != nil {
				fmt.Println("Invalid byte.")
				continue
			}

			*(*byte)(ptr) = byte(value)
			fmt.Printf("Wrote 0x%02X to %s\n", value, addrStr)
		} else {
			fmt.Println("Invalid mode.")
		}
	}
}