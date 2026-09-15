from hashlib import md5
import itertools

# L3AK{jus7_p4tt3rn_m4tch1ng_4t_f1rs7_bu7_th3n_y0u_n33d_4_h3ur1st1c_t0_n4rr0w_1t_d0wn}
# abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01233456789!_{}

ascii = open("alphabet.txt").readlines()[1:]
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01233456789!_{}"
jumbled = open("../build/flag.txt").readlines()
letters = {}

FLAG_LENGTH = 84

for i in range(len(alphabet)):
    counts = []
    for l in ascii:
        r = l[i*4:(i+1)*4]
        counts.append(r.count('#'))
    letters[alphabet[i]] = counts


jumbled_counts = []
for i in range(FLAG_LENGTH//2):
    rows = jumbled[(i*6)+1:(i+1)*6]
    counts = []
    for r in rows:
        counts.append(r.count('#'))
    jumbled_counts.append(counts)

chunks: list[set[str]] = list()
for chunk in jumbled_counts:
    possible_chunks = set()
    for a in alphabet:
        for b in alphabet:
            a_counts = letters[a]
            b_counts = letters[b]
            sum_counts = []
            for i in range(5):
                sum_counts.append(a_counts[i]+b_counts[i])
            if all(i == j for i, j in zip(sum_counts, chunk)):
                possible_chunks.add(a+b)
    chunks.append(possible_chunks)

def force_substr(index: int, s: str):
    if index < 0:
        index = FLAG_LENGTH + index - len(s) + 1
    to_remove = []
    for i, char in enumerate(s):
        chunk_num = (index+i)//2
        letter_index = (index +i) % 2 
        for c in chunks[chunk_num]:
            if c[letter_index] != char:
                to_remove.append((chunk_num, c))

    for c in to_remove:
        if c[1] in chunks[c[0]]:
            chunks[c[0]].remove(c[1])

i = 1
for chunk in chunks:
    i *= len(chunk)
print(i)

force_substr(0, 'L3AK{')
force_substr(-1, '}')
# force_substr(-1, '_f1rs7_bu7_th3n_y0u_n33d_4_h3ur1st1c_t0_n4rr0w_1t_d0wn}')

i = 1
for chunk in chunks:
    i *= len(chunk)

print(i)

for i in range(2,len(chunks[2:])):
    to_remove = []
    for c in chunks[i]:
        if not all(l.isdigit() or l.islower() or l in '{_}' for l in c):
            to_remove.append(c)
    for c in to_remove:
        chunks[i].remove(c)

# for combo in itertools.product(*chunks):
#     flag = ''.join(combo)
#     print(flag, md5(flag.encode()).hexdigest())
#     if md5(flag.encode()).hexdigest() == "a7bf5f833c3e4ceff2e006ff801ec16b":
#         print("FOUND:", flag)
#         break