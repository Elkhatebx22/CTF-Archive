#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define ROUNDS     4
#define BLOCK_SIZE 16  // 128-bit block

/* Round keys (you can change these to anything you like) */
static const uint64_t round_keys[ROUNDS] = { 0x1337DEADBEEF, 0xC0DE12345678, 0xABCDEF012345, 0x9876543210AB };

/* Example target ciphertext for the "right" passphrase */
// put this in target cipher : 91 BC 04 8F 7A 48 83 FD 31 63 41 16 93 B2 A9 1E 4F 94 08 6B 54 A4 BE 2F AF DC 54 98 7E 9E 2E 92
// L3AK{feistel_netWork_Is_fun!!!!}

static const uint8_t target_cipher[BLOCK_SIZE * 2] = {
    0x91, 0xBC, 0x04, 0x8F, 0x7A, 0x48, 0x83, 0xFD,
    0x31, 0x63, 0x41, 0x16, 0x93, 0xB2, 0xA9, 0x1E,
    0x4F, 0x94, 0x08, 0x6B, 0x54, 0xA4, 0xBE, 0x2F,
    0xAF, 0xDC, 0x54, 0x98, 0x7E, 0x9E, 0x2E, 0x92
};

uint64_t feistel(uint64_t half, uint64_t key) {
    half ^= key;
    half = ((half << 13) | (half >> 51)) ^ (half * 31);
    return half;
}

void feistel_encrypt(uint8_t *block) {
    uint64_t *L = (uint64_t *)block;
    uint64_t *R = (uint64_t *)(block + 8);

    for (int i = 0; i < ROUNDS; i++) {
        uint64_t tmp = *R;
        *R = *L ^ feistel(*R, round_keys[i]);
        *L = tmp;
    }
}

// void feistel_decrypt(uint8_t *block) {
//     uint64_t *L = (uint64_t *)block;
//     uint64_t *R = (uint64_t *)(block + 8);

//     for (int i = ROUNDS - 1; i >= 0; i--) {
//         uint64_t tmp = *L;
//         *L = *R ^ feistel(*L, round_keys[i]);
//         *R = tmp;
//     }
// }

int main(void) {
    uint8_t buf[BLOCK_SIZE * 2 + 1];
    uint8_t work[BLOCK_SIZE * 2];

    printf("Enter passphrase (32 chars): ");
    if (!fgets((char*)buf, sizeof(buf), stdin)) {
        return 1;
    }
    buf[strcspn((char*)buf, "\n")] = 0;

    if (strlen((char*)buf) != BLOCK_SIZE * 2) {
        printf("Invalid input length. Must be exactly %d characters.\n", BLOCK_SIZE * 2);
        return 1;
    }

    memcpy(work, buf, BLOCK_SIZE * 2);

    feistel_encrypt(work);
    feistel_encrypt(work + BLOCK_SIZE);
    
    // printf("Encrypted ciphertext: ");
    // for (int i = 0; i < BLOCK_SIZE * 2; i++) {
    //     printf("%02X ", work[i]);
    // }
    // printf("\n");

    /* Check against target */
    if (memcmp(work, target_cipher, BLOCK_SIZE * 2) == 0) {
        printf("✔\n");
    } else {
        printf("✘\n");
    }

    // /* Now decrypt to prove it's reversible */
    // feistel_decrypt(work + BLOCK_SIZE);
    // feistel_decrypt(work);
    // printf("After decryption: %.*s\n", BLOCK_SIZE * 2, work);

    return 0;
}
