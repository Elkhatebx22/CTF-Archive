# RNJail solution

With an unlimited (er, thousands) number of guesses, it's easily possible to do a binary search (use the walrus operator to work with variables instead of literals),
but the challenge only gives two normally. The eval *is* given the locals of the RNJail init function, but without builtins, so variables will persist between attempts.

We're given a reference to the `rnjail` object in `locals()`, if we could call `rnjail.startRnj()` it would reset the attempts counter.

We're only allowed 10-char inputs, and `rnjail.startRnj()` is 17 long. We *could* assign rnjail to something with the walrus like `{z:=rnjail}`, but that's still too long.

Luckily, unicode inputs are allowed, and both `rnjail` and `startRnj` have single-char ligature marks that Python normalizes to be more than one character (`ǌ` becomes `nj` and `ﬅ` becomes `st`).

With this, it's possible to run `{z:=rǌail}` in 10 chars, and then `z.ﬅartRǌ()` in another 10. It takes both shots to set this up the first time, and after that you can make a guess with one attempt, then run
`z.ﬅartRǌ()` again (because `z` is still in locals) to get another two attempts. 

This doesn't quite get there, though, because Python will limit you to around 255-ish stack frames from a function recursively calling itself. Instead, you need to do it a little smarter, and branch down to
about 15 layers deep using *both* guesses to get another two, and only perform actual guesses on the last level of the binary tree.

My solve script gets the answer in about 24500 guesses (it's probably possible to do it in fewer than 3 per bit [change a, check, change b] but I'm lazy)