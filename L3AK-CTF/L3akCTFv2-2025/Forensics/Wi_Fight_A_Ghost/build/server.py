import sys
import time
from secret import FLAG

questions = [
    "1. What was the ComputerName of the device?",
    "2. What was the SSID of the first Wi-Fi network they connected to?",
    "3. When did they obtain the DHCP lease at the first café?",
    "4. What IP address was assigned at the first café?",
    "5. What GitHub page did they visit at the first café?",
    "6. What did they download at the first café?",
    "7. What was the name of the notes file?",
    "8. What are the contents of the notes?",
    "9. What was the SSID of the second Wi-Fi network they connected to?",
    "10. When did they obtain the second lease?",
    "11. What was the IP address assigned at the second café?",
    "12. What website did they log into at the second café?",
    "13. What was the MAC address of the Wi-Fi adapter used?",
    "14. What city did this take place in?"
]

answers = [
    "99phoenixdowns",
    "mugs_guest_5g",
    "2025-05-14 00:13:36",
    "192.168.0.114",
    "https://github.com/dbissell6/dfir/blob/main/blue_book/blue_book.md",
    "chromesetup.exe",
    "howtohacktheworld.txt",
    "practice and take good notes.",
    "alleycat",
    "2025-05-14 00:35:07",
    "10.0.6.28",
    "l3ak.team",
    "48:51:c5:35:ea:53",
    "fort collins"
]

def normalize(s):
    return s.strip().lower()

def send_msg(msg):
    print(msg, end='', flush=True)

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

def handle_client():
    limiter = rate_limiter()
    answered = [False] * len(questions)
    
    send_msg("Welcome to the Ghost Hunt Terminal. Answer all questions to reveal the final flag.\nType 'exit' at any prompt to quit.\n\n")
    
    while not all(answered):
        if not limiter():
            send_msg("\n⚠ You're going too fast. Please wait a moment.\n")
            time.sleep(2)
            continue
        
        try:
            # Show unanswered
            send_msg("\nUnanswered Questions:\n")
            for i, (q, a) in enumerate(zip(questions, answered)):
                if not a:
                    send_msg(f"  {q}\n")
            
            # Show answered
            send_msg("\nAnswered so far:\n")
            for i, (q, a) in enumerate(zip(questions, answered)):
                if a:
                    send_msg(f"  ✅ {i+1}. {questions[i]} → {answers[i]}\n")
            
            send_msg("\nEnter question number to answer: ")
            qnum = input().strip()
            if not qnum or qnum.lower() == 'exit':
                send_msg("Goodbye!\n")
                break
            
            q_index = int(qnum) - 1
            if not (0 <= q_index < len(questions)):
                send_msg("Invalid question number.\n")
                continue
            if answered[q_index]:
                send_msg("That question is already answered.\n")
                continue
            
            send_msg("Enter your answer: ")
            user_answer = input().strip()
            if not user_answer or user_answer.lower() == 'exit':
                send_msg("Goodbye!\n")
                break
            
            if normalize(user_answer) == normalize(answers[q_index]):
                answered[q_index] = True
                send_msg("\n✔ Correct!\n")
            else:
                send_msg("\n✖ Incorrect, try again.\n")
        
        except (ValueError, EOFError, KeyboardInterrupt):
            break
    
    if all(answered):
        send_msg(f"\n🎉 All questions answered! Final flag:\n{FLAG}\n")

def main():
    handle_client()

if __name__ == "__main__":
    main()
