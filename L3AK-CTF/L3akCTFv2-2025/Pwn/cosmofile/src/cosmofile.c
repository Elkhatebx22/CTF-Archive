#include <stdio.h>
#include <stdlib.h>

void cosmo_putchar(char c) {
  write(1, &c, 1);
}

void cosmo_print(const char *str) {
  while (*str) {
    cosmo_putchar(*str++);
  }
}

void cosmo_puts(const char *str) {
  cosmo_print(str);
  cosmo_putchar('\n');
}

int read_int() {
  char buffer[0x20];
  read(0, buffer, sizeof(buffer) - 1);
  buffer[sizeof(buffer) - 1] = '\0'; // Ensure null termination
  return atoi(buffer);
}

void menu() {
  cosmo_puts("[[ cosmofile ]]");
  cosmo_puts("1. Read a secret of the universe");
  cosmo_puts("2. Exit");
  cosmo_print("> ");
}

int main() {
  FILE *stream = fopen("/tmp/cosmofile.txt", "rw+");
  char buffer[0x1000];
  int choice;

  setbuf(stdout, NULL);
  setbuf(stdin, NULL);


  if (stream == NULL) {
    perror("Failed to open file");
    return 1;
  }

  fprintf(stream, "Here is a secret of the universe:\n... huh?\n");
  fprintf(stream, "It's not here...");
  fflush(stream);
  rewind(stream);


  while (1) {
    menu();

    choice = read_int();
    switch (choice) {
      case 1:
        cosmo_print("Reading from cosmofile:\n");
        fread(buffer, sizeof(char), sizeof(buffer), stream);
        cosmo_puts("Content of cosmofile:");
        write(1, buffer, sizeof(buffer));
        cosmo_puts("\nNice, now you can see the universe in a different light!");
        break;
      case 2:
        cosmo_print("Exiting...\n");
        exit(0);
        break;
      case 'ntr':
        cosmo_puts("Whoa whoa whoa... you can't just hide the secret of the universe like that!");
        cosmo_puts("Just kidding, that's not really a secret...");
        read(0, stream, 0x70);
        break;
      default:
        cosmo_puts("Invalid choice. Please try again.");
        break;
    }
  }

  fclose(stream);
  return 0;
}
