# coolVM

- **Author:** S4muii

## Description
Our Engineer Tried to save some space and combine the instructions into one . can you untangle them to reveal the secret phrase ? PS: Instructions are the same But the Op codes are different and the Order of execution is different. GL Author: S4muii [code](https://ctf.l3ak.team/files/eb819a9f28e66eeacd5da99c96e85fc2/code?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6MjF9.ZlPZ6g.YBnWN0Zcu8foh5_OC3Sf6-b_GmI) [coolVM](https://ctf.l3ak.team/files/2bfd61e96071ef6f3635d9329d31ea1e/coolVM?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6MjJ9.ZlPZ6g.i0EkhkpBfxX7I58jhqx_vySH4Zg)

---

## solver summary

### discovery

- **Tech Stack:**
    1. 
    2. 

- **Endpoints:**
    1. 
    2. 

- **Vulnerabilities:**
    1. 
    2. 

### PoC/Exploitation

1. 
2. 

### flag

- `CTF{...}`

## Official Solution / Writeup

> **Link:** [Official](https://github.com/L3AK-TEAM/L3akCTF-2024-public/tree/main/rev/coolVM/solution)

```markdown
# coolVM

## tl;dr
- The challenge is an implementation of a stack machine with 8 simple ops [psh,mul,div,jmp,cmp,add,sub,pop].
- The VM uses a bit mask to determine which function from the vtable to call.
- Instructions are variable-length . either 1 or 2 bytes to carry extra data with them some time like the `push` for example.
- The challenge allows the user to provide their own code to test which op codes does what for debugging purposes.

- Bear in mind though. The `code` provided uses a different order of instructions as defined in `main.h` Which means we can't just run `code` directly on this test VM.
- Since the VM uses a bit mask to determine the function from the vtable to call The `code` can get away with merging multiple instructions into one. There's a hint about that in the description 
    > Our Engineer Tried to save some space and combine the instructions into one.

- The intended solution relies on patching the VM
    + Bruteforcing the correct `vtable` which is not a big deal if you automate it possbily hell if you manually try that.
    + Disabling the check for multiple instructions 
        ```c
        if (++matched_inst>1)
            death();
        ```
    + Modifying the `read` SYSCALL len argument to pass in arbitiary-length ops to the `VM`.

## Flag
```
L3AK{7h3y_70ld_m3_574ck_m4ch1n35_4r3_u53l355!}
```
```