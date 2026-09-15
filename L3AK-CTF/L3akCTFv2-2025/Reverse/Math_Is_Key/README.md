# Math Is Key

- **Author:** brew
- **Category:** Reverse
- **Solves:** 33

## Description

I think reverse engineering is too hard of a category. How about we do some math problems instead? To speed up my checker, I made sure to use -O3 -flto for maximum performance, enjoy! Author: brew [final](<https://ctf.l3ak.team/files/4eb448b94212cb45491e154e684eb97a/final?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjI5fQ.aHGqfA.kBpcO12QdS5iXtDvWZ_XGbJn7_w>)
final.zip

---

# Summary

Math is key is a simple number checker implemented in C. It performs basic arithmetic but with a twist: the addition, multiplication, etc are all done *very* inefficiently and are all overly complex. Along with this, they are also inlined and optimized, making it even more painful to reverse engineer.

# Solve

The binary is extremely complex, so actually reverse engineering it would be extremely tedious. Using debugging, you can gain data points for the inputs outputs. For the first key, we can set a breakpoint at the comparison and view what our modified input is. Here are some inputs and outputs:

```
123, 0x1fca527
789, 0x1FCA7C1
545, 0x1FCA6CD
```

Then we can use `sympy` to find a corresponding equation:

```python
from sympy import symbols, interpolate
from sympy import simplify

data = [(123, 0x1FCA527), (789, 0x1FCA7C1), (545, 0x1FCA6CD)]
x = symbols('x')
poly = interpolate(data, x)
print("Simplified:", simplify(poly))
```

This outputs `x + 33334444`, this means that we can satisfy the condition check by subtracting `33334444` from `0x1538BEBAD` (what our modified input is compared against) we get our input. Repeat this for the second key, with the inputs/outputs of:

```
123, -0x581fa8a81609
456, -0x581fa8a81222
789, -0x581fa8a80e3b
101112, -0x581fa8a37692
```

This can be solved with the previous equation finder, yielding `3*x - 96892996818810`. So `x*3-96892996818810=12` where 12 is the constant our modified input is compared against. We can transform this into `(12+96892996818810)/3=x`, so `32297665606274` is our input. The next key is a bit different, you can find through debugging it's performing a simple add operation. Treating these as unsigned integers it's essentially `(x+9371337133713371337)=9696421969563673637` solving we get `x=325084835850302300`. The next key is easy to find via debugging, all you have to do is set breakpoints at comparisons that may lead to "wrong" being displayed between the third key and the fourth key. You will find it is just a bunch of modulos needing to result in 0. It is performed with 7, 857, 2837, and 19843, with the input needing to be under 1000000000000. You can find it with:

```python
from math import prod

primes = [7, 857, 2837, 19843]
lcm = prod(primes)
```

This results in `337711251409`. The last check is just a comparison against `0x14feb1657751986`... sorry. With that we have our input:

```
5663311617
32297665606274
325084835850302300
337711251409
94552598387169670
```

And that yields:

```
Congrats! To decode the flag, please run the following: python -c "a=56633116173229766560627432508483585030230033771125140994552598387169670804300; print(a.to_bytes(32, 'little'))"
```

Running that gets us:

```
b'L3AK{w31c0m3_b4cK_t0_m4th_cl455}'
```
