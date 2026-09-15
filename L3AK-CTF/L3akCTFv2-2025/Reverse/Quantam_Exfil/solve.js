#!/usr/bin/env node

const crypto = require("crypto");
const dct = require("./helper.node");

function createRNG(seed) {
  if (!Buffer.isBuffer(seed) || seed.length !== 16)
    throw new Error("need 16-byte seed");
  let s0 = BigInt("0x" + seed.slice(0, 8).reverse().toString("hex"));
  let s1 = BigInt("0x" + seed.slice(8, 16).reverse().toString("hex"));
  if (s0 === 0n && s1 === 0n) s1 = 1n;
  return {
    next64() {
      let x = s0,
        y = s1;
      s0 = y;
      x ^= x << 23n;
      x ^= x >> 17n;
      x ^= y;
      x ^= y >> 26n;
      s1 = x;
      return (s0 + s1) & ((1n << 64n) - 1n);
    },
    randInt(n) {
      return Number(this.next64() % BigInt(n));
    },
  };
}

function genSBox(st) {
  const sbox = Array.from({ length: 256 }, (_, i) => i);
  const rng = createRNG(st.slice(0, 16));
  for (let i = 255; i > 0; i--) {
    const j = rng.randInt(i + 1);
    [sbox[i], sbox[j]] = [sbox[j], sbox[i]];
  }
  return sbox;
}

function genPBox(st) {
  const pbox = Array.from({ length: 128 }, (_, i) => i);
  const rng = createRNG(st.slice(16, 32));
  for (let i = 127; i > 0; i--) {
    const j = rng.randInt(i + 1);
    [pbox[i], pbox[j]] = [pbox[j], pbox[i]];
  }
  return pbox;
}

if (process.argv.length !== 4) {
  console.error("Usage: node solve.js original.jpg exfil.jpg");
  process.exit(1);
}
const [, , hostPath, stegPath] = process.argv;

const { quant0: q0, quant1: q1, coefs: host } = dct.read(hostPath);
const { coefs: steg } = dct.read(stegPath);

const initState = crypto.createHash("sha512").update(q0).update(q1).digest();

const parity = [];
host.forEach((buf, ci) => {
  const blocks = buf.length / 128;
  for (let bi = 0; bi < blocks; ++bi)
    for (let zz = 1; zz < 64; ++zz)
      if (Math.abs(buf.readInt16LE((bi * 64 + zz) * 2))) {
        const v = steg[ci].readInt16LE((bi * 64 + zz) * 2);
        parity.push(Math.abs(v) & 1);
      }
});

const rng = createRNG(Buffer.from(initState.slice(32, 48)));
const slots = Array.from({ length: parity.length }, (_, i) => i);
for (let i = slots.length - 1; i; --i) {
  const j = rng.randInt(i + 1);
  [slots[i], slots[j]] = [slots[j], slots[i]];
}
const bits = slots.map((idx) => parity[idx]);

function cipherAt(off) {
  const b = Buffer.alloc(16);
  for (let i = 0; i < 16; i++) {
    let v = 0;
    for (let k = 0; k < 8; k++) v = (v << 1) | bits[off + i * 8 + k];
    b[i] = v;
  }
  return b;
}

let state = initState,
  posBits = 0,
  needBits = Infinity,
  blk = 0;
const plain = [];

while (posBits + 128 <= needBits) {
  const cblk = cipherAt(posBits);
  posBits += 128;

  const S = genSBox(state), P = genPBox(state);
  const invS = Uint8Array.from({ length: 256 }, () => 0);
  const invP = Uint8Array.from({ length: 128 }, () => 0);
  for (let i = 0; i < 256; i++) invS[S[i]] = i;
  for (let i = 0; i < 128; i++) invP[P[i]] = i;

  const afterXor = Buffer.alloc(16);
  for (let i = 0; i < 16; i++) afterXor[i] = cblk[i] ^ state[i];

  const bitsPerm = [];
  for (let i = 0; i < 16; i++)
    for (let k = 7; k >= 0; k--) bitsPerm.push((afterXor[i] >> k) & 1);

  const bitsOrig = new Uint8Array(128);
  for (let i = 0; i < 128; i++) bitsOrig[i] = bitsPerm[invP[i]];

  const pblk = Buffer.alloc(16);
  for (let i = 0; i < 16; i++) {
    let v = 0;
    for (let k = 0; k < 8; k++) v = (v << 1) | bitsOrig[i * 8 + k];
    pblk[i] = invS[v];
  }
  plain.push(pblk);

  state = crypto
    .createHash("sha512")
    .update(Buffer.concat([state, pblk]))
    .digest();

  if (blk === 0) {
    const L = pblk.readUInt32BE(0);
    const padded = (4 + L + 15) & ~15;
    needBits = padded * 8;
  }
  ++blk;
}

const full = Buffer.concat(plain);
const L = full.readUInt32BE(0);
const flag = full.slice(4, 4 + L).toString("utf8");
console.log(flag);
