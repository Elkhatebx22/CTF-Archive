# CC

- **Tags:** `crypto`
- **Author:** 0xnil

## Description
C stands for Crab or Crypto ? Author: 0xnil [CC](https://ctf.l3ak.team/files/3486b7d46e77ca0eeed07f5c7758c700/CC?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6MTl9.ZlPXgQ.EUnmO8qd8_9I2NtJOjwchTuZ-pU) [flag.bin](https://ctf.l3ak.team/files/29e7f2bc3ec7c90d73fc65cf8495aa88/flag.bin?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6MjB9.ZlPXgQ.HiFH3-HYDXnRw19SLjyyKgDtOOQ)

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

> **Link:** [Official](https://github.com/L3AK-TEAM/L3akCTF-2024-public/tree/main/rev/CC/solution)

```markdown
# CC

## tl;dr
- The binary is an implementation of Feisel network in rust, the key is given in plaintext. You can either recreate the network in Python, and swap the keys (The decryption is almost like the encrytion)
- Or you can patch the binary to use the decrypt function

## Flag :
```
L3AK{its_all_started_with_C}
```
```