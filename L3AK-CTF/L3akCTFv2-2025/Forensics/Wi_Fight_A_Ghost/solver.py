import socket
import time

# Same answers used by the server
answers = [
    "99phoenixdowns",
    "mugs_guest_5g",
    "2025-05-14 00:13:36",
    "192.168.0.114",
    "https://github.com/dbissell6/dfir/blob/main/blue_book/blue_book.md",
    "chromesetup.exe",
    "howtohacktheworld.txt",
    "practice and take good notes",
    "alleycat",
    "2025-05-14 00:35:07",
    "10.0.6.28",
    "99phoenixdowns.myrtle.solutions",
    "l3ak.team",
    "48:51:c5:35:ea:53",
    "fort collins"
]

HOST = 'localhost'
PORT = 1234

def recv_until(sock, end_marker=b': ', timeout=1.0):
    sock.settimeout(timeout)
    data = b""
    while not data.endswith(end_marker):
        try:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            break
    return data.decode()

def solve():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        for i in range(len(answers)):
            output = recv_until(s)
            print(output)

            # Send question number
            s.sendall(f"{i+1}\n".encode())
            print(f"[>] Answering Q{i+1}")

            # Wait for prompt
            recv_until(s)

            # Send answer
            s.sendall(f"{answers[i]}\n".encode())

            # Print feedback
            print(recv_until(s))

        # Final flag
        final_output = s.recv(2048).decode()
        print("\n🏁 Final Output:")
        print(final_output)

if __name__ == "__main__":
    solve()
 