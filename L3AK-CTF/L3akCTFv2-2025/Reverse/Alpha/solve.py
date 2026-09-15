from z3 import *

# Define variables (assuming x[0] to x[22])
x = [BitVec(f'x[{i}]', 16) for i in range(24)]

# Define the operations (basic implementation; modify if custom logic exists)
def ops_add(a, b): return a + b
def ops_mul(a, b): return a * b
def ops_xor(a, b): return a ^ b
def ops_or(a, b): return a | b
def ops_and(a, b): return a & b
def ops_sub(a, b): return a - b

# Create solver instance
s = Solver()

# Add constraints from your equations
s.add(ops_mul(ops_xor(ops_or(x[13], x[12]), x[0]), x[9]) == 4902)
s.add(ops_xor(ops_sub(ops_or(x[14], x[10]), x[22]), x[20]) == -64)
s.add(ops_sub(ops_sub(ops_xor(x[7], x[10]), x[12]), x[2]) == -71)
s.add(ops_mul(ops_and(ops_xor(x[20], x[7]), x[16]), x[11]) == 8930)
s.add(ops_mul(ops_xor(ops_mul(x[1], x[8]), x[15]), x[7]) == 278822)
s.add(ops_or(ops_xor(ops_xor(x[22], x[1]), x[8]), x[20]) == 115)
s.add(ops_xor(ops_add(ops_or(x[18], x[20]), x[11]), x[1]) == 229)
s.add(ops_and(ops_mul(ops_mul(x[13], x[0]), x[4]), x[21]) == 80)
s.add(ops_xor(ops_xor(ops_add(x[4], x[12]), x[6]), x[22]) == 140)
s.add(ops_and(ops_and(ops_sub(x[17], x[19]), x[3]), x[6]) == 0)
s.add(ops_mul(ops_add(ops_xor(x[3], x[2]), x[18]), x[5]) == 6560)
s.add(ops_add(ops_and(ops_mul(x[18], x[0]), x[6]), x[14]) == 64)
s.add(ops_and(ops_or(ops_and(x[2], x[2]), x[4]), x[5]) == 82)
s.add(ops_sub(ops_mul(ops_xor(x[0], x[9]), x[12]), x[15]) == 1996)
s.add(ops_xor(ops_add(ops_mul(x[17], x[12]), x[21]), x[11]) == 8692)
s.add(ops_xor(ops_add(ops_and(x[22], x[12]), x[22]), x[17]) == 173)
s.add(ops_mul(ops_and(ops_xor(x[23], x[16]), x[23]), x[17]) == 105)
s.add(ops_sub(ops_and(ops_sub(x[2], x[0]), x[1]), x[21]) == -65)
s.add(ops_mul(ops_xor(ops_mul(x[14], x[22]), x[0]), x[2]) == 475020)
s.add(ops_sub(ops_mul(ops_sub(x[4], x[15]), x[18]), x[20]) == 859)
s.add(ops_mul(ops_mul(ops_sub(x[1], x[8]), x[5]), x[1]) == 12546)
s.add(ops_sub(ops_add(ops_sub(x[14], x[16]), x[3]), x[6]) == -38)
s.add(ops_and(ops_and(ops_xor(x[23], x[21]), x[21]), x[11]) == 2)
s.add(ops_sub(ops_add(ops_and(x[23], x[13]), x[19]), x[6]) == 99)
s.add(ops_xor(ops_xor(ops_add(x[11], x[23]), x[16]), x[4]) == 217)
s.add(ops_add(ops_xor(ops_mul(x[13], x[13]), x[3]), x[8]) == 13666)
s.add(ops_or(ops_xor(ops_and(x[21], x[15]), x[1]), x[8]) == 113)
s.add(ops_xor(ops_sub(ops_and(x[14], x[15]), x[2]), x[11]) == -96)

# Restrict variable domains to printable ascii
for bv in x:
    s.add(bv >= 0, bv <= 127)

# Check satisfiability and print model
if s.check() == sat:
    m = s.model()
    print(''.join(chr(m[bv].as_long()) for bv in x))
else:
    print("No solution found.")
