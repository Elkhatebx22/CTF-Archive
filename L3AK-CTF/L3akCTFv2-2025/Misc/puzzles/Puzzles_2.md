# Puzzles - 2

That first one was pretty easy, this level might take you a bit longer unless you're clever about it

## Flag

L3AK{2_i_5ur3_hop3_u_d1dn7_d0_th4t_by_h4nd}

# Puzzles - 2

- **Author:** sy1vi3
- **Category:** Misc
- **Solves:** 70
- **Connection:** `http://34.55.69.223:14001`

## Description

That first one was pretty easy, this level might take you a bit longer unless you're clever about it Author: sy1vi3 <http://34.55.69.223:14001>

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

> **Link:** [Official](https://github.com/L3AK-TEAM/L3akCTF-2025-public/tree/main/misc/puzzles/solution)

```markdown
## Solution

### Flag 1

Solve the puzzles, shouldnt take more than 10 minutes to do by hand

### Flag 2

*Either* solve them by hand (will take at least an hour or two), or find the source images and use them to match with pixels in
the chunks to find the right order

### Flag 3

Same as flag 2, but too big for doing it by hand to be a reasonable option, requiring automation

### Code Download

The image used isn't on the internet so you can't match pixels. instead, match edges by best fit using whatever search method you choose

### Flag 4

There's an XSS on the user display page. The session cookie is httponly, but since it's same-site you can make an API request to fetch the flag directly instead of exfiltrating the session token

### Flag 5

The 5th flag is embedded in the 5th image, getting the level 5 reward isn't enough to actually get the image. There's an unsecure random number generation bug in
the code, golang's default random number generator only uses the lower 32 bits of the seed, even if more than that is provided. This is possible to brute force in about
10 minutes. Solve the first puzzle normally to find the correct answer, then crack its random seed, and use that to predict the rest of the puzzle solutions. Use that to
reconstruct the final puzzle image, which has the flag written on it. Run `go run .` and then `python3 reconstruct_5.py`
```
