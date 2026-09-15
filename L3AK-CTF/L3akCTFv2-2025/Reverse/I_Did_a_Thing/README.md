# I Did a Thing

- **Author:** SteakEnthusiast
- **Category:** Reverse
- **Solves:** 4
- **Connection:** `https://ctf.l3ak.team/files/68917b8e711959b8ba8e4da833aaf831/chal.zip?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjI3fQ.aHGslQ.bi7lxMeoQfeRD2YISwEY2dVY7vM`

## Description

I like obfuscation :D It is recommended to play rev/Useless VM as a prelude to this challenge. Author: SteakEnthusiast [chal.zip](<https://ctf.l3ak.team/files/68917b8e711959b8ba8e4da833aaf831/chal.zip?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjI3fQ.aHGslQ.bi7lxMeoQfeRD2YISwEY2dVY7vM>)
I Did a Thing.zip

---

## Flag Format

`L3AK{V1rtu4l_M4ch1n3_M4st3r_H00r4y!!!:)}`

## Author's Post-Mortem

After the competition ended, someone pointed out that the VM only executed two opcode shuffle instructions. This was unintentional, and I realized I had accidentally compiled the VM with the opcode shuffling features disabled. Since this was meant to be a big part of the challenge, I've decided to include the intended version of the challenge's distribution and solution files in the `/dist/ideal-version-dist` and `/dist/ideal-version-solution` directories, respectively. The original distribution and solution files given to participants during the competition are available in the `/dist/ctfd-dist` and `/dist/ctfd-solution` directories.
