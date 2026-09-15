import numpy as np
import ast
import f2_solve as f2
import sys
from pwn import *


class MT19937:
    w, n, m, r = 32, 624, 397, 31
    a = 0x9908B0DF
    u, d = 11, 0xFFFFFFFF
    s, b = 7, 0x9D2C5680
    t, c = 15, 0xEFC60000
    l = 18
    LMASK = (0xFFFFFFFF >> (w-r)) & 0xFFFFFFFF
    UMASK = (0xFFFFFFFF << r) & 0xFFFFFFFF

    def __init__(self, state_array, k):
        self.state_array = list(state_array)
        assert len(self.state_array) == 624
        self.k = k
    
    def next_uint32(self):
        # this implementation is based on Wikipedia's implementation accessed 07-07-2025
        # with small modifications to make it consistent with python's implementation
        j = self.k + 1
        if j >= MT19937.n:
            j -= MT19937.n
        x = (self.state_array[self.k] & MT19937.UMASK) | (self.state_array[j] & MT19937.LMASK)
        x_a = x >> 1
        if x & 1:
            x_a = x_a ^ MT19937.a
        j = self.k + MT19937.m
        if j >= MT19937.n:
            j -= MT19937.n

        x = (self.state_array[j] ^ x_a) & MT19937.d
        self.state_array[self.k] = x

        self.k += 1
        if self.k >= MT19937.n:
            self.k = 0
        
        y = x ^ (x >> MT19937.u)
        y = y ^ ((y << MT19937.s) & MT19937.b)
        y = y ^ ((y << MT19937.t) & MT19937.c)
        return (y ^ (y >> MT19937.l)) & MT19937.d

class AlgebraicMersenneTwisterCracker:
    def __init__(self, MT):
        self.known_val = []
        self.known_pos = []
        self.ctr = 0
        self.MT = MT
        self.UMASK_VEC = self.mask_to_vec(self.MT.UMASK, self.MT.w)
        self.LMASK_VEC = self.mask_to_vec(self.MT.LMASK, self.MT.w)
        self.RS1_TARGET_MASK_VEC, self.RS1_MASK_VEC = self.right_shift_to_vec(1, self.MT.w)
        self.A_MASK_VEC = self.mask_to_vec(self.MT.a, self.MT.w)
        self.RSU_TARGET_MASK_VEC, self.RSU_MASK_VEC = self.right_shift_to_vec(self.MT.u, self.MT.w)
        self.LSS_MB_TARGET_MASK_VEC, self.LSS_MB_MASK_VEC = self.left_shift_to_vec(self.MT.s, self.MT.w)
        # apply mask to shift
        self.LSS_MB_TARGET_MASK_VEC &= self.mask_to_vec(self.MT.b, self.MT.w)
        self.LSS_MB_MASK_VEC &= self.mask_to_vec(self.MT.b >> self.MT.s, self.MT.w)

        self.LST_MC_TARGET_MASK_VEC, self.LST_MC_MASK_VEC = self.left_shift_to_vec(self.MT.t, self.MT.w)
         # apply mask to shift
        self.LST_MC_TARGET_MASK_VEC &= self.mask_to_vec(self.MT.c, self.MT.w)
        self.LST_MC_MASK_VEC &= self.mask_to_vec(self.MT.c >> self.MT.t, self.MT.w)

        self.RSL_TARGET_MASK_VEC, self.RSL_MASK_VEC = self.right_shift_to_vec(self.MT.l, self.MT.w)
    
    def mask_to_vec(self, mask, bit_length):
        """ returns boolean vector representation of a mask
        """
        return np.array([(mask >> i) & 1 for i in range(bit_length)], dtype=bool)
    
    def right_shift_to_vec(self, shift, bit_length):
        """ returns boolean vector representation of a right shift
        """
        t = np.ones(bit_length, dtype=bool)
        v = np.ones(bit_length, dtype=bool)
        for i in range(shift):
            v[i] = 0
            t[-1-i] = 0
        return t, v

    
    def left_shift_to_vec(self, shift, bit_length):
        """ returns boolean vector representation of a left shift
        """
        v, t = self.right_shift_to_vec(shift, bit_length)
        return t, v

    def conditional_sum(self, x0, num_bits):
        """ represents (x & 1) ? mask : 0 in GF(2)
        """
        z = np.zeros((self.MT.w, num_bits), dtype=bool)
        z[self.A_MASK_VEC] = x0
        return z

    def submit(self, bin_str):
        """ Submit a partial leak from a mersenne twister. Word alignment must be maintained.
        Args:
            bin_str: string consisting of {0,1,?} with length MT.w with least significant bit last
        """
        assert len(bin_str) == self.MT.w
        for c in reversed(bin_str):
            assert c in ("0", "1", "?")
            if c != "?":
                self.known_val.append(int(c))
                self.known_pos.append(self.ctr)
            self.ctr += 1
    
    def solve(self, check_unique=False, save_target_matrix=False, track_progress=True):
        """ Solve for the initial and final state of the mersenne twister. Runs in O(n^3) time due the solving a system of linear equations.

        Args:
            check_unique: whether to check the solution is unique (try this if you are getting mismatches), it requires computing kernel of matrix which also takes O(n^3) time.
            save_target_matrix: saves target_matrix to self.target_matrix
            track_progress: prints progress status
        
        Returns True if legal solution found (may or may not be unique) when check_unique is False. 
        If check_unique is True, it returns True iff legal solution is unique, False if legal solution is non unique.
        Fails if no solution can be found.
        """
        num_bits = self.MT.w * self.MT.n
        assert len(self.known_val) >= num_bits
        assert self.ctr % self.MT.w == 0
        # large state matrix
        state_matrix = np.eye(num_bits, dtype=bool)
        target_matrix = np.zeros((len(self.known_pos), num_bits * 2), dtype=bool)
        pos = 0
        print_if_track_progress = lambda x : print(x) if track_progress else None
        print_if_track_progress("Determining system of linear equations:")
        words = self.ctr // self.MT.w
        if track_progress:
            from tqdm import tqdm
        else:
            tqdm = lambda x : x
        for i in tqdm(range(words)):
            curr_end = (i + 1) * self.MT.w
            k = i % self.MT.n

            j = k + 1
            if j >= self.MT.n:
                j -= self.MT.n
            
            x = np.zeros((self.MT.w, num_bits), dtype=bool)
            x[self.UMASK_VEC] = state_matrix[k*self.MT.w:(k+1)*self.MT.w][self.UMASK_VEC]
            x[self.LMASK_VEC] = state_matrix[j*self.MT.w:(j+1)*self.MT.w][self.LMASK_VEC]

            x_a = self.conditional_sum(x[0], num_bits)
            x_a[self.RS1_TARGET_MASK_VEC] ^= x[self.RS1_MASK_VEC]

            j = k + self.MT.m
            if j >= self.MT.n:
                j -= self.MT.n

            x = (state_matrix[j*self.MT.w:(j+1)*self.MT.w] ^ x_a)
            state_matrix[k*self.MT.w:(k+1)*self.MT.w, :] = x
            if pos < len(self.known_pos) and self.known_pos[pos] < curr_end:
                y = x
                y[self.RSU_TARGET_MASK_VEC] ^= y[self.RSU_MASK_VEC]
                y[self.LSS_MB_TARGET_MASK_VEC] ^= y[self.LSS_MB_MASK_VEC]
                y[self.LST_MC_TARGET_MASK_VEC] ^= y[self.LST_MC_MASK_VEC]
                y[self.RSL_TARGET_MASK_VEC] ^= y[self.RSL_MASK_VEC]

                while pos < len(self.known_pos) and self.known_pos[pos] < curr_end:
                    target_matrix[pos] = np.concatenate([y[self.known_pos[pos]%self.MT.w], y[self.known_pos[pos]%self.MT.w] ^ y[(self.known_pos[pos]+1)%self.MT.w]])
                    if self.known_val[pos]:
                        target_matrix[pos+1] = np.concatenate([y[self.known_pos[pos+1]%self.MT.w], y[self.known_pos[pos+1]%self.MT.w] ^ y[(self.known_pos[pos+1]+1)%self.MT.w]])
                    else:
                        target_matrix[pos+1] = np.concatenate([y[self.known_pos[pos+1]%self.MT.w] ^ y[self.known_pos[pos]%self.MT.w], y[self.known_pos[pos+1]%self.MT.w] ^ y[(self.known_pos[pos+1]+1)%self.MT.w]])
                    pos += 2
        assert pos == len(self.known_pos)

        if save_target_matrix:
            self.target_matrix = target_matrix
        print_if_track_progress("Solving system of linear equations, please wait.")
        initial_state = f2.solve_right(target_matrix, np.array(self.known_val, dtype=bool))
        self.initial_state1, self.initial_state2 = np.split(np.array(initial_state, dtype=bool), 2)
        self.final_state1 = f2.matmul(state_matrix, self.initial_state1.reshape(-1, 1))
        self.final_state2 =  f2.matmul(state_matrix, self.initial_state2.reshape(-1, 1))
        self.final_k = (k + 1) % self.MT.n
        return True
    
    def convert_to_state_list(self, state):
        """ Convert a given state to a list of int. """
        L = []
        for i in range(len(state) // self.MT.w):
            word = int(0)
            for j in range(self.MT.w):
                word = word | (int(state[i*self.MT.w + j]) << j)
            L.append(word)
        return L
    
    def get_final_state(self):
        """ Return the final state and index of a mersenne twister. """
        return self.convert_to_state_list(self.final_state1), self.final_k, self.convert_to_state_list(self.final_state2), self.final_k

if __name__ == "__main__":
    if args.REMOTE:
        io = remote(sys.argv[1], sys.argv[2])
    else:
        io = process(["python", "dual_mt_drbg.py"])
    io.recvuntil(b'n=')
    io.sendline(b"20000")
    io.recvuntil(b'L=')
    L = ast.literal_eval(io.recvline().rstrip().decode())
    solver = AlgebraicMersenneTwisterCracker(MT19937)
    for v in L:
        solver.submit("?"*30 + str((v>>1)&1) + str(v&1))
    solver.solve()
    recovered_state1, recovered_k1, recovered_state2, recovered_k2 = solver.get_final_state()
    r1 = MT19937(recovered_state1, recovered_k1)
    r2 = MT19937(recovered_state2, recovered_k2)
    for i in range(624):
        io.recvuntil(b'v1=')
        v1 = r1.next_uint32()
        print(v1)
        io.sendline(str(v1).encode())
    for i in range(624):
        io.recvuntil(b'v2=')
        v2 = r2.next_uint32()
        io.sendline(str(v2).encode())
    print(io.recvall())
