# cosmofile
**Author:** drec

**Difficulty:** medium/hard

**Category:** pwn

## Description
Have you ever read files? Hopefully, this will teach you how to read them.
Go read the code, the Dockerfile, the fake flag,
and the secrets of the universe... and the real flag, of course.

Before you complain to the admins, test your exploit locally.
To set up a local challenge environment, you can run the following command,
on the same directory as the provided Dockerfile:

```
docker run -p 5000:5000 --privileged $(docker build -q .)
```

For those that have podman or rootless installations of Docker,
you will need to build and run the container as root.

Any issues you find are most likely intended and are part of the challenge,
except for availability issues.

## Building/Deployment

Follow the typical [redpwn jail](https://github.com/redpwn/jail) workflow.

```sh
docker run -p 5000:5000 --privileged $(docker build -q .)
```

## Flag format
L3AK{JU57_b3c4u43_7H3R3_15_N0_vft4bl3_D035N7_m34n_Y0U_5h0uld_61V3_up}
