# Reading is hard

- **Author:** sy1vi3

## Infra notes

This challenge needs to be instanced, and both flags need to be dynamic + mapped in as volumes, and very important that flag2 is owned by root and `r--------` perms

no external network, but routing between containers does need to work

this is a 0day challenge

## Description

You might need to do a little bit of reading.

---

## Flag 1 (2 solves)

trivial nsjail sidechannel, see kalmarctf. there are a bajillion ways to do it

## Flag 2 (0 solves)

postgres rce 0day. i have a working PoC. i'm not sharing it
