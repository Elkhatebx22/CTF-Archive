# Build Overview

### Directory Structure

* `resources/` – Contains binaries and assembly code used during challenge construction.
  * `template` – The base binary compiled from `template.c`, used as a foundation for the final challenge binary.
  * `main.s` – A partially assembled version of `main`, containing machine instructions manually reconstructed using `objdump`. Function offsets are manually populated.
  * `alpha` – The final unstripped binary with symbols. See [How to Build](#how-to-build) for build instructions.

* `scripts/` – Various scripts and helper tools for automating the build process.

  * `builder.py` – Assembles the modified `main.s` and injects it into the `template` binary.
  * `writer.cpp` – Utility that modifies the `.text` section to be writable, allowing code injection.
  * `z3_gen.py` – Generates a system of equations from a polynomial, used to assist in generating `main.c`.

* `src/` – Source code for the challenge.

  * `main.c`, `operators.c`, `operators.h` – Core logic of the challenge binary.
  * `template.c` – Source used to generate the `template` binary.

* `tests/` – Contains test cases and utilities for verifying challenge correctness during development.

> Note: The scripts `builder.py` and `writer.cpp` were generated with the assistance of AI.

---

## How to Build

Below is a rough outline of the build process for generating the challenge binary:

```sh
# Compile the main source into assembly (main.s)
gcc src/main.c -fno-stack-protector -S

# Manually edit main.s:
#   - Remove all directives and functions except main
#   - Replace all symbols with their virtual address
#   - Remove any `endbr64` instructions

# Assemble and patch the binary using builder.py
python scripts/builder.py main.s

# Modify the .text section to be writable
objcopy --writable-text --set-section-flags .text=alloc,load,code,data dist/alpha dist/alpha
g++ scripts/writer.cpp && ./a.out dist/alpha

# Strip symbols from the final binary
strip dist/alpha
```

> This process will produce `dist/alpha`, the final challenge binary.
