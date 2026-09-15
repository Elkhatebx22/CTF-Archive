# Math as a Service

- **Author:** SteakEnthusiast
- **Category:** Misc
- **Solves:** 3
- **Connection:** `https://github.com/silentmatt/expr-eval`

## Description

The author of [this library](<https://github.com/silentmatt/expr-eval>) forgot to push a security fix to the [npm package](<https://www.npmjs.com/package/expr-eval>). No worries though, I manually installed the latest version to ensure my service is as secure as possible! Build / deploy: docker run -p 5000:5000 --privileged $(docker build -q .) Author: SteakEnthusiast nc 34.55.69.223 14000 [dist.zip](<https://ctf.l3ak.team/files/03191dbe53fcc6391d8947742ac29797/dist.zip?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjM3fQ.aHGu9Q.hCxZjC8_v0O3ablX-vzIF5IAyE8>) Hint1: This isn't actually a zero-day vulnerability. The solution depends on a mismatch between the output of the challenge's convert.js and the output you'd get from a correctly built version of the library. Compare both carefully and look for subtle differences. Hint2: After some lively arguments with participants about the last hint, I realized I shoiuld've been clearer on the wording. While it may have seemed like you needed a zero-day to solve this challenge, that’s not strictly the case here.
Math as a Service.zip

## Building/Deployment

Follow the typical [redpwn jail](https://github.com/redpwn/jail) workflow.

docker run -p 5000:5000 --privileged $(docker build -q .)

## Flag Format

`L3AK{57r1c7_m0d3_1n_pl4c3_k33p5_7h3_0_d4y5_47_b4y_f72eb7086c2957d4}`
