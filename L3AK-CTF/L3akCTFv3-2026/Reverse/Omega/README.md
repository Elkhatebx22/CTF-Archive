# Omega

- **Author:** Atzr
- **Category:** Reverse
- **Solves:** 3
- **Connection:** `ncat --ssl omega.instances.ctf.l3ak.team 1337`

## Description

"One must imagine Sisyphus happy." — Camus

---

Omega is a job executor: it accepts jobs and runs them inside its virtual
machine. The flag is at `/challenge/flag.txt` on the server.

## What's here

| File              | Description                          |
| ----------------- | ------------------------------------ |
| `executor`        | The executor binary the server runs. |
| `echo.remote.prx` | An example job; runs on the remote.  |
| `echo.local.prx`  | The same job, for local runs.        |

## Running locally

```
SECRET=00112233445566778899aabbccddeeff ./executor echo.local.prx
```

Flag: `L3AK{M45k3d_1n$truct!on5_P3rmu+ed_5u8s+1tut3d_954247ee}`

## Deploying

Using Docker Compose (recommended):

```sh
docker compose -f build/docker-compose.yml up --build -d
```

Or with plain Docker:

```sh
docker build -f build/Dockerfile -t omega .
docker run --rm --privileged -p 5000:5000 omega
```
