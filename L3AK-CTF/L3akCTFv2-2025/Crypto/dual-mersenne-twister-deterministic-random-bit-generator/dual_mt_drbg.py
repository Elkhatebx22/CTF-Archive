from random import Random
from flag import FLAG
import os
r1 = Random()
r1.seed(os.urandom(32))
r2 = Random()
r2.seed(os.urandom(32))


print("Dual Mersenne Twister Deterministic Random Bit Generator")
num_words = int(input("n="))
if num_words > 100000:
    print("Network bandwidth doesnt grow on trees!")
    exit(1)

L = []
for i in range(num_words):
    v1 = r1.getrandbits(32)
    v2 = r2.getrandbits(32)
    # break symmetry by rotating v2
    L.append((v1 + (v2 ^ ((v2 >> 1) | (v2 & 1) << 31))) & 0xffffffff)
print("L="+str(L))

print("Recover the states of r1 and r2 to get the flag.")
print("Enter the next 624 outputs of r1:")
for i in range(624):
    v1 = int(input("v1="))
    if v1 != r1.getrandbits(32):
        print("Incorrect guess")
        exit(1)

print("Now enter the next 624 outputs of r2:")
for i in range(624):
    v2 = int(input("v2="))
    if v2 != r2.getrandbits(32):
        print("Incorrect guess")
        exit(1)

print("Congratulations, here is the flag:", FLAG)