# Crypto on the rocks

- **Author:** supaaasugee

## Description

When life gives you digital signatures, put them on the rocks and drink them straight up. This challenge is like a stiff pour of cryptographic Hennessey. No chaser. Author: supaaasugee nc 193.148.168.30 5667 [chal.py](https://ctf.l3ak.team/files/1be914974f4c039b84504766ca8a4593/chal.py?token=eyJ1c2VyX2lkIjo3NzMsInRlYW1faWQiOjM2MSwiZmlsZV9pZCI6MzZ9.ZlPWvQ.0V5gl295vFqWNQxYeoOnYQ5tQn0)

---

# Henny on the rocks solution

Run the challenge PoC script:

```bash
python3 exploit.py <remote-host> <remote-port> <nsigs(Default: 100)>

python exploit.py 172.17.0.2 1337 80
```

The script will connect and receive $n$ signatures from the remote host then runs the attack defined in `utils.py` that solves the hidden number problem using an attack based on the shortest vector problem.

- The hidden number problem is defined as finding y such that {xi = {aij * yj} + bi mod m}.

... *To be continued*
