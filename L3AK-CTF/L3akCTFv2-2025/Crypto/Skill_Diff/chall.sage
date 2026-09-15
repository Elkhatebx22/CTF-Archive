import os
import hashlib

sb = (238, 180, 132, 65, 223, 139, 245, 252, 68, 184, 227, 73, 30, 225, 253, 204, 86, 7, 202, 243, 41, 213, 118, 167, 136, 193, 236, 107, 33, 13, 183, 229, 105, 55, 182, 94, 155, 109, 18, 119, 186, 52, 224, 221, 131, 83, 165, 110, 113, 185, 44, 209, 228, 157, 148, 143, 108, 134, 101, 141, 80, 31, 40, 23, 210, 154, 244, 181, 22, 226, 97, 151, 251, 76, 102, 125, 45, 158, 240, 137, 25, 235, 248, 53, 153, 166, 164, 208, 220, 198, 106, 88, 201, 163, 38, 121, 10, 82, 84, 173, 215, 161, 63, 24, 250, 57, 66, 4, 21, 1, 5, 43, 27, 92, 58, 218, 112, 114, 171, 103, 177, 99, 50, 87, 211, 122, 0, 39, 138, 75, 46, 239, 2, 6, 91, 176, 178, 127, 237, 169, 133, 34, 231, 15, 11, 81, 49, 69, 62, 123, 212, 71, 90, 249, 172, 98, 233, 254, 255, 203, 116, 8, 128, 200, 74, 145, 205, 187, 222, 59, 70, 16, 26, 207, 160, 217, 191, 246, 179, 72, 150, 140, 89, 14, 64, 174, 37, 232, 242, 170, 19, 47, 216, 77, 9, 67, 104, 36, 135, 35, 147, 60, 247, 117, 129, 56, 175, 196, 189, 149, 206, 42, 152, 192, 120, 51, 96, 85, 93, 144, 146, 126, 100, 48, 29, 32, 194, 130, 197, 162, 188, 61, 142, 95, 3, 159, 28, 124, 241, 190, 219, 230, 156, 20, 214, 54, 199, 111, 168, 79, 234, 195, 17, 12, 115, 78)

inv_sbox = [0]*256

for i, c in enumerate(sb):
    inv_sbox[c] = i

M = Matrix(Zmod(256), [(0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0),
 (0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0),
 (0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0),
 (0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0),
 (0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0),
 (0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0),
 (1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0),
 (0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0),
 (0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0),
 (1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1),
 (0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0),
 (0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1),
 (0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0),
 (1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0),
 (1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1),
 (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]) 

inv_M = M.inverse()

aff = [[109, 211], [123, 254], [81, 20], [129, 182], [251, 74], [57, 11], [213, 44], [155, 52], [205, 146], [239, 12], [123, 218], [143, 178], [63, 228], [153, 223], [237, 1], [133, 72]]

inv_aff = [[inverse_mod(a, 256), -inverse_mod(a, 256)*b] for a, b in aff]

KEY = list(map(Integer, os.urandom(16)))

def generate_round_keys(master):
    res = [master]
    for i in range(3):
        h = hashlib.sha256()
        h.update(bytes(res[-1]))
        h.update(bytes(master))
        res.append(list(h.digest()[:16]))
    return res

def encrypt_block(block, key):
    round_keys = generate_round_keys(key)
    block = [(b+k)%256 for b, k in zip(block, round_keys[0])]
    for r in range(3):
        block = list(map(Integer, M*vector(block)))
        for i, p in enumerate(aff):
            a, b = p
            block[i] = (a*block[i]+b)%256
            block[i]^^=1
            block[i] = sb[block[i]]
            block[i] = (block[i]+round_keys[r+1][i])%256
    return block

def differential_encrypt(block, key):
    round_keys = generate_round_keys(key) 
    block = [(b+k)%256 for b, k in zip(block, round_keys[0])]
    for r in range(3):
        block = list(map(Integer, M*vector(block)))
        for i, p in enumerate(aff):
            a, b = p
            block[i] = (a*block[i]+b)%256
            #block[i]^^=1
            #block[i] = sb[block[i]]
            block[i] = (block[i]+round_keys[r+1][i])%256
    return block

def encrypt_two_rounds(block, key):
    round_keys = generate_round_keys(key)
    block = [(b+k)%256 for b, k in zip(block, round_keys[0])]
    for r in range(2):
        block = list(map(Integer, M*vector(block)))
        for i, p in enumerate(aff):
            a, b = p
            block[i] = (a*block[i]+b)%256
            block[i]^^=1
            block[i] = sb[block[i]]
            block[i] = (block[i]+round_keys[r+1][i])%256
    return block

def truncated_encrypt(block, key):
    round_keys = generate_round_keys(key) 
    block = [(b+k)%256 for b, k in zip(block, round_keys[0])]
    for r in range(3):
        block = list(map(Integer, M*vector(block)))
        for i, p in enumerate(aff):
            a, b = p
            block[i] = (a*block[i]+b)%256
            block[i]^^=1
            if r<2:
                block[i] = sb[block[i]]
                block[i] = (block[i]+round_keys[r+1][i])%256
    return block

def print_differential(block1, block2):
    print(*[(b2-b1)%256 for b1, b2 in zip(block1, block2)])

def encrypt_blocks_and_log_differential(block1, block2, key):
    round_keys = generate_round_keys(key)
    block1 = [(b+k)%256 for b, k in zip(block1, round_keys[0])]
    block2 = [(b+k)%256 for b, k in zip(block2, round_keys[0])]
    print_differential(block1, block2)
    for r in range(3):
        block1 = list(map(Integer, M*vector(block1)))
        block2 = list(map(Integer, M*vector(block2)))
        print_differential(block1, block2)
        for i, p in enumerate(aff):
            a, b = p
            block1[i] = (a*block1[i]+b)%256
            block2[i] = (a*block2[i]+b)%256
        print_differential(block1, block2)
        for i in range(16):
            block1[i]^^=1
            block2[i]^^=1
        print_differential(block1, block2)
        if r<2:
            for i in range(16):
                block1[i] = sb[block1[i]]
                block2[i] = sb[block2[i]]
            print_differential(block1, block2)
            for i in range(16):
                block1[i] = (block1[i]+round_keys[r+1][i])%256
                block2[i] = (block2[i]+round_keys[r+1][i])%256
            print_differential(block1, block2)
    return block1, block2

def decrypt_one_round(block, rk):
    block = list(block)
    for i, p in enumerate(inv_aff):
        a, b = p
        block[i] = (block[i]-rk[i])%256
        block[i] = inv_sbox[block[i]]
        block[i]^^=1
        block[i] = (a*block[i]+b)%256
    block = list(map(Integer, inv_M*vector(block)))
    return block