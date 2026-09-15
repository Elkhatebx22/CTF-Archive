# babyRev(beginner)

- **Author:** 0xnil
- **Category:** Reverse
- **Solves:** 676

## Description

They always give you strings challenges, we are not the same, we do better. Author: 0xnil [babyrev](<https://ctf.l3ak.team/files/03104d284f8093dd8365243bd4b6bd2a/babyrev?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjIyfQ.aHGprQ.N2iNfTrzsJyhjiR9hn_ShqOjWgY>)
babyrev.zip

---

## Solution

The program implements a substitution cipher that maps lowercase letters to other letters:

```
a->q, b->w, c->e, d->r, e->t, f->y, g->u, h->i, i->o, j->p, k->a, l->s, m->d, n->f
o->g, p->h, q->j, r->k, s->l, t->z, u->x, v->c, w->v, x->b, y->n, z->m
```

The encrypted flag is: `L3AK{ngx_qkt_fgz_ugffq_uxtll_dt}`

Reverse the mapping to decrypt:

```python
#!/usr/bin/env python3

encrypted = "L3AK{ngx_qkt_fgz_ugffq_uxtll_dt}"

# Reverse mapping
reverse = {
    'q': 'a', 'w': 'b', 'e': 'c', 'r': 'd', 't': 'e', 'y': 'f', 'u': 'g',
    'i': 'h', 'o': 'i', 'p': 'j', 'a': 'k', 's': 'l', 'd': 'm', 'f': 'n',
    'g': 'o', 'h': 'p', 'j': 'q', 'k': 'r', 'l': 's', 'z': 't', 'x': 'u',
    'c': 'v', 'v': 'w', 'b': 'x', 'n': 'y', 'm': 'z'
}

decrypted = ""
for char in encrypted:
    if char.islower():
        decrypted += reverse.get(char, char)
    else:
        decrypted += char

print(f"Flag: {decrypted}")
```

## Flag

**L3AK{you_are_not_gonna_guess_me}**
