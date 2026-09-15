import os
import subprocess
import socket

def run_custom_server():
    port = int(os.getenv("APP_PORT", "12345"))
    print(f"Server is listening on tcp://localhost:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connection from {addr}")
                with open("input.txt", "w") as f:
                    while True:
                        data = conn.recv(4096)
                        if not data:
                            break
                        text = data.decode(errors="ignore")
                        if "EOF" in text:
                            f.write(text.split("EOF")[0])
                            break
                        f.write(text)
                result = subprocess.run(
                    ["./final"],
                    stdin=open("input.txt", "rb"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                conn.sendall(result.stdout + result.stderr)

if __name__ == "__main__":
    run_custom_server()
