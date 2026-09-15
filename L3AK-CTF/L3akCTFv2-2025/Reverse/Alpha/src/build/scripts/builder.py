# Used to populate the assembly

from keystone import Ks, KS_ARCH_X86, KS_MODE_64
import sys
from pwn import *

context.arch = "amd64"  # 64-bit x86 architecture
context.bits = 64  # Explicitly use 64-bit

# Configuration
ARCH = KS_ARCH_X86
MODE = KS_MODE_64
CHUNK_SIZE = 64  # bytes


def read_assembly_file(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    # Remove comments and blank lines
    instructions = [line.strip().split(";")[0] for line in lines if line.strip()]
    return instructions


def assemble_chunk(ks: Ks, instructions, address):
    asm_code = "\n".join(instructions)
    encoding, _ = ks.asm(asm_code, address)
    return encoding


def chunk_instructions(instructions, ks: Ks, chunk_size=64):
    result = []
    xored_result = []
    current_chunk = []
    current_size = 0

    for instr in instructions:
        try:
            # Assemble this instruction alone to see its size
            instr_bytes, _ = ks.asm(instr, addr=0x101310 + current_size)
            instr_size = len(instr_bytes)
        except Exception as e:
            print(f"Error assembling instruction '{instr}': {e}")
            instr_size = 2

        if (
            current_size + instr_size > chunk_size
            or instr == "cmp\tBYTE PTR [rbp - 17], 0"
        ):
            # Assemble current chunk and reset
            current_chunk += ["nop"] * (CHUNK_SIZE - current_size)
            if current_chunk:
                next_chunk = assemble_chunk(ks, current_chunk, 0x101310)
                if len(result) > 0:
                    xored_result.extend(
                        x ^ y for x, y in zip(next_chunk, result[-CHUNK_SIZE:])
                    )
                result.extend(next_chunk)
            current_chunk = [instr]
            current_size = instr_size
        else:
            current_chunk.append(instr)
            current_size += instr_size

    # Assemble remaining chunk
    if current_chunk:
        next_chunk = assemble_chunk(ks, current_chunk, 0x101310)
        xored_result.extend(x ^ y for x, y in zip(next_chunk, result[-CHUNK_SIZE:]))
        result.extend(next_chunk)

    return result, xored_result


def main(filename):
    ks = Ks(ARCH, MODE)
    instructions = read_assembly_file(filename)
    assembled_bytes, xored_bytes = chunk_instructions(
        instructions, ks, chunk_size=CHUNK_SIZE
    )

    with open("dist/alpha", "+rb") as elf:
        elf.seek(0x1310)
        elf.write(bytes(assembled_bytes[:64]))
        elf.write(b"\x37")  # AAA
        elf.seek(0x2020)
        elf.write(bytes(xored_bytes))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <assembly_file>")
        sys.exit(1)
    main(sys.argv[1])
