#include <stdio.h>
#include <string.h>
#include <stdbool.h>


void rc4_encrypt(unsigned char *plaintext, int plaintext_len, unsigned char *key, int key_len, unsigned char *ciphertext) {
    unsigned char S[256];
    for (int i = 0; i < 256; i++) {
        S[i] = i;
    }

    int j = 0;
    for (int i = 0; i < 256; i++) {
        j = (j + S[i] + key[i % key_len]) % 256;
        unsigned char temp = S[i];
        S[i] = S[j];
        S[j] = temp;
    }

    int i = 0;
    j = 0;
    for (int index = 0; index < plaintext_len; index++) {
        i = (i + 1) % 256;
        j = (j + S[i]) % 256;
        unsigned char temp = S[i];
        S[i] = S[j];
        S[j] = temp;
        int k = S[(S[i] + S[j]) % 256];
        ciphertext[index] = plaintext[index] ^ k;
    }
}
char Read (char* c){
printf("MEOW ₍^. .^₎⟆\n");
    return c;
}
int main() {
    char plaintext[256];
    Read(plaintext);
    int plaintext_len = strlen(plaintext);
    unsigned char key[] = "I_L0v3_UnP4ck1ng";
    int key_len = strlen(key);
    unsigned char ciphertext[plaintext_len];
    int ciphertext_len = strlen(ciphertext);
    rc4_encrypt(plaintext, plaintext_len, key, key_len, ciphertext);
    bool correct_flag = false;
    unsigned char correct[]={0x4b,0xb0,0xe2,0x2d,0xae,0xac,0xcc,0x60,0x5b,0x6b,0x93,0xf7,0x1d,0xfe,0xa0,0xe5,0xe6,0xb3,0xeb,0xc0,0x9b,0x83,0x35,0x85,0xa5,0x77,0xd9,0x57,0xa6,0xdf,0xa4,0xea,0xe5,0xdd,0xf8};
    for (int i = 0; i < ciphertext_len; i++) {
        if (ciphertext[i] != correct[i]) {
            correct_flag = false;
        }
        else {
            correct_flag = true;
        }
    }
    if (correct_flag) {
        printf("Correct\n");
    }
    return 0;

}