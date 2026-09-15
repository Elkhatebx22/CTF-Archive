# oorrww

- **Author:** Orrr
- **Target:** `nc 193.148.168.30 7666`

## Description
doubled with gifts Author: Orrr nc 193.148.168.30 7666 [oorrww_dist.zip](https://ctf.l3ak.team/files/c40dde0531d96aa1b891857f7ed40a0f/oorrww_dist.zip?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6Mzh9.ZlPL6g.Gs4oNKeiEyWO7SHSW9SWOyKUqDs)

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

> **Link:** [Official](https://github.com/L3AK-TEAM/L3akCTF-2024-public/tree/main/pwn/oorrww/solution)

```markdown
# oorrww


## tl;dr
- stack_addr and libc_addr leakage at the beginning
- write our orw on stack
- `-` bypass the canary check 
- stack pivot to where orw is located
- happy flag (data processing attention plz...
```