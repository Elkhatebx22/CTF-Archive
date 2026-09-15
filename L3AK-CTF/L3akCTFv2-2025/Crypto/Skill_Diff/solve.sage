load('./chall.sage')
import itertools
import random
from tqdm import tqdm
differentials = {(1, 250): [(0, (60, 110)), (5, (76, 182))],
 (0, 62): [(1, (174, 182)), (3, (170, 66)), (9, (182, 158))],
 (0, 90): [(2, (196, 52)), (7, (236, 188))],
 (4, 142): [(4, (240, 244))],
 (2, 102): [(6, (210, 16)), (8, (130, 144))],
 (2, 4): [(10, (144, 206)), (11, (80, 150))],
 (0, 116): [(12, (214, 160))],
 (1, 188): [(13, (136, 238))]}
differentials2 = {(7, 38): [(0, 122)],
 (2, 98): [(1, 86)],
 (3, 2): [(2, 194), (3, 34)],
 (5, 18): [(4, 86), (7, 150)],
 (4, 102): [(5, 146), (11, 254)],
 (0, 202): [(6, 74), (9, 190), (13, 82), (14, 122)],
 (1, 102): [(8, 58), (12, 94)],
 (6, 250): [(10, 86)]}
ddt = [[[] for j in range(256)] for i in range(256)]

for d in range(256):
    for pt in range(256):
        ddt[d][(sb[(pt+d)%256]-sb[pt])%256].append(sb[pt])

def createPTs():
    f = open("plaintext.txt", "wb")
    for step, inp in enumerate(differentials):
        inp, inp_d = inp
        print(inp, inp_d)
        d = list(map(Integer, inv_M*vector([0]*inp+[inp_d]+[0]*(15-inp))))
        for z in range(200000):
            pt1 = random.randbytes(16)
            pt2 = [(i+j)%256 for i, j in zip(pt1, d)]
            f.write(pt1+bytes(pt2))
    for step, inp in enumerate(differentials2):
        inp, inp_d = inp
        print(inp, inp_d)
        d = list(map(Integer, inv_M*vector([0]*inp+[inp_d]+[0]*(15-inp))))
        for z in range(10000):
            pt1 = random.randbytes(16)
            pt2 = [(i+j)%256 for i, j in zip(pt1, d)]
            f.write(pt1+bytes(pt2))
    for inp in range(16):
        d = list(map(Integer, inv_M*vector([0]*inp+[2]+[0]*(15-inp))))
        for z in range(100):
            pt1 = random.randbytes(16)
            pt2 = [(i+j)%256 for i, j in zip(pt1, d)]
            f.write(pt1+bytes(pt2))
    f.close()
def recoverKey():
    ptr = 0
    last_key = [None]*16
    last_key[14] = list(range(256))
    last_key[15] = [0]
    for step, inp in enumerate(differentials):
        inp, inp_d = inp
        print(inp, inp_d)
        freqs = [([0]*256, [0]*256) for i in range(len(differentials[(inp, inp_d)]))]
        d = list(map(Integer, inv_M*vector([0]*inp+[inp_d]+[0]*(15-inp))))
        for z in tqdm(range(200000)):
            pt1, pt2 = pts[ptr:ptr+16], pts[ptr+16:ptr+32]
            ct1, ct2 = cts[ptr:ptr+16], cts[ptr+16:ptr+32]
            ptr += 32
            for i, out in enumerate(differentials[(inp, inp_d)]):
                out, e = out
                cd = (ct2[out]-ct1[out])%256
                for ct in ddt[e[0]][cd]:
                    freqs[i][0][(ct1[out]-ct)%256]+=1
                for ct in ddt[e[1]][cd]:
                    freqs[i][1][(ct1[out]-ct)%256]+=1
        for i, out in enumerate(differentials[(inp, inp_d)]):
            out, e = out
            f1, f2 = list(enumerate(freqs[i][0])), list(enumerate(freqs[i][1]))
            s1, s2 = sorted(f1, key=lambda x: x[1]), sorted(f2, key=lambda x: x[1])
            scores = []
            for k in range(256):
                scores.append(s1.index(f1[k])+s2.index(f2[k]))
            scores = sorted(list(enumerate(scores)), key = lambda x: x[1])
            kgs = []
            i = -1
            while True:
                if scores[i][1]>=scores[-1][1]-15:
                    kgs.append(scores[i][0])
                else:
                    break
                i-=1
            last_key[out] = kgs
            print(scores[-7:])
        print("Finished", inp, inp_d)
        print(last_key)
    print(prod(list(map(len, last_key))), "keys to filter")
    col = M.column(1)
    valid = []
    for kg in tqdm(itertools.product(*last_key), total = prod(list(map(len, last_key)))):
        ct1, ct2 = cts[:16], cts[16:32]
        ct1 = decrypt_one_round(ct1, kg)
        ct2 = decrypt_one_round(ct2, kg)
        diff = [(ct2[i]-ct1[i])%256 for i in range(16)]
        for i in range(16):
            if col[i]==0 and diff[i]!=0:
                break
        else:
            valid.append(kg)
    print(len(valid))
    print(valid)
    valid2 = valid
    valid = []
    for i in range(256):
        for kg in valid2:
            nkg = list(kg)
            nkg[-1] = i
            valid.append(tuple(nkg))
    valid2 = []
    col = M.column(3)
    for kg in valid:
        ct1, ct2 = cts[32*(1620000):32*(1620000)+16], cts[32*(1620000)+16:32*(1620000)+32]
        ct1 = decrypt_one_round(ct1, kg)
        ct2 = decrypt_one_round(ct2, kg)
        diff = [(ct2[i]-ct1[i])%256 for i in range(16)]
        for i in range(16):
            if col[i]==0 and diff[i]!=0:
                break
        else:
            valid2.append(kg)
    valid = valid2
    print(valid)
    print(len(valid))
    valid2 = []
    col = M.column(2)
    for kg in valid:
        ct1, ct2 = cts[32*(1000000):32*(1000000)+16], cts[32*(1000000)+16:32*(1000000)+32]
        ct1 = decrypt_one_round(ct1, kg)
        ct2 = decrypt_one_round(ct2, kg)
        diff = [(ct2[i]-ct1[i])%256 for i in range(16)]
        for i in range(16):
            if col[i]==0 and diff[i]!=0:
                break
        else:
            valid2.append(kg)
    valid = valid2
    print(valid)
    print(len(valid))
    valid2 = []
    col = M.column(2)
    for kg in valid:
        ct1, ct2 = cts[32*(1000001):32*(1000001)+16], cts[32*(1000001)+16:32*(1000001)+32]
        ct1 = decrypt_one_round(ct1, kg)
        ct2 = decrypt_one_round(ct2, kg)
        diff = [(ct2[i]-ct1[i])%256 for i in range(16)]
        for i in range(16):
            if col[i]==0 and diff[i]!=0:
                break
        else:
            valid2.append(kg)
    valid = valid2
    print(valid)
    print(len(valid))
    valid2 = []
    col = M.column(2)
    for kg in valid:
        ct1, ct2 = cts[32*(1000002):32*(1000002)+16], cts[32*(1000002)+16:32*(1000002)+32]
        ct1 = decrypt_one_round(ct1, kg)
        ct2 = decrypt_one_round(ct2, kg)
        diff = [(ct2[i]-ct1[i])%256 for i in range(16)]
        for i in range(16):
            if col[i]==0 and diff[i]!=0:
                break
        else:
            valid2.append(kg)
    valid = valid2
    print(valid)
    print(len(valid))
    valid2 = []
    col = M.column(4)
    for kg in valid:
        ct1, ct2 = cts[32*(1640002):32*(1640002)+16], cts[32*(1640002)+16:32*(1640002)+32]
        ct1 = decrypt_one_round(ct1, kg)
        ct2 = decrypt_one_round(ct2, kg)
        diff = [(ct2[i]-ct1[i])%256 for i in range(16)]
        for i in range(16):
            if col[i]==0 and diff[i]!=0:
                break
        else:
            valid2.append(kg)
    valid = valid2
    print(valid)
    print(len(valid))
    assert len(valid)==1
    rk4 = valid[0]
    print("Recovered 4th round key:", rk4)
    
    # Recover the 3rd round key
    second_ptr_start = ptr
    rk3 = [-1]*16
    for step, inp in enumerate(differentials2):
        inp, inp_d = inp
        freqs = [[0]*256 for i in range(len(differentials2[(inp, inp_d)]))]
        d = list(map(Integer, inv_M*vector([0]*inp+[inp_d]+[0]*(15-inp))))
        for z in range(10000):
            pt1, pt2 = pts[ptr:ptr+16], pts[ptr+16:ptr+32]
            ct1, ct2 = cts[ptr:ptr+16], cts[ptr+16:ptr+32]
            ptr += 32
            ct1 = [inv_sbox[(ct1[i]-rk4[i])%256]^^1 for i in range(16)]
            ct2 = [inv_sbox[(ct2[i]-rk4[i])%256]^^1 for i in range(16)]
            for i, p in enumerate(inv_aff):
                a, b = p
                ct1[i] = (a*ct1[i]+b)%256
                ct2[i] = (a*ct2[i]+b)%256
            ct1 = list(map(Integer, inv_M*vector(ct1)))
            ct2 = list(map(Integer, inv_M*vector(ct2)))
            #print(ct1)
            #print(ct2)
            for i, out in enumerate(differentials2[(inp, inp_d)]):
                out, e = out
                cd = (ct2[out]-ct1[out])%256
                for ct in ddt[e][cd]:
                    freqs[i][(ct1[out]-ct)%256]+=1
        for i, out in enumerate(differentials2[(inp, inp_d)]):
            out, e = out
            rk3[out] = freqs[i].index(max(freqs[i]))
            print(sorted(list(enumerate(freqs[i])), key = lambda x: x[1])[-7:])
        print("Finished", inp, inp_d)
        print(rk3)
    valid = []
    for i in range(256):
        rk3[-1] = i
        ct1, ct2 = cts[:16], cts[16:32]
        ct1 = decrypt_one_round(ct1, rk4)
        ct2 = decrypt_one_round(ct2, rk4)
        ct1 = decrypt_one_round(ct1, rk3)
        ct2 = decrypt_one_round(ct2, rk3)
        diff = [(ct2[i]-ct1[i])%256 for i in range(16)]
        #print(diff)
        for j in range(16):
            if j!=1 and diff[j]!=0:
                break
        else:
            valid.append(rk3.copy())
    valid2 = valid
    valid = []
    for rk3 in valid2:
        ct1, ct2 = cts[32:48], cts[48:64]
        ct1 = decrypt_one_round(ct1, rk4)
        ct2 = decrypt_one_round(ct2, rk4)
        ct1 = decrypt_one_round(ct1, rk3)
        ct2 = decrypt_one_round(ct2, rk3)
        diff = [(ct2[i]-ct1[i])%256 for i in range(16)]
        #print(diff)
        for j in range(16):
            if j!=1 and diff[j]!=0:
                break
        else:
            valid.append(rk3.copy())
    print(len(valid))
    print(valid)
    assert len(valid)==1
    rk3 = valid[0]
    rk2 = []
    for inp in range(16):
        freqs = [0]*256
        e = (2*aff[inp][0])%256
        for z in range(100):
            pt1, pt2 = pts[ptr:ptr+16], pts[ptr+16:ptr+32]
            ct1, ct2 = cts[ptr:ptr+16], cts[ptr+16:ptr+32]
            ptr += 32
            ct1 = decrypt_one_round(ct1, rk4)
            ct2 = decrypt_one_round(ct2, rk4)
            ct1 = decrypt_one_round(ct1, rk3)
            ct2 = decrypt_one_round(ct2, rk3)
            cd = (ct2[inp]-ct1[inp])%256
            for ct in ddt[e][cd]:
                freqs[(ct1[inp]-ct)%256]+=1
        print(sorted(list(enumerate(freqs)), key = lambda x: x[1])[-7:])
        rk2.append(freqs.index(max(freqs)))
    ct2 = decrypt_one_round(ct2, rk2)
    key2 = [(ct2[i]-pt2[i])%256 for i in range(16)]
    ct1 = decrypt_one_round(ct1, rk2)
    key1 = [(ct1[i]-pt1[i])%256 for i in range(16)]
    print(key1)
    print(key2)
    assert key1==key2
    rk1 = key1
    rk4 = list(rk4)
    print(generate_round_keys(rk1))
    assert generate_round_keys(rk1) == [rk1, rk2, rk3, rk4]
    enc_flag = open("./flag.enc", "rb").read()
    blocks = [enc_flag[i:i+16] for i in range(0, len(enc_flag), 16)]
    for i in range(len(blocks)):
        blocks[i] = decrypt_one_round(blocks[i], rk4)
        blocks[i] = decrypt_one_round(blocks[i], rk3)
        blocks[i] = decrypt_one_round(blocks[i], rk2)
        blocks[i] = [(b-k)%256 for b, k in zip(blocks[i], rk1)]
    print(b''.join(list(map(bytes, blocks))))
    return (rk1, rk2, rk3, rk4)


createPTs()

while True:
    l = input("Did you encrypt plaintext.txt and place the flag.enc and input.enc?")
    if l=='yes':
        break

pts = open("plaintext.txt", "rb").read()
cts = open("input.enc", "rb").read()
assert len(pts)==len(cts)

valid = recoverKey()
print(len(valid))
for k in valid:
    print(k)

