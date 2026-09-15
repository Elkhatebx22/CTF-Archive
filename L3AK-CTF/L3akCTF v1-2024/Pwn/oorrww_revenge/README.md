# oorrww revenge

- **Author:** Orrr
- **Target:** `nc 193.148.168.30 7667`

## Description
gifts disappeared Author: Orrr nc 193.148.168.30 7667 [oorrww_revenge.zip](https://ctf.l3ak.team/files/359bb5cab4bf763f1a3831c18d071c70/oorrww_revenge.zip?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6Mzl9.ZlPMGg.oVyX9RIT3eMjbmEi0F6iXrAXZMQ)

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

> **Link:** [Official](https://github.com/L3AK-TEAM/L3akCTF-2024-public/tree/main/pwn/oorrww_revenge/solution)

```markdown
# oorrww_revenge


## tl;dr
- `pop rax; ret;` and `mov rdi, rax;` in `gifts()` to leak libc_addr
- `-` bypass canary check
- write orw chain on bss and stack pivot to there
- happy flag (don't forget the data processing :)
```