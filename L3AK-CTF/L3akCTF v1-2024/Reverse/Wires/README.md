# Wires

- **Author:** 0xnil

## Description
Why just fdf when you can do more ? Author: 0xnil [wires](https://ctf.l3ak.team/files/811979eadd00cd11a36a63d417606cd5/wires?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6MTd9.ZlPYfg.tNVTyLkgkICOC_5gO38QxfUtUdA)

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

> **Link:** [Official](https://github.com/L3AK-TEAM/L3akCTF-2024-public/tree/main/rev/wires/solution)

```markdown
# Wires

## tl;dr
- Find the weird strings that start with ff in the binary (with `strings`)
- Understand that it's the flag compressed
- Understand the compression which is working as `"ff" + number of bytes + "ff" + byte compressed`

## Flag :
```
L3AK{42_1s_th3_answer}
```
```