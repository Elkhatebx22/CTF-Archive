#include <errno.h>
#include <fcntl.h>
#include <stddef.h>
#include <unistd.h>

#define FLAG_PATH "/run/commonplace-final/flag"

static int write_all(int descriptor, const char *buffer, size_t length) {
  while (length > 0) {
    ssize_t written = write(descriptor, buffer, length);
    if (written < 0) {
      if (errno == EINTR) continue;
      return -1;
    }
    buffer += written;
    length -= (size_t)written;
  }
  return 0;
}

int main(void) {
  char buffer[512];
  int descriptor = open(FLAG_PATH, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
  if (descriptor < 0) return 1;

  int ended_with_newline = 0;
  for (;;) {
    ssize_t count = read(descriptor, buffer, sizeof(buffer));
    if (count == 0) break;
    if (count < 0) {
      if (errno == EINTR) continue;
      close(descriptor);
      return 1;
    }
    ended_with_newline = buffer[count - 1] == '\n';
    if (write_all(STDOUT_FILENO, buffer, (size_t)count) < 0) {
      close(descriptor);
      return 1;
    }
  }

  close(descriptor);
  if (!ended_with_newline && write_all(STDOUT_FILENO, "\n", 1) < 0) return 1;
  return 0;
}
