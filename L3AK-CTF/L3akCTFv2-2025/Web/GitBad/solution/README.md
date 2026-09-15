## Description

#### Step 1
The idea of this challenge is to exploit a blind SSRF caused by `git submodule update --init --recursive` in the profile upload function. The player should be able to create a git repo where the submodule points to an arbitrary URL they control.

#### Step 2
There is an obvious NoSQL injection in the search endpoint, but it can only be reached from 127.0.0.1. So, you will use the blind SSRF to hit this endpoint. There is also a filter; the player should craft a payload that bypasses the filter.

#### Step 3
There is a cache misconfiguration in Varnish where all URLs ending with .js or .css will be cached. The cache key is the path plus parameters. Also, some endpoints add a fake or misleading file extension (like .json, .php, .html, etc.) to API endpoints or URLs to confuse bots, scanners, or attackers. This can be used with the cache to make the blind SSRF response cached.

#### Step 4
Request the same exact path and parameters using curl and you will get the cached response which contains the flag 

check solution.bash for poc 