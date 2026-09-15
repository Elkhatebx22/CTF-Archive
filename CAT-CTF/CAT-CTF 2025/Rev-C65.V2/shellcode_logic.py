def xor_encrypt(data: bytes, seed: int = 0x3B) -> bytes:
    key = seed
    out = bytearray()
    for b in data:  
        c = b ^ key
        out.append(c)
        key = (key + c) & 0xFF  
    return bytes(out)
def feistel_encrypt(data: bytes, key: int = 0x3B, const_seed: int = 0x05) -> bytes:
    assert len(data) == 16
    arr = bytearray(data)
    CONST = const_seed
    for i in range(0, 16, 2):
        R0 = arr[i]
        L0 = arr[i+1]
        F = (((R0 ^ key) << 1) + CONST) & 0xFF
        arr[i]   = L0
        arr[i+1] = R0 ^ F
        CONST = (CONST + 1) & 0xFF
    return bytes(arr)
if __name__ == '__main__':
    import sys

plaintext_hex = input("The input is: ")
plaintext = bytes.fromhex(plaintext_hex)

stage1 = xor_encrypt(plaintext)
stage2 = feistel_encrypt(stage1)

ciphertext = bytes([0x87,0xf3,0xf7,0xde,0x5f,0x3e,0x62,0x07,0xcd,0x50,0xff,0x43,0xf7,0x77,0xec,0x6b])

if stage2 == ciphertext:
    A = 1
else:
    A = 0

print(A)
