#include <stdio.h>
#include <assert.h>
#include <limits.h>

#include "operators.h"

void test_add()
{
    assert(ops_add(1, 1) == 2);
    assert(ops_add(123, 456) == 579);
    assert(ops_add(1000, 2000) == 3000);

    assert(ops_add(-1, -1) == -2);
    assert(ops_add(-100, -200) == -300);
    assert(ops_add(-500, 200) == -300);
    assert(ops_add(500, -200) == 300);

    assert(ops_add(0, 0) == 0);
    assert(ops_add(0, 123) == 123);
    assert(ops_add(123, 0) == 123);
    assert(ops_add(0, -456) == -456);
    printf("All ADD (+) tests passed!\n");
}

void test_sub()
{
    // Basic positive cases
    assert(ops_sub(5, 3) == 2);
    assert(ops_sub(10, 0) == 10);
    assert(ops_sub(0, 10) == -10);
    assert(ops_sub(1000, 1000) == 0);

    // Negative numbers
    assert(ops_sub(-5, -3) == -2);
    assert(ops_sub(-3, -5) == 2);
    assert(ops_sub(-10, 5) == -15);
    assert(ops_sub(5, -10) == 15);

    // Mixed signs
    assert(ops_sub(0, -1) == 1);
    assert(ops_sub(-1, 0) == -1);
    assert(ops_sub(1, -1) == 2);
    assert(ops_sub(-1, 1) == -2);

    // Edge cases
    assert(ops_sub(INT_MAX, 0) == INT_MAX);
    assert(ops_sub(INT_MIN, 0) == INT_MIN);
    assert(ops_sub(INT_MAX, INT_MAX) == 0);
    assert(ops_sub(INT_MIN, INT_MIN) == 0);

    printf("All SUB (-) tests passed!\n");
}

void test_mul()
{
    // Basic positive tests
    assert(ops_mul(2, 3) == 6);
    assert(ops_mul(5, 1) == 5);
    assert(ops_mul(7, 0) == 0);
    assert(ops_mul(0, 7) == 0);
    assert(ops_mul(1, 1) == 1);

    // Negative and mixed sign tests
    assert(ops_mul(-2, 3) == -6);
    assert(ops_mul(2, -3) == -6);
    assert(ops_mul(-2, -3) == 6);
    assert(ops_mul(0, -10) == 0);
    assert(ops_mul(-10, 0) == 0);

    // Tests with INT_MAX and INT_MIN
    assert(ops_mul(INT_MAX, 1) == INT_MAX);
    assert(ops_mul(1, INT_MAX) == INT_MAX);
    assert(ops_mul(INT_MIN, 1) == INT_MIN);
    assert(ops_mul(1, INT_MIN) == INT_MIN);
    assert(ops_mul(0, INT_MAX) == 0);
    assert(ops_mul(0, INT_MIN) == 0);

    // Larger and symmetric numbers
    assert(ops_mul(1000, 1000) == 1000000);
    assert(ops_mul(-1000, 1000) == -1000000);
    assert(ops_mul(1000, -1000) == -1000000);
    assert(ops_mul(-1000, -1000) == 1000000);

    // Edge case: multiplying by -1
    assert(ops_mul(-1, 1234) == -1234);
    assert(ops_mul(1234, -1) == -1234);
    assert(ops_mul(-1, -1234) == 1234);

    printf("All MUL (*) tests passed.\n");
}

void test_and()
{
    // Basic cases
    assert(ops_and(0, 0) == 0);
    assert(ops_and(1, 0) == 0);
    assert(ops_and(0, 1) == 0);
    assert(ops_and(1, 1) == 1);
    assert(ops_and(5, 3) == (5 & 3));   // 0101 & 0011 = 0001
    assert(ops_and(7, 15) == (7 & 15)); // 0111 & 1111 = 0111

    // Identity and zero
    assert(ops_and(0xFFFFFFFF, 0) == 0);
    assert(ops_and(0, 0xFFFFFFFF) == 0);
    assert(ops_and(0xFFFFFFFF, 0xFFFFFFFF) == 0xFFFFFFFF);

    // Negative numbers
    assert(ops_and(-1, 0) == 0);
    assert(ops_and(-1, -1) == -1);
    assert(ops_and(-1, 0x12345678) == 0x12345678);
    assert(ops_and(-123, 456) == (-123 & 456));

    // Edge cases with INT_MIN and INT_MAX
    assert(ops_and(INT_MAX, INT_MAX) == INT_MAX);
    assert(ops_and(INT_MIN, INT_MIN) == INT_MIN);
    assert(ops_and(INT_MIN, INT_MAX) == 0);
    assert(ops_and(INT_MIN, -1) == INT_MIN);
    assert(ops_and(INT_MAX, -1) == INT_MAX);

    // Patterned values
    assert(ops_and(0xAAAAAAAA, 0x55555555) == 0x00000000); // alternating bits
    assert(ops_and(0xAAAAAAAA, 0xFFFFFFFF) == 0xAAAAAAAA);
    assert(ops_and(0x55555555, 0xFFFFFFFF) == 0x55555555);
    assert(ops_and(0x12345678, 0xFFFFFFFF) == 0x12345678);

    printf("All AND (&) tests passed!\n");
}

void test_or()
{
    // Zero cases
    assert(ops_or(0, 0) == (0 | 0));
    assert(ops_or(0, 1) == (0 | 1));
    assert(ops_or(1, 0) == (1 | 0));

    // One-bit overlaps
    assert(ops_or(1, 2) == (1 | 2));
    assert(ops_or(2, 4) == (2 | 4));
    assert(ops_or(8, 16) == (8 | 16));

    // Same numbers
    assert(ops_or(5, 5) == (5 | 5));
    assert(ops_or(-7, -7) == (-7 | -7));

    // Opposite bits
    assert(ops_or(0x0F, 0xF0) == (0x0F | 0xF0)); // 00001111 | 11110000 = 11111111

    // All 1s and 0s
    assert(ops_or(INT_MAX, 0) == (INT_MAX | 0));
    assert(ops_or(0, INT_MIN) == (0 | INT_MIN));
    assert(ops_or(INT_MAX, INT_MIN) == (INT_MAX | INT_MIN));

    // Negative values
    assert(ops_or(-1, 0) == (-1 | 0));
    assert(ops_or(-1, 1) == (-1 | 1));
    assert(ops_or(-2, 3) == (-2 | 3));
    assert(ops_or(-128, 127) == (-128 | 127));

    // Edge combinations
    assert(ops_or(0xAAAA5555, 0x5555AAAA) == (0xAAAA5555 | 0x5555AAAA));
    assert(ops_or(0xFFFFFFFF, 0x00000000) == (0xFFFFFFFF | 0x00000000));
    assert(ops_or(0x12345678, 0x87654321) == (0x12345678 | 0x87654321));

    // Random values
    assert(ops_or(42, 21) == (42 | 21));
    assert(ops_or(100, 200) == (100 | 200));
    assert(ops_or(0xDEADBEEF, 0xBEEFDEAD) == (0xDEADBEEF | 0xBEEFDEAD));

    printf("All OR  (~) tests passed!\n");
}

void test_xor()
{
    assert(ops_xor(0, 0) == 0);
    assert(ops_xor(0, 1) == 1);
    assert(ops_xor(1, 0) == 1);
    assert(ops_xor(1, 1) == 0);

    assert(ops_xor(42, 42) == 0);
    assert(ops_xor(-7, -7) == 0);

    assert(ops_xor(0xAAAAAAAA, 0x55555555) == 0xFFFFFFFF);

    assert(ops_xor(0x12345678, 0xFFFFFFFF) == ~0x12345678);
    assert(ops_xor(ops_xor(0x12345678, 0xFFFFFFFF), 0xFFFFFFFF) == 0x12345678);

    assert(ops_xor(5, 9) == ops_xor(9, 5));

    int a = 12, b = 25, c = 37;
    assert(ops_xor(ops_xor(a, b), c) == ops_xor(a, ops_xor(b, c)));

    assert(ops_xor(INT_MAX, 0) == INT_MAX);
    assert(ops_xor(INT_MIN, 0) == INT_MIN);
    assert(ops_xor(INT_MAX, INT_MAX) == 0);
    assert(ops_xor(INT_MIN, INT_MIN) == 0);
    assert(ops_xor(INT_MAX, INT_MIN) == (INT_MAX ^ INT_MIN));

    assert(ops_xor(-1, 1) == -2);
    assert(ops_xor(-5, -10) == (-5 ^ -10));

    assert(ops_xor(0xFFFFFFFF, 0x00000000) == 0xFFFFFFFF);
    assert(ops_xor(0xFFFFFFFF, 0xFFFFFFFF) == 0x00000000);

    printf("All XOR (^) tests passed!\n");
}

void test_invert()
{
    // Test 0
    assert(ops_invert(0) == -1);

    // Test positive integers
    assert(ops_invert(1) == -2);
    assert(ops_invert(2) == -3);
    assert(ops_invert(10) == -11);
    assert(ops_invert(12345) == -12346);

    // Test negative integers
    assert((ops_invert(-1)) == 0);
    assert((ops_invert(-2)) == 1);
    assert((ops_invert(-10)) == 9);
    assert((ops_invert(-12345)) == 12344);

    assert(ops_invert(0x55555555) == 0xAAAAAAAA);
    assert(ops_invert(0xFFFFFFFF) == 0);
    assert(ops_invert(0) == 0xFFFFFFFF);

    printf("All NOT (~) tests passed!\n");
}

int main()
{
    test_add();
    test_sub();
    test_mul();
    test_and();
    test_or();
    test_xor();
    test_invert();
    printf("All tests passed!\n");
    return 0;
}
