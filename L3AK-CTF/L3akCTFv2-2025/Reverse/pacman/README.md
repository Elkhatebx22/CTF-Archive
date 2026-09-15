# pacman

- **Author:** 0xnil
- **Category:** Reverse
- **Solves:** 153

## Description

I am more than just a man, I am PACMAN!

---

## TL;DR

1. **Binary Analysis**: Examine the packed binary structure and entry point
2. **Loader Extraction**: Analyze the injected `.pac` section assembly code
3. **Algorithm Reversal**: Understand and reverse the 3-layer decryption
4. **Parameter Extraction**: Extract key and text section info from loader
5. **Binary Decryption**: Decrypt the original challenge binary
6. **Feistel Solution**: Solve the Feistel network challenge
7. **Flag Recovery**: Decrypt the target ciphertext to get the flag

## Challenge Analysis

Players are given the `pac` binary, which is a packed version of the original challenge. The packer has encrypted the `.text` section and injected a custom loader that decrypts the code at runtime.

## Solution

### Step 1: Analyze the Packed Binary

First, examine the packed binary structure:

```bash
# Check file type and entry point
file pac
readelf -h pac | grep Entry
readelf -S pac
```

The entry point will point to the injected `.pac` section, not the original `.text` section.

### Step 2: Examine the New Section

The packer injects a `.pac` section that contains:

- Decryption routines (assembly code)
- 16-byte encryption key
- Text section address and size
- Jump instruction to original entry point

### Step 3: Extract the Loader Code

Disassemble the `.pac` section to understand the decryption algorithm:

```bash
# Extract the .pac section
objdump -d pac -j .pac

# Or use gdb to examine the entry point
gdb pac
(gdb) x/50i $entry_point
```

### Step 4: Understand the Decryption Algorithm

From the assembly analysis, the decryption performs these operations in reverse order:

1. **XXTEA Decryption**: Reverse of XXTEA encryption
2. **ROT_BITS Decryption**: Rotate right by 3 bits (`ror byte [rdi], 3`)
3. **ROT_XOR Decryption**: Subtract 0x37, then XOR with 0xAA

### Step 5: Extract Key and Parameters

From the loader section, extract:

- **Key**: 16 bytes starting at offset `g_loader_sz - 0x20`
- **Text Address**: 8 bytes at offset `g_loader_sz - 0x10`
- **Text Size**: 4 bytes at offset `g_loader_sz - 0x8`

### Step 6: Decrypt the Original Binary

Implement the decryption algorithm to recover the original challenge:

```python
#!/usr/bin/env python3

def rot_xor_decrypt(data):
    """Reverse ROT_XOR: subtract 0x37, then XOR with 0xAA"""
    result = bytearray()
    for byte in data:
        byte = (byte - 0x37) & 0xFF
        byte ^= 0xAA
        result.append(byte)
    return bytes(result)

def rot_bits_decrypt(data):
    """Rotate right by 3 bits"""
    result = bytearray()
    for byte in data:
        result.append(((byte >> 3) | (byte << 5)) & 0xFF)
    return bytes(result)

def xxtea_decrypt(data, key):
    """XXTEA decryption (reverse of the assembly implementation)"""
    # Implementation based on the assembly code analysis
    # This requires understanding the XXTEA algorithm and reversing it
    pass

def decrypt_text_section(encrypted_data, key):
    """Decrypt the text section using the 3-layer algorithm"""
    # Apply decryption in reverse order
    data = xxtea_decrypt(encrypted_data, key)
    data = rot_bits_decrypt(data)
    data = rot_xor_decrypt(data)
    return data
```

### Step 7: Solve the Feistel Challenge

Once the original binary is decrypted, it reveals a 4-round Feistel network challenge:

```c
// From the decrypted chall.c
static const uint64_t round_keys[ROUNDS] = { 
    0x1337DEADBEEF, 0xC0DE12345678, 0xABCDEF012345, 0x9876543210AB 
};

static const uint8_t target_cipher[BLOCK_SIZE * 2] = {
    0x91, 0xBC, 0x04, 0x8F, 0x7A, 0x48, 0x83, 0xFD,
    0x31, 0x63, 0x41, 0x16, 0x93, 0xB2, 0xA9, 0x1E,
    0x4F, 0x94, 0x08, 0x6B, 0x54, 0xA4, 0xBE, 0x2F,
    0xAF, 0xDC, 0x54, 0x98, 0x7E, 0x9E, 0x2E, 0x92
};
```

### Step 8: Implement Feistel Decryption

```python
def feistel(half, key):
    half ^= key
    half = ((half << 13) | (half >> 51)) ^ (half * 31)
    return half & 0xFFFFFFFFFFFFFFFF

def feistel_decrypt(block):
    L = struct.unpack('<Q', block[:8])[0]
    R = struct.unpack('<Q', block[8:16])[0]
    
    round_keys = [0x1337DEADBEEF, 0xC0DE12345678, 0xABCDEF012345, 0x9876543210AB]
    
    for i in range(3, -1, -1):  # Reverse order
        tmp = L
        L = R ^ feistel(L, round_keys[i])
        R = tmp
    
    return struct.pack('<QQ', L, R)

def solve_feistel():
    target = bytes.fromhex('91 BC 04 8F 7A 48 83 FD 31 63 41 16 93 B2 A9 1E 4F 94 08 6B 54 A4 BE 2F AF DC 54 98 7E 9E 2E 92'.replace(' ', ''))
    
    block1 = feistel_decrypt(target[:16])
    block2 = feistel_decrypt(target[16:32])
    
    return (block1 + block2).decode('utf-8', errors='ignore')
```

## Flag

**L3AK{feistel_netWork_Is_fun!!!!}**
