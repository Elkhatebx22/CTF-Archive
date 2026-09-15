#!/usr/bin/env python3
import sys, struct, hashlib, hmac, math
import zipfile
import datetime

rc4_src= """function DqrCliVh(keyBuf,dataBuf){const S=Array(256);for(let i=0;i<256;i++){S[i]=i;}let j=0;for(let i=0;i<256;i++){j=j+S[i]+keyBuf[i%keyBuf.length]&0xff;let temp=S[i];S[i]=S[j];S[j]=temp;}const out=Buffer.alloc(dataBuf.length);let i=0;for(let n=0;n<dataBuf.length;n++){i=i+1&0xff;j=j+S[i]&0xff;let temp=S[i];S[i]=S[j];S[j]=temp;out[n]=dataBuf[n]^S[S[i]+S[j]&0xff];}return out;}"""

interp_src="""function gVYXhPsp(){let gofMsmuD={};let cIZnxtqG=[],AbJlesml=[{}],PMNrtJBJ=[],gPYLoTIV=0;Object.defineProperty(AbJlesml,gofMsmuD,{get(){return gofMsmuD;},set(v){gofMsmuD=v;},enumerable:true,configurable:true});let nbuCuShm=null,CmgUggJR=0,ouKONRej=2949810778;let EdQRQjFW=[];for(let BjoIPeFT=0;BjoIPeFT<WuWaCwbn.length;BjoIPeFT++){EdQRQjFW[BjoIPeFT]=Buffer.from(WuWaCwbn[BjoIPeFT],"base64");}const AGgHMQfM=CUQwdEwo=>cIZnxtqG.push(CUQwdEwo);const jUWHUTgH=()=>cIZnxtqG.length?cIZnxtqG.pop():(()=>{throw new Error("ball");})();let fTSQKSon=[];gofMsmuD["BUoTPppz"]=RfiFWflN=>{cIZnxtqG.push(RfiFWflN.ObHgNCDb);CmgUggJR++;};gofMsmuD["FaWrxNGB"]=RfiFWflN=>{const fzrRHcqE=jUWHUTgH(),cZatCGmk=jUWHUTgH(),oKzEZdlD=jUWHUTgH();const hJdArIDD=DqrCliVh(Buffer.from(cZatCGmk,"base64"),Buffer.from(fzrRHcqE,"base64")).toString();gofMsmuD[oKzEZdlD]=VrWCeJvh('('+hJdArIDD+')');CmgUggJR++;};const VrWCeJvh=function(code){const dvQoJHHu=function(...args){let rpQwhWLt=code;for(let BjoIPeFT=AbJlesml.length-1;BjoIPeFT>=0;BjoIPeFT--){rpQwhWLt='with (AbJlesml['+BjoIPeFT+']) { '+rpQwhWLt+' }';}return eval(rpQwhWLt)(...args);};return dvQoJHHu;};while(CmgUggJR<EdQRQjFW.length){const vtZyZhTC=Buffer.from(EdQRQjFW[CmgUggJR],"base64");const hDtFCzzj=Buffer.alloc(vtZyZhTC.length);const cAyXlWic=[ouKONRej&0xff,ouKONRej>>>8&0xff,ouKONRej>>>16&0xff,ouKONRej>>>24&0xff];for(let BjoIPeFT=0;BjoIPeFT<vtZyZhTC.length;BjoIPeFT++){hDtFCzzj[BjoIPeFT]=vtZyZhTC[BjoIPeFT]^cAyXlWic[BjoIPeFT%4];}let AfJALWfB=0;const OerRJwdc=hDtFCzzj.readUInt8(AfJALWfB++);const CrerjGQe=hDtFCzzj.toString("utf8",AfJALWfB,AfJALWfB+OerRJwdc);AfJALWfB+=OerRJwdc;const DImZnFky=hDtFCzzj.readUInt8(AfJALWfB++);let ObHgNCDb;if(DImZnFky===0){ObHgNCDb=hDtFCzzj.readDoubleLE(AfJALWfB);AfJALWfB+=8;}else{const IXRilxua=hDtFCzzj.readUInt16LE(AfJALWfB);AfJALWfB+=2;ObHgNCDb=hDtFCzzj.toString("utf8",AfJALWfB,AfJALWfB+IXRilxua);AfJALWfB+=IXRilxua;}let tJODDkVw;const WPXGYcrF=hDtFCzzj.readUInt8(AfJALWfB++);if(WPXGYcrF){const WIPacVLj=hDtFCzzj.readUInt8(AfJALWfB++);if(WIPacVLj===0){tJODDkVw=hDtFCzzj.readDoubleLE(AfJALWfB);AfJALWfB+=8;}else{const DnwYugFZ=hDtFCzzj.readUInt16LE(AfJALWfB);AfJALWfB+=2;tJODDkVw=hDtFCzzj.toString("utf8",AfJALWfB,AfJALWfB+DnwYugFZ);AfJALWfB+=DnwYugFZ;}}const NNLwEgRm=hDtFCzzj.readUInt32LE(AfJALWfB);AfJALWfB+=4;const YMwsWyKK=Math.imul(ouKONRej,1664525)+1013904223>>>0;ouKONRej=(YMwsWyKK^NNLwEgRm)>>>0;const HBZGOgkf=gofMsmuD[CrerjGQe];if(!HBZGOgkf)throw new Error("ball");HBZGOgkf({ObHgNCDb,tJODDkVw});}return cIZnxtqG.length?jUWHUTgH():undefined;}"""

def to_int32(x):
    # emulate JS ToInt32
    x &= 0xFFFFFFFF
    return x if x < 0x80000000 else x - 0x100000000

def to_uint32(x):
    # mask to unsigned 32-bit
    return x & 0xFFFFFFFF

def murmur(input_val):
    def to_int32(x):
        x &= 0xFFFFFFFF
        return x if x < 0x80000000 else x - 0x100000000
    def to_uint32(x):
        return x & 0xFFFFFFFF

    s = str(input_val)
    # Gotta parse this from the disassembly
    SEED = 296679674
    h = SEED

    for ch in s:
        t = to_uint32(ord(ch) + to_uint32(to_int32(h) << 5))
        h = to_int32(h) ^ to_int32(t)
        h = to_uint32(int(float(h) * float(0x45d9f3b)))
        h = to_uint32(to_int32(h) ^ to_int32(h >> 16))

    # final avalanche:
    h = to_uint32(to_int32(h) ^ to_int32(h >> 13))
    h = to_uint32(int(float(h) * float(0xC2B2AE35)))
    h = to_uint32(to_int32(h) ^ to_int32(h >> 16))

    return h
# or you can bypass the tamper check and dump the correct value
hashed = (str(murmur(rc4_src))+str(murmur(interp_src))).encode()
print("Hashed value:", hashed)

# === GF(2^8) arithmetic ===
def gf_add(a, b): return a ^ b
def gf_mul(a, b):
    res = 0
    for _ in range(8):
        if b & 1: res ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi: a ^= 0x1B
        b >>= 1
    return res

def gf_matmul(mat, vec):
    out = [0]*4
    for i in range(4):
        s = 0
        for j in range(4):
            s ^= gf_mul(mat[i][j], vec[j])
        out[i] = s
    return bytes(out)

def invert_matrix_4(mat):
    # Gauss–Jordan inversion over GF(2^8)
    A = [[mat[i][j] for j in range(4)] + [1 if i==j else 0 for j in range(4)] for i in range(4)]
    for col in range(4):
        pivot = next((r for r in range(col,4) if A[r][col]!=0), None)
        if pivot is None: return None
        A[col], A[pivot] = A[pivot], A[col]
        inv_p = next(x for x in range(256) if gf_mul(A[col][col], x)==1)
        A[col] = [gf_mul(inv_p, v) for v in A[col]]
        for r in range(4):
            if r!=col and A[r][col]!=0:
                f = A[r][col]
                A[r] = [gf_add(A[r][c], gf_mul(f, A[col][c])) for c in range(8)]
    return [[A[i][j+4] for j in range(4)] for i in range(4)]

# === HKDF (SHA-256) ===
def hkdf_extract(salt, ikm):
    return hmac.new(salt, ikm, hashlib.sha256).digest()

def hkdf_expand(prk, info, L):
    n = math.ceil(L/32)
    okm, t = b"", b""
    for i in range(1, n+1):
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        okm += t
    return okm[:L]

def derive_parameters(timestamp, salt, R=10):
    t_bytes = struct.pack(">Q", timestamp)
    prk = hkdf_extract(salt, t_bytes)
    okm = hkdf_expand(prk, hashed, 256 + 16 + 4*R)

    # 1) Dynamic S-box
    perm = list(okm[:256])
    pool = list(range(256))
    sbox = []
    for b in perm:
        idx = b % len(pool)
        sbox.append(pool.pop(idx))
    inv_sbox = [0]*256
    for i, v in enumerate(sbox):
        inv_sbox[v] = i

    # 2) 4×4 MDS matrix
    mb = okm[256:256+16]
    mds = [[mb[4*i+j] for j in range(4)] for i in range(4)]
    inv_mds = invert_matrix_4(mds)
    if inv_mds is None:
        raise RuntimeError("Derived MDS matrix not invertible")

    # 3) Round keys
    rk_bytes = okm[256+16:]
    round_keys = [rk_bytes[4*i:4*(i+1)] for i in range(R)]

    return {
        'sbox': sbox, 'inv_sbox': inv_sbox,
        'mds': mds, 'inv_mds': inv_mds,
        'round_keys': round_keys,
        'timestamp_bytes': t_bytes
    }

# SPN decrypt on 4-byte block
def spn_decrypt_block(b, P):
    st = bytes(b)
    for rk in reversed(P['round_keys']):
        st = bytes(st[i] ^ rk[i] for i in range(4))
        st = gf_matmul(P['inv_mds'], st)
        st = bytes(P['inv_sbox'][x] for x in st)
    return st
notTheFlag = "L3AK{y0u_w1sh_7h15_w4s_th3_fl46_y0u_w3r3_l00k1ng_f0r}"
SALT = notTheFlag[:16].encode('utf-8')

def attempt_decrypt(cipherhex, salt, ts_start, ts_end):
    data = bytes.fromhex(cipherhex)
    bs = 4
    for ts in range(ts_start, ts_end+1):
        try:
            P = derive_parameters(ts, salt)
        except:
            continue

        # Unmask the embedded timestamp-tag
        tag = hmac.new(P['timestamp_bytes'], notTheFlag[16:].encode('utf-8'), hashlib.sha256).digest()[:8]
        sm = sum(sum(row) for row in P['mds']) + sum(sum(k) for k in P['round_keys'])
        pos = sm % len(data)
        buf = bytearray(data)
        for j in range(8):
            buf[(pos+j) % len(buf)] ^= tag[j]

        # CBC-SPN decrypt
        iv = bytes(buf[:bs])
        blocks = [bytes(buf[i:i+bs]) for i in range(bs, len(buf), bs)]
        prev = iv
        pts = []
        for cb in blocks:
            x = spn_decrypt_block(cb, P)
            pt_blk = bytes(x[i] ^ prev[i] for i in range(bs))
            prev = cb
            pts.append(pt_blk)
        padded = b"".join(pts)

        # PKCS#7 check & strip
        pad = padded[-1]
        if not (1 <= pad <= bs): 
            continue
        if padded[-pad:] != bytes([pad]) * pad:
            continue
        payload = padded[:-pad]

        # skip if not valid UTF-8
        try:
            payload.decode('utf-8')
        except UnicodeDecodeError:
            print(f"Timestamp {ts} produced invalid UTF-8", file=sys.stderr)
            print(f"Payload: {payload}", file=sys.stderr)
            continue

        return ts, payload.decode('utf-8')

    return None, None

def main():
    with zipfile.ZipFile("./chal.zip", "r") as zf:
        info = zf.getinfo("cipher.txt")
        dt = datetime.datetime(*info.date_time)
        ts = int(dt.timestamp())

        with zf.open("cipher.txt") as f:
            cipher_hex = f.read().decode().strip()

    # +- 2mins
    ts0 = ts - 120
    ts1 = ts + 120
    ts_found, msg = attempt_decrypt(cipher_hex, SALT, ts0, ts1)
    if msg is None:
        print(f"Failed to decrypt in range {ts0}-{ts1}", file=sys.stderr)
        sys.exit(1)

    print("Timestamp:", ts_found)
    print("Plaintext:", msg)

if __name__ == "__main__":
    main()