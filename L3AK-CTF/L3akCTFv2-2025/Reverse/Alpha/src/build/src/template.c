#define _GNU_SOURCE
#include <setjmp.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ucontext.h>

#include "operators.h"

static const volatile unsigned char main_text[2560] = {0};
static int main_cursor = 0;

static const char *USER_PROMPT = "FLAG: ";
static const char *SUCCESS = "Correct!";
static const char *FAILURE = "Incorrect!";

void init() __attribute__((constructor));
int main();

void sigill_handler(int signum, siginfo_t *info, void *ucontext) {
  ucontext_t *ctx = (ucontext_t *)ucontext;
  ctx->uc_mcontext.gregs[REG_RIP] = (unsigned long)main;

  unsigned char *main_function = (void *)main;
  for (unsigned i = 0; i < 64; ++i, ++main_cursor) {
    const unsigned char xored_byte = main_text[main_cursor];
    main_function[i] = main_function[i] ^ xored_byte;
  }

  main_function[64] = 0x37;  // AAA
}

void init() {
  struct sigaction sa = {0};
  sa.sa_sigaction = sigill_handler;
  sigemptyset(&sa.sa_mask);
  sa.sa_flags = SA_SIGINFO;

  sigaction(SIGILL, &sa, NULL);
}

int main() {
  char x[64];
  printf(USER_PROMPT);
  fgets(x, sizeof(x), stdin);
  puts(SUCCESS);
  return 0;
}
