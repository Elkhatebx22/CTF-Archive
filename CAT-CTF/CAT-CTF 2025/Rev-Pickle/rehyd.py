# rehyd.py  ─────────────────────────────────────────────────────────────
"""
Only contains the helper that turns the compressed byte-code back into
your original function.  Shipping this file leaks nothing important.
"""
import marshal, gzip, base64

def _rehydrate(b85, entry):
    code = marshal.loads(gzip.decompress(base64.b85decode(b85)))
    ns = {}
    exec(code, ns)
    return ns[entry]