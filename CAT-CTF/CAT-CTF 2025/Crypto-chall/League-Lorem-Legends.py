from Crypto.Util.number import bytes_to_long, getPrime
import gmpy2


flag = b'CATF{redacted}'



e = getPrime(128)
p = getPrime(1024)
q = getPrime(1024)
n = p * q
c = pow(bytes_to_long(flag), e, n)

d = pow(e, -1, (p - 1) * (q - 1))
dp = d % (p - 1)
dp_big = dp >> 205

print(f"{n = }")
print(f"{e = }")
print(f"{c = }")
print(f"{dp_big = }")