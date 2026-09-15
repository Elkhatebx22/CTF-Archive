#!/usr/bin/env python3

def decrypt_flag():
    encrypted_flag = "L3AK{ngx_qkt_fgz_ugffq_uxtll_dt}"
    
    reverse_mapping = {
        'q': 'a', 'w': 'b', 'e': 'c', 'r': 'd', 't': 'e', 'y': 'f', 'u': 'g',
        'i': 'h', 'o': 'i', 'p': 'j', 'a': 'k', 's': 'l', 'd': 'm', 'f': 'n',
        'g': 'o', 'h': 'p', 'j': 'q', 'k': 'r', 'l': 's', 'z': 't', 'x': 'u',
        'c': 'v', 'v': 'w', 'b': 'x', 'n': 'y', 'm': 'z'
    }
    
    decrypted = ""
    for char in encrypted_flag:
        if char.islower():
            decrypted += reverse_mapping.get(char, char)
        else:
            decrypted += char
    
    return decrypted

if __name__ == "__main__":
    flag = decrypt_flag()
    print(f"Flag: {flag}")
