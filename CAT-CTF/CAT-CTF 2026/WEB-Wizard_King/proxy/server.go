package main

import (
	"bytes"
	"fmt"
	"net"
	"os"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"
)

var (
	listenAddr = env("SERVICE_LISTEN_ADDR", ":8080")
	backend   = env("UPSTREAM_ADDR", "app:5000")
	backendMu sync.Mutex
	backendCn *bufferedConn
	clRe      = regexp.MustCompile(`(?im)^content-length:\s*(\d+)`)
	teRe      = regexp.MustCompile(`(?im)^transfer-encoding:\s*chunked`)
	ioTimeout = 5 * time.Second
)

type bufferedConn struct {
	conn net.Conn
	buf  []byte
}

func env(key, fallback string) string {
	value := os.Getenv(key)
	if value == "" {
		return fallback
	}
	return value
}

func (c *bufferedConn) readUntil(delim []byte) ([]byte, error) {
	for !bytes.Contains(c.buf, delim) {
		tmp := make([]byte, 4096)
		n, err := c.conn.Read(tmp)
		if err != nil {
			return nil, err
		}
		c.buf = append(c.buf, tmp[:n]...)
	}
	idx := bytes.Index(c.buf, delim) + len(delim)
	out := append([]byte(nil), c.buf[:idx]...)
	c.buf = c.buf[idx:]
	return out, nil
}

func (c *bufferedConn) readExact(size int) ([]byte, error) {
	for len(c.buf) < size {
		tmp := make([]byte, 4096)
		n, err := c.conn.Read(tmp)
		if err != nil {
			return nil, err
		}
		c.buf = append(c.buf, tmp[:n]...)
	}
	out := append([]byte(nil), c.buf[:size]...)
	c.buf = c.buf[size:]
	return out, nil
}

func contentLength(headers []byte) int {
	match := clRe.FindSubmatch(headers)
	if len(match) == 0 {
		return 0
	}
	value, _ := strconv.Atoi(string(match[1]))
	return value
}

func isChunked(headers []byte) bool {
	return teRe.Match(headers)
}

func getBackend() (*bufferedConn, error) {
	if backendCn != nil {
		_ = backendCn.conn.SetDeadline(time.Now().Add(ioTimeout))
		return backendCn, nil
	}
	raw, err := net.DialTimeout("tcp", backend, ioTimeout)
	if err != nil {
		return nil, err
	}
	_ = raw.SetDeadline(time.Now().Add(ioTimeout))
	backendCn = &bufferedConn{conn: raw}
	return backendCn, nil
}

func closeBackend() {
	if backendCn != nil {
		_ = backendCn.conn.Close()
		backendCn = nil
	}
}

func readResponse(conn *bufferedConn) ([]byte, error) {
	head, err := conn.readUntil([]byte("\r\n\r\n"))
	if err != nil {
		return nil, err
	}
	if isChunked(head) {
		body := []byte{}
		for {
			line, err := conn.readUntil([]byte("\r\n"))
			if err != nil {
				return nil, err
			}
			sizeText := strings.TrimSpace(strings.SplitN(string(line), ";", 2)[0])
			size, err := strconv.ParseInt(sizeText, 16, 64)
			if err != nil {
				return nil, err
			}
			if size == 0 {
				_, err = conn.readUntil([]byte("\r\n"))
				if err != nil {
					return nil, err
				}
				break
			}
			chunk, err := conn.readExact(int(size))
			if err != nil {
				return nil, err
			}
			body = append(body, chunk...)
			_, err = conn.readUntil([]byte("\r\n"))
			if err != nil {
				return nil, err
			}
		}
		head = teRe.ReplaceAll(head, nil)
		head = bytes.TrimSuffix(head, []byte("\r\n\r\n"))
		head = append(head, []byte(fmt.Sprintf("\r\nContent-Length: %d\r\n\r\n", len(body)))...)
		return append(head, body...), nil
	}
	cl := contentLength(head)
	body := []byte{}
	if cl > 0 {
		var err error
		body, err = conn.readExact(cl)
		if err != nil {
			return nil, err
		}
	}
	return append(head, body...), nil
}

func handle(client net.Conn) {
	defer client.Close()
	_ = client.SetDeadline(time.Now().Add(ioTimeout))

	buf := []byte{}
	for !bytes.Contains(buf, []byte("\r\n\r\n")) {
		tmp := make([]byte, 4096)
		n, err := client.Read(tmp)
		if err != nil {
			return
		}
		buf = append(buf, tmp[:n]...)
	}

	sep := bytes.Index(buf, []byte("\r\n\r\n")) + 4
	head := append([]byte(nil), buf[:sep]...)
	body := append([]byte(nil), buf[sep:]...)
	cl := contentLength(head)
	for len(body) < cl {
		tmp := make([]byte, 4096)
		n, err := client.Read(tmp)
		if err != nil {
			break
		}
		body = append(body, tmp[:n]...)
	}
	if len(body) > cl {
		body = body[:cl]
	}

	backendMu.Lock()
	defer backendMu.Unlock()

	resp, err := forward(head, body)
	if err != nil {
		closeBackend()
		resp, err = forward(head, body)
	}
	if err != nil {
		_, _ = client.Write([]byte("HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"))
		return
	}
	_, _ = client.Write(resp)
}

func forward(head, body []byte) ([]byte, error) {
	be, err := getBackend()
	if err != nil {
		return nil, err
	}
	_ = be.conn.SetDeadline(time.Now().Add(ioTimeout))
	_, err = be.conn.Write(append(append([]byte{}, head...), body...))
	if err != nil {
		return nil, err
	}
	return readResponse(be)
}

func main() {
	ln, err := net.Listen("tcp", listenAddr)
	if err != nil {
		panic(err)
	}
	fmt.Printf("server listening on %s\n", listenAddr)
	for {
		conn, err := ln.Accept()
		if err == nil {
			go handle(conn)
		}
	}
}
