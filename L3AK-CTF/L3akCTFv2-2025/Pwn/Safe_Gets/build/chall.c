#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int main(){
    char buf[0x100];
    gets(buf);

    int len = strlen(buf);
    for (size_t i = 0; i < len/2; i++)
    {
        char temp = buf[len - 1 - i];
        buf[len - 1 - i] = buf[i];
        buf[i] = temp;
    }
    puts("Reversed string:");
    puts(buf);
}

void win(){
    system("/bin/sh");
}
