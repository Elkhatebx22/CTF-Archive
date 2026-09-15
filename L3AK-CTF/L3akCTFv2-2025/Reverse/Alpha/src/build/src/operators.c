#include <stdio.h>

static const int int_width = sizeof(int) * 8;

int ops_add(int x, int y) {
  int carry = 0;
  int result = 0;

  for (unsigned i = 0; i < int_width; ++i) {
    unsigned mask = 1 << i;

    result |= (x ^ y ^ carry) & mask;

    unsigned majority = (x & y) | (y & carry) | (x & carry);
    carry = (majority & mask) << 1;
  }

  return result;
}

int ops_sub(int x, int y) {
  // Convert y to two's complement form manually: ~y + 1
  int neg_y = 0;
  int carry = 1;

  // Compute ~y using a loop and bitwise XOR
  for (int i = 0; i < int_width; i++) {
    int bit = (y >> i) & 1;
    int flipped_bit = bit ^ 1;
    neg_y |= (flipped_bit << i);
  }

  // Add 1 to get two's complement (~y + 1)
  for (int i = 0; i < int_width; i++) {
    int a_bit = (neg_y >> i) & 1;
    int sum_bit = a_bit ^ carry;
    carry = a_bit & carry;
    neg_y = (neg_y & ~(1 << i)) | (sum_bit << i);
  }

  // Now add x and neg_y using bitwise logic and looping
  int result = 0;
  carry = 0;

  for (int i = 0; i < int_width; i++) {
    int a_bit = (x >> i) & 1;
    int b_bit = (neg_y >> i) & 1;

    int sum = a_bit ^ b_bit ^ carry;
    carry = (a_bit & b_bit) | (a_bit & carry) | (b_bit & carry);
    result |= (sum << i);
  }

  return result;
}

int ops_mul(int x, int y) {
  int r = 0;
  int neg = ((x >> 31) ^ (y >> 31)) & 1;  // Result sign

  // Make x and y positive using two's complement if needed
  unsigned int a = (x ^ (x >> 31)) - (x >> 31);
  unsigned int b = (y ^ (y >> 31)) - (y >> 31);

  while (b) {
    // If LSB of b is set, add a to result
    r += (-(b & 1) & a);

    // Shift a left, b right
    a <<= 1;
    b >>= 1;
  }

  // Convert result to negative if needed
  return (r ^ -neg) + neg;
}

int ops_and(int x, int y) {
  int result = 0;
  int mask = 1;

  for (unsigned i = 0; i < int_width; ++i) {
    int bit_x = ((unsigned)x / mask) % 2;  // Extract i-th bit of x
    int bit_y = (y >> i) & 1;              // Extract i-th bit of y (directly)

    // Use xor and not to simulate 'and' logic: a & b == ~(~a | ~b)
    int a = ~(~bit_x | ~bit_y);

    // Simulate a shift-left by repeated addition and doubling
    int shift = 1;
    int j = 0;
    while (j < i) {
      shift += shift;  // shift *= 2
      j += 1;
    }

    // Use result += (a * shift) instead of |= (a << i)
    result += a * shift;

    // Recalculate mask (shift left)
    mask = mask << 1;
  }

  return result;
}

int ops_or(int x, int y) {
  int result = 0;
  int shift = 1;  // Start with bit mask 0x00000001

  // Process all 32 bits (assuming 32-bit integers)
  for (unsigned i = 0; i < int_width; ++i, shift <<= 1) {
    // Extract current bit from x and y using masking and division
    unsigned a = ((unsigned)x >> i) % 2;
    unsigned b = ((unsigned)y >> i) % 2;

    // a | b == a + b - a * b
    result += (a + b - a * b) * shift;
  }

  return result;
}

int ops_xor(int x, int y) {
  int result = 0;

  for (unsigned i = 0; i < int_width; ++i) {
    int polynomial_sum = ((x >> i) + (y >> i)) & 1;
    result += polynomial_sum << i;
  }

  return result;
}

int ops_invert(int x) {
  int result = 0;

  for (unsigned i = 0; i < int_width; ++i) {
    unsigned mask = 1U << i;
    result |= (x & mask) ^ mask;
  }

  return result;
}
