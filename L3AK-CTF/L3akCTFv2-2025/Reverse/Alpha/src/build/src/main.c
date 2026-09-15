#define _GNU_SOURCE
#include <setjmp.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
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
  bool is_system_satisfied = true;
  char x[64];

  printf(USER_PROMPT);
  fgets(x, sizeof(x), stdin);

  is_system_satisfied &= ops_mul(ops_xor(ops_or(x[13], x[12]), x[0]), x[9]) == 4902;
  is_system_satisfied &= ops_xor(ops_sub(ops_or(x[14], x[10]), x[22]), x[20]) == -64;
  is_system_satisfied &= ops_sub(ops_sub(ops_xor(x[7], x[10]), x[12]), x[2]) == -71;
  is_system_satisfied &= ops_mul(ops_and(ops_xor(x[20], x[7]), x[16]), x[11]) == 8930;
  is_system_satisfied &= ops_mul(ops_xor(ops_mul(x[1], x[8]), x[15]), x[7]) == 278822;
  is_system_satisfied &= ops_or(ops_xor(ops_xor(x[22], x[1]), x[8]), x[20]) == 115;
  is_system_satisfied &= ops_xor(ops_add(ops_or(x[18], x[20]), x[11]), x[1]) == 229;
  is_system_satisfied &= ops_and(ops_mul(ops_mul(x[13], x[0]), x[4]), x[21]) == 80;
  is_system_satisfied &= ops_xor(ops_xor(ops_add(x[4], x[12]), x[6]), x[22]) == 140;
  is_system_satisfied &= ops_and(ops_and(ops_sub(x[17], x[19]), x[3]), x[6]) == 0;
  is_system_satisfied &= ops_mul(ops_add(ops_xor(x[3], x[2]), x[18]), x[5]) == 6560;
  is_system_satisfied &= ops_add(ops_and(ops_mul(x[18], x[0]), x[6]), x[14]) == 64;
  is_system_satisfied &= ops_and(ops_or(ops_and(x[2], x[2]), x[4]), x[5]) == 82;
  is_system_satisfied &= ops_sub(ops_mul(ops_xor(x[0], x[9]), x[12]), x[15]) == 1996;
  is_system_satisfied &= ops_xor(ops_add(ops_mul(x[17], x[12]), x[21]), x[11]) == 8692;
  is_system_satisfied &= ops_xor(ops_add(ops_and(x[22], x[12]), x[22]), x[17]) == 173;
  is_system_satisfied &= ops_mul(ops_and(ops_xor(x[23], x[16]), x[23]), x[17]) == 105;
  is_system_satisfied &= ops_sub(ops_and(ops_sub(x[2], x[0]), x[1]), x[21]) == -65;
  is_system_satisfied &= ops_mul(ops_xor(ops_mul(x[14], x[22]), x[0]), x[2]) == 475020;
  is_system_satisfied &= ops_sub(ops_mul(ops_sub(x[4], x[15]), x[18]), x[20]) == 859;
  is_system_satisfied &= ops_mul(ops_mul(ops_sub(x[1], x[8]), x[5]), x[1]) == 12546;
  is_system_satisfied &= ops_sub(ops_add(ops_sub(x[14], x[16]), x[3]), x[6]) == -38;
  is_system_satisfied &= ops_and(ops_and(ops_xor(x[23], x[21]), x[21]), x[11]) == 2;
  is_system_satisfied &= ops_sub(ops_add(ops_and(x[23], x[13]), x[19]), x[6]) == 99;
  is_system_satisfied &= ops_xor(ops_xor(ops_add(x[11], x[23]), x[16]), x[4]) == 217;
  is_system_satisfied &= ops_add(ops_xor(ops_mul(x[13], x[13]), x[3]), x[8]) == 13666;
  is_system_satisfied &= ops_or(ops_xor(ops_and(x[21], x[15]), x[1]), x[8]) == 113;
  is_system_satisfied &= ops_xor(ops_sub(ops_and(x[14], x[15]), x[2]), x[11]) == -96;

  if (is_system_satisfied) {
    puts(SUCCESS);
  } else {
    puts(FAILURE);
  }

  return 0;
}
