#!/usr/bin/env python3
import struct
import heapq
import sys

def read_userdb(path='user.db'):
    with open(path, 'rb') as f:
        size1 = struct.unpack('<Q', f.read(8))[0]
        vertical = list(struct.unpack(f'<{size1}i', f.read(4*size1)))
        size2 = struct.unpack('<Q', f.read(8))[0]
        horizontal = list(struct.unpack(f'<{size2}i', f.read(4*size2)))
        lax = struct.unpack('<i', f.read(4))[0]
    return vertical, horizontal, lax

def build_binary_matrix(horiz, vert):
    n = len(horiz)
    r = horiz[:]  
    c = vert[:]
    M = [[0]*n for _ in range(n)]

    heap = [(-r_i, i) for i, r_i in enumerate(r)]
    heapq.heapify(heap)

    while heap:
        negri, i = heapq.heappop(heap)
        ri = -negri
        if ri == 0:
            continue

        cols = sorted(range(n), key=lambda j: -c[j])[:ri]
        for j in cols:
            M[i][j] = 1
            c[j] -= 1

    return M

def write_ppm(M, out_path='out.ppm', inlier_val=128, outlier_val=0):
    n = len(M)
    with open(out_path, 'w') as img:
        img.write('P3\n')
        img.write(f'{n} {n}\n')
        for i in range(n):
            row = M[i]
            line = []
            for bit in row:
                v = inlier_val if bit else outlier_val
                line.append(f'{v} {v} {v}')
            img.write(' '.join(line) + '\n')

def main():
    vert, horiz, lax = read_userdb()
    M = build_binary_matrix(horiz, vert)
    write_ppm(M, out_path='attack.ppm')

if __name__ == '__main__':
    main()

