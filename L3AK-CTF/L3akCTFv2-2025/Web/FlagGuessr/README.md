# FlagGuessr

- **Author:** sy1vi3
- **Category:** Web
- **Solves:** 6

## Description

I was told the challs weren't guessy enough and decided to do something about it. <http://34.59.119.124:17005> The challenge container restarts every 10 minutes. Author: sy1vi3 [flagguessr.zip](<https://ctf.l3ak.team/files/a53568744c14d4f27b2592d5ed1ce517/flagguessr.zip?token=eyJ1c2VyX2lkIjoxMTQ3LCJ0ZWFtX2lkIjo1NjIsImZpbGVfaWQiOjcyfQ.aHGnEQ.oS0pSY7XoVGlvZyUk0iwSsxkSs8>) Hint: perhAps there's a wAy to turn An XSS into something thAt lets you get RCE... ??? -> XSS -> ??? -> RCE
flagguessr.zip

---

## Solution

This challenge has several different bugs that are intended to be chained together to get RCE in the container

The web app presents a fairly simple game where one uploads a "flag.txt" file when making an account, and is then invited to "guess"
the flags of the other users on the site. The user input and saved flag are hashed and compared with two different hashing algorithms.
There also a utility on the profile page to create a PNG image "certificate", which invokes another binary in the container with values
passed via environment variables.

The intended solution is as follows

1) Create a hash collision to allow arbitrary file upload
    - The `MARK_CHEATER` SQL template has a typo that results in a panic. This is "fine" normally, because it only gets
    invoked if both a user's flag and another user's guess have the same MD5 sum but different SHA256 sums. This will only
    happen for specifically chosen payloads, and would almost certainly never happen randomly.
    - It's fairly trivial to generate an MD5 hash collision that results in valid HTML. We can do this, and then send the admin
    bot (cheater report, which accepts an arbitrary URL path on the site) to the uploaded file via `/users/x/guesses/y`. Putting
    a script tag in that file gives XSS.

2) Use the XSS to leak the admin account display name
    - The display names are hidden, normally. It's possible to leak it via the previously mentioned XSS vuln

3) Forge a JWT with custom data
    - The `/register` endpoint has a bug - if the `InsertUser` call fails after the username was validated, it will mistakenly re-sign
    the session cookie the user sent, even if it was invalid to start with. The SQLite database has `COLLATE NOCASE` in the username field,
    and the application lowercases every input to the register function. Golang string comparison will work normally, but a SELECT statement
    with a username of a different case will still result in a match. The primary key on the table is (username, display_name), if it's possible
    to get a username with the same letters but a different casing (and know the corresponding display_name), the insert will fail. This bug is
    based on something I discovered in the wild myself, where `COLLATE NOCASE` was causing an insert to fail even though a Golang string comparison
    said it was unique.
    - The admin user created to handle a report has a capital `A` in their name. Leaking their display name with the XSS allows forging the JWT we need

4) Set LD_PRELOAD in the session cookie
    - The certificate generator copies all of the `properties` out of the session into environment variables. Setting LD_PRELOAD to an uploaded malicious
    library results in code execution when the `cp` call in the certgen program is made (the Golang program alone won't cause it to get invoked)
    - Compile a library with a reverse shell in the ctor, such that it fires when loaded.

## Flag

L3AK{c0llat3_n0c4s3_c4n_caus3_issue5_a7_tim3s}
