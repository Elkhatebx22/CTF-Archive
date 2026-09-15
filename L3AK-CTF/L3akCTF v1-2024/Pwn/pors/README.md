# pors

- **Target:** `nc 193.148.168.30 7668`

## Description
bazzed nc 193.148.168.30 7668 [pors_dist.zip](https://ctf.l3ak.team/files/77f08d7591695005805be6e76096d1ec/pors_dist.zip?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6Mzd9.ZlPMRA.XsKmG24IwC3-20bIx13xxEbSjBo)

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

> **Link:** [Official](https://github.com/L3AK-TEAM/L3akCTF-2024-public/tree/main/pwn/pors/solution)

```markdown
# pors


## tl;dr
- SROP to read our following payload on bss
- use `openat+sendfile` to bypass the sandbox
- happy flag
```