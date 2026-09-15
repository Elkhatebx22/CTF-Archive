## Solution

### Flag 1

Solve the puzzles, shouldnt take more than 10 minutes to do by hand

### Flag 2

*Either* solve them by hand (will take at least an hour or two), or find the source images and use them to match with pixels in
the chunks to find the right order

### Flag 3

Same as flag 2, but too big for doing it by hand to be a reasonable option, requiring automation

### Code Download

The image used isn't on the internet so you can't match pixels. instead, match edges by best fit using whatever search method you choose

### Flag 4

There's an XSS on the user display page. The session cookie is httponly, but since it's same-site you can make an API request to fetch the flag directly instead of exfiltrating the session token

### Flag 5

The 5th flag is embedded in the 5th image, getting the level 5 reward isn't enough to actually get the image. There's an unsecure random number generation bug in
the code, golang's default random number generator only uses the lower 32 bits of the seed, even if more than that is provided. This is possible to brute force in about
10 minutes. Solve the first puzzle normally to find the correct answer, then crack its random seed, and use that to predict the rest of the puzzle solutions. Use that to
reconstruct the final puzzle image, which has the flag written on it. Run `go run .` and then `python3 reconstruct_5.py`