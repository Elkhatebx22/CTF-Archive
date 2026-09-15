#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int registering_enabled = 1;
int str_to_int (char* chars) {
    int result = 0;
    while (*chars) {
        result = result * 10 + (*chars - 0x30); // 0x30 is the offset at which the ascii values for integers start
        chars++;
    }
    return result;
}

int parse_line (char tmp_cur_line[], unsigned char image[500][500][3], int cur_line) {
    /* This is possibly, the worst code, I have ever written. It is so 
     * unoptomized, complex, and redudent that it makes me want to scream.
     * But, if I touch it, it will break, so I am leaving it be. It works
     * but I am ashamed. I am also sorry for whoever is going to reverse 
     * this, hopefully they find it to just be converting strings to integers
     * in an overly complex way. Again, I am sorry, I wish I was better 
     * at coding. I spent 3 hours on this function. There were (and probably
     * are) still so many bugs. Will this crash if unexpected data is put 
     * into it? Hell yeah it will. But, this is a CTF challenge, so I will
     * not waste an additional hour securing it. */
    int index = 0; // for image
    int index_cur = 0; // for tmp_cur_line
    int char_count = 0;
    int cur_pixel = 0; // for the current pixel
    char tmp_chars[4] = {0}; // extra char full null byte, used by str_to_int
    char a[] = " ";
    if (tmp_cur_line[strlen(tmp_cur_line)-1] != ' ') {
        tmp_cur_line[strlen(tmp_cur_line)-1] = ' ';
    }
    while (index < 500) {
        while (cur_pixel < 3) {
            if ((char_count > 3) && !(tmp_cur_line[index_cur+char_count] == 0)) {
                printf("Parsing error at line %d, real index %d, pixel index %d, current rgb %d, currently pointing at %d/%c\n", cur_line, index_cur, index, cur_pixel, tmp_cur_line[index_cur+char_count], tmp_cur_line[index_cur+char_count]);
                exit(-1);
            }
            if (tmp_cur_line[index_cur+char_count] == ' ' || tmp_cur_line[index_cur+char_count] == 0) { // an idiot admires complexity, luckily I don't, the code is just complex because I'm bad at coding
                tmp_cur_line[index_cur+char_count] = 0;
                strcpy(tmp_chars, (tmp_cur_line+index_cur));
                image[cur_line][index][cur_pixel] = str_to_int(tmp_chars); // I realized this could have been way simpler by not grouping these into pixels but I already implemented it
                cur_pixel++; // also wrong! this should be rgb, the index specifies the pixel value. I am not renaming out of sheere lazyness
                index_cur = index_cur+char_count+1;
                char_count = -1;
            }
            char_count++;
        }
        index++;
        cur_pixel = 0;
    }
    return 0;
}

int comp (const void * elem1, const void * elem2) { // copy and pasted off of stack overflow
    int f = *((unsigned char*)elem1);
    int s = *((unsigned char*)elem2);
    if (f > s) return  1;
    if (f < s) return -1;
    return 0;
}
int hacky_hacks () {
    while (1) {
        printf("Please enter y to continue\n");
        if (getchar() == 'y') {
            return 0;
        }   
    }
}
int main_but_better (int registering) {
    printf("Please input an image in PPM format (ascii)\n");
    char header[100] = {0};
    fgets(header, 5, stdin);
    if (strncmp(header, "P3", 2)) {
        printf("Wrong header! Please use ppm\n");
        return -1;
    }
    fgets(header, 10, stdin);
    if (strncmp(header, "500 500", 7)) {
        printf("Sorry, only 500 by 500 images are supported\n");
        return -1;
    }
    unsigned char image[500][500][3] = {0};
    char tmp_cur_line[500*15] = {0};
    for (int i = 0; i < 500; i++) {
        fgets(tmp_cur_line, 500*15, stdin); 
        parse_line(tmp_cur_line, image, i); // An aditional check was planned to normalize pixels/rgb values seperated by more than one whitespace. For reasons stated in the function comment I will not be doing that.
    }
    // the following will check all pixels outside of a 288 by 339 oval (with the middle in 0, 0)
    unsigned char memory_eater_nom_nom[500*500] = {0};
    int krill = 0;
    for (int y = 0; y < 500; y++) {
        for (int x = 0; x < 500; x++) {
            if ((28900*((x-250)*(x-250))+20736*((y-250)*(y-250)) > 598790400) && y > 150) { // the y > 150 makes sure we don't include the body when finding the bounds
                memory_eater_nom_nom[krill] = (image[y][x][0] + image[y][x][1] + image[y][x][2])/3; // brightness
                krill++;
            }
        }
    }
    qsort(memory_eater_nom_nom, krill, sizeof(*memory_eater_nom_nom), comp);
    unsigned int n = krill;
    if ( n % 2 == 0) {
        n--; // :)
    }
    unsigned int median = memory_eater_nom_nom[n/2 + 1];
    unsigned int q1 = n/2;
    if ( q1 % 2 == 0) {
        q1--;
    }
    unsigned int q3 = memory_eater_nom_nom[q1+(q1/2)];
    q1 = memory_eater_nom_nom[q1/2];
    unsigned int iqr = q3 - q1;
    unsigned int upper_fence = q3 + (iqr + (iqr/2));
    unsigned int lower_fence = q1 - (iqr + (iqr/2));
    if ((int)lower_fence < 0) {
        lower_fence = 0;
    }
    int horizantal_sums[500] = {0};
    memset(memory_eater_nom_nom, 0, sizeof(memory_eater_nom_nom));
    int temp = 0;
    for (int y = 0; y < 500; y++) {
        for (int x = 0; x < 500; x++) {
            if (1) {// ((28900*((x-250)*(x-250))+20736*((y-250)*(y-250)) <= 598790400)) { // this is worse, actually, idk why tho
                temp = (image[y][x][0] + image[y][x][1] + image[y][x][2])/3;
                if (temp < upper_fence && temp > lower_fence) {
                    temp = 1;
                } else {
                    temp = 0;
                }
            } else {
                temp = 1;
            }
            horizantal_sums[y]+=temp;
        }
    }
    memset(memory_eater_nom_nom, 0, sizeof(memory_eater_nom_nom));
    int vertical_sums[500] = {0};
    memset(memory_eater_nom_nom, 0, sizeof(memory_eater_nom_nom));
    temp = 0;
    for (int x = 0; x < 500; x++) {
        for (int y = 0; y < 500; y++) {
            if (1) {// ((28900*((x-250)*(x-250))+20736*((y-250)*(y-250)) <= 598790400)) { // this is worse, actually, idk why tho
                temp = (image[y][x][0] + image[y][x][1] + image[y][x][2])/3;
                if (temp < upper_fence && temp > lower_fence) {
                    temp = 1;
                } else {
                    temp = 0;
                }
            } else {
                temp = 1;
            }
            vertical_sums[y]+=temp;
        }
    }
    memset(memory_eater_nom_nom, 0, sizeof(memory_eater_nom_nom));

    if (registering && registering_enabled) {
        size_t size1 = sizeof(vertical_sums) / sizeof(vertical_sums[0]);
        size_t size2 = sizeof(horizantal_sums) / sizeof(horizantal_sums[0]);

        FILE *f = fopen("user.db", "wb");

        fwrite(&size1, sizeof(size1), 1, f); // write length of array1
        fwrite(vertical_sums, sizeof(int), size1, f);

        fwrite(&size2, sizeof(size2), 1, f); // write length of array2
        fwrite(horizantal_sums, sizeof(int), size2, f);
        int qwe = 0;
        hacky_hacks();
        printf("How lax do you want the login to be? \n");
        scanf("%d", &qwe);
        fwrite(&qwe, sizeof(qwe), 1, f);
        fclose(f);
        printf("Registration successful! Please log in...\n");
        return 0;
    }
    if (!registering) {
        FILE *f = fopen("user.db", "rb");
        if (!f) { perror("fopen"); return -1; }
    
        size_t stored_n1, stored_n2;
        fread(&stored_n1, sizeof(stored_n1), 1, f);
        int *sv = malloc(stored_n1 * sizeof *sv);
        fread(sv, sizeof *sv, stored_n1, f);
    
        fread(&stored_n2, sizeof(stored_n2), 1, f);
        int *sh = malloc(stored_n2 * sizeof *sh);
        fread(sh, sizeof *sh, stored_n2, f);
    
        int lax;
        fread(&lax, sizeof lax, 1, f);
        fclose(f);
    
        // assume size1 == stored_n1 and size2 == stored_n2
        int ok = 1;
        for (size_t i = 0; i < stored_n1; i++) {
            printf("Vertical sum %d is %d needs to be %d\n", i, vertical_sums[i], sv[i]);
            if (abs(vertical_sums[i] - sv[i]) > lax) { ok = 0; }
        }
        for (size_t i = 0; ok && i < stored_n2; i++) {
            printf("Horizantal sum %d is %d needs to be %d\n", i, horizantal_sums[i], sv[i]);
            if (abs(horizantal_sums[i] - sh[i]) > lax) { ok = 0; }
        }
    
        free(sv);
        free(sh);
    
        if (ok) {
            FILE *fp2 = fopen("flag.txt", "r");
            int c;
            while ((c = fgetc(fp2)) != EOF) {
                putchar(c);
            }
            fclose(fp2);
            fflush(stdout);
            return 0;
        } else {
            printf("Login failed: sums out of ±%d range.\n", lax);
            return -1;
        }
    }
}

int main () {
    printf("Registration disabled, defaulting to login...\n");
    main_but_better(0);
}
