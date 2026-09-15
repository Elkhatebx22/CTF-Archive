# Really Simple Algorithm

- **Tags:** `baby`
- **Author:** Suvoni

## Description

Like I said, it's really simple! Author: Suvoni nc 193.148.168.30 5668 [server.py](https://ctf.l3ak.team/files/36245c79edc3c493e2640638ae7cb70e/server.py?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6MzR9.ZlPVZQ.sR_EMBnw_GKw8gbQXKUfyWdoFeE)

## Official Solution / Writeup

```markdown
You can use Hastad's Broadcast Attack to find the flag. To do this, we can simply get ``e = 1337`` pairs of ``(n_i,c_i)`` from the server, use the Chinese Remainder Theorem to find ``x``, then take the 1337th root to get the flag.

https://en.wikipedia.org/wiki/Chinese_remainder_theorem

https://docs.xanhacks.xyz/crypto/rsa/08-hastad-broadcast-attack/

```
