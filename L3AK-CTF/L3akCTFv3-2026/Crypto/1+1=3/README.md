# 1+1=3

- **Author:** 0xhashiman
- **Category:** Crypto
- **Solves:** 5
- **Connection:** `https://one-plus-one-equals-three.instances.ctf.l3ak.team`

## Description

Hacking ZK is just finding Δ Λ Γ

---

## Port changes

If you need to change the listenning port go to:

1 - In challenge.go, the port openning at lines 193/194:

``` rust
fmt.Println("listening on :8080")
http.ListenAndServe(":8080", nil)
```

2- In docker-compose.yml:

```yaml
ports:
  - "8080:8080"
```

---

## Solution

This challenge uses a broken Groth16 setup. The server asks for a proof that passes verification for the false statement `z = x + y + 1`. If the proof is accepted the server returns the flag.

## Where's the bug?

Normally, proving this false statement should be impossible. However, the verifier in `challenge.go` uses a corrupted verifying key stored in `vkHex`. The setup intentionally creates the weak relation `delta = lambda * gamma` where `lambda` is small. In normal Groth16 verification, the public-input commitment is paired with `gamma`, while the proof element `C` is paired with `delta`. Because `lambda` is small, we can recover it from the verifying key and choose `C` so that these two pairing terms cancel each other.

Precisely, we choose `C = -(1/lambda) * vk_x` where `vk_x = IC[0] + x*IC[1] + y*IC[2] + z*IC[3]`

## Why no proving key is needed

A genuine Groth16 proof normally requires the proving key. In this exploit however, we do not create a valid proof from a witness. The forged proof passes verification because selected terms in the pairing equation cancel each other.
Once we recover `lambda` from the verifying key, we can construct the proof directly. The proving key `pk.bin` is included in the player files as a distraction, so the real vulnerability is not immediately obvious.

## More info

This challenge was inspired by vulnerabilities found in two blockchain projects:
[Forging zkSNARK Proofs via Misconfigured Verification Keys](https://coinsbench.com/forging-zksnark-proofs-via-misconfigured-verification-keys-the-veil-01-eth-exploit-2a6bb7d0078b)
[Foomcash Exploit Explained](https://www.quillaudits.com/blog/hack-analysis/foomcash-exploit-explained)
