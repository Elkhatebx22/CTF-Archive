# Fire Checker

- **Author:** ahh
- **Target:** `nc 34.139.98.117 6667`

## Description

It's so easy to make a secure flag checker, just check it on the server, duh

---

## solver summary

AA XX replace "Incorrect," "Correct!" +1 replace "you\x20guessed\x20AA,\x20but\x20the\x20flag\x20is\x20" "" +1 replace "." "\x20is\x20the\x20flag!" +1 replace "\n" "" +1 -- --separator XX
