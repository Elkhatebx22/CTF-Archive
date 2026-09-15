# Whitespace Solution

We're given the ASCII-art generator, using it we can find that each letter is a 3x5 grid of pound symbols.

It's somewhat easy to figure, from here, that the spaces-removed flag file has letters 2-across on each row (nothing else makes sense)

We can figure out the number of pound signs on each row of every letter to build a fingerprint for each, then we can check each row of
the flag file to find how many pound signs are on each. The possible letters are every combo of two letters (in either order) that results
in a matching fingerprint when summed together.

Putting all of the possibilities together, there are way too many options at first (61775263599091771244544000). Knowing the flag format, we
can declare that the first five chars are `L3AK{` and that the last one is `}` which narrows it to 20109135286162685952000. From there, iterating
over the choices in a smart way will reveal that the final word could be `d0wn`, and that nothing else looks english-like. Assume the underscore
goes before the `d`, run it again, and the next chunk back looks a lot like `1t`. Keep repeating this, because there aren't that many choices for
each individual word, eventually it's narrowed down enough that brute-force can check the hashes of the remaining possibilities and find the flag.
