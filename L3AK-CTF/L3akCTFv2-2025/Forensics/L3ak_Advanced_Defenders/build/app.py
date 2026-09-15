import socket
import threading
import time

FLAG = "L3AK{@ct1v3_d1r3ct0ry_3num3r@t10n_1s_fun_sdf0sa90}" 

questions = [
    "1) What is the forest root domain name? Format: prefix.name.suffix",
    "2) What is the name of the primary domain controller for this domain?",
    "3) Which hosts have not been assigned to an OU? Format: host1, host2, ...",
    "4) List the oldest operating system used in the domain and the name of the workstation with this OS. Format: OS1, OS2, ...",
    "5) Based on their current operating system, which workstations are placed in the wrong OU? Format: host1, host2, ...",
    "6) Which hosts are no longer used by the organization? Format: host1, host2, ...",
    "7) Which users have their account disabled, and what is the value (in hex) of the attribute that dictates this? Format: displayName, 0x...",
    "8) Which enabled users have their password set to not expire, and what is the value (in hex) of the attribute that dictates this? Format: displayName, 0x...",
    "9) What departments exist inside this domain, and how many active employees exist in each department? List the departments in alphabetical order. Format: DepartmentName-NumberOfEmployees",
    "10) Which users have the most control over the structure of the AD forest? Format: user1, user2, ...",
    "11) Which users violate the principle of least privilege? Format: user1, user2, ...",
    "12) Which OUs block inheritance? Format: OU1, OU2, ...",
    "13) The GPOs were imported from a file supplied by a U.S. organization. Provide the sha256sum hash of the zip file containing the GPOs.",
    "14) What anti-virus software does the domain utilize, what is the maximum age in days of the AV definitions, and what must be impeded from launching executables? Format: answer1, answer2, ..."
]

# Placeholder answers — replace these with your real ones
answers = [
    "l3ak.ctf.com",
    "L3AKPRIDC",
    "FileSrv03, FileSrvWin11, InternStn",
    "Windows 95, InternStn",
    "ITWorkStn02, ITWorkStn03",
    "IT, ITTroubleshootStn, Linux, Repo",
    "Wilhelm Firtz, Reginald Norwood, Christopher Price, 0x202",
    "Bigsby Appleton, Montgomery Fitzgerald, Lily Sampson, 0x10200",
    "Finance-3, HR-8, IT-5",
    "Charlie Edgars, Lily Sampson",
    "Christopher Price, Eleanor Wharton",
    "Domain Controllers, IT, FileServers",
    "4BD7742C73A610EDF79A6B484457351438C90DC6FAC119EF8475B46D96BD2B37",
    "Microsoft Defender, 7, JavaScript, VBScript"
]

def normalize(s):
    return s.strip().lower()

def send(conn, msg):
    try:
        conn.sendall(msg.encode())
    except (BrokenPipeError, ConnectionResetError):
        conn.close()

def rate_limiter():
    timestamps = []

    def is_allowed():
        nonlocal timestamps
        now = time.time()
        timestamps = [t for t in timestamps if now - t < 60]
        if len(timestamps) < 15:
            timestamps.append(now)
            return True
        return False

    return is_allowed

def handle_client(conn):
    conn.settimeout(300)
    limiter = rate_limiter()

    send(conn, "Welcome to the Active Directory Challenge Terminal.\nAnswer each question correctly to reveal the final flag.\nSubmit all answers in alphabetical order.\nFor answers with names, please submit alphabetically by last name.\nType 'exit' at any time to quit.\n\n")

    q_index = 0
    while q_index < len(questions):
        if not limiter():
            send(conn, "\nYou're going too fast. Please wait a moment.\n")
            time.sleep(2)
            continue

        try:
            send(conn, f"\nQuestion {q_index + 1}:\n{questions[q_index]}\nYour answer: ")
            user_input = conn.recv(2048).decode().strip()
            if not user_input or user_input.lower() == 'exit':
                send(conn, "\nGoodbye!\n")
                break

            if normalize(user_input) == normalize(answers[q_index]):
                send(conn, "\nCorrect!\n")
                q_index += 1
            else:
                send(conn, "\nIncorrect, try again.\n")

        except (ValueError, socket.timeout, ConnectionResetError, BrokenPipeError):
            break

    if q_index == len(questions):
        send(conn, f"\nAll questions answered correctly! Here is your final flag:\n{FLAG}\n")
    conn.close()

def main():
    HOST = '0.0.0.0'
    PORT = 5982
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on port {PORT}...")
        while True:
            conn, addr = s.accept()
            print(f"Connection from {addr}")
            thread = threading.Thread(target=handle_client, args=(conn,))
            thread.start()

if __name__ == "__main__":
    main()
                