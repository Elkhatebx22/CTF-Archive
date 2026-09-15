# Immiscible

- **Author:** Suvoni
- **Category:** Crypto
- **Solves:** 145

## Description

When I was a child, my grandfather would sit alone at the kitchen table long after midnight, toiling tirelessly beneath the weak amber light flickering faintly above the stove. I would wake sometimes to the sound of glass clinking softly against glass and wander down the hallway to find him there, sleeves rolled to his elbows, surrounded by notebooks filled with symbols and careful little sketches only he could understand. Most people called him mad, and even among our family I was the only one who showed any curiosity about him and his work. He hardly spoke, only answering simple questions with impossible ones, but his eyes - tired as they were - always carried the strange calm of someone listening to a conversation the rest of the world could not hear.

On those nights he would pour two liquids into a tall bottle. One pale and sharp-smelling, thin as rainwater. The other dark gold, slow and heavy, catching the light like melted glass. He would shake them together over and over, watching the storm swirl inside the bottle as though he expected revelation itself to emerge from the chaos. And for a fleeting moment, it looked like two dancers waltzing elegantly around a ballroom; the currents twisted together into delicate clouds and spirals, each one folding into the next so perfectly that I almost believed they had become one thing entirely.

But he would always set the bottle down and wait. Slowly, inevitably, the illusion unraveled. The heavier currents gathered themselves apart. The lighter ones drifted upward. Invisible boundaries reappeared where moments ago there had seemed to be harmony.

I once asked him why he kept repeating the experiment if he already knew the outcome.

He smiled at that - not sadly, not happily, but with the contemplative expression of someone remembering a truth too large to explain simply.

“Because,” he told me, “the world reveals itself most honestly through the things that refuse to mix.”

I did not understand him then.

I think I do now.

---

## Solution

The Unbalanced Oil & Vinegar (UOV) signature scheme in this challenge is broken because the public key does not contain oil-oil terms. Thus, if we can guess the 4 vinegar variables, every polynomial becomes linear in the 4 oil variables.

The attack is:

1. Brute-force the 4 vinegar variables over F_79. There are 79^4 = 38,950,081 possible candidates, which is very feasible to brute.
2. For each guess, convert the MQ system into a linear system in the 4 oil variables.
3. Solve the 9 x 4 linear system modulo 79 using Gaussian elimination.
4. Verify the recovered signature against the target.
5. Derive AES key = SHA256(bytes(signature)).
6. Decrypt encrypted_flag.

Flag: ``L3AK{Oil_4ND_v1N3g4r_WitH0ut_Mix1nG_Sp1LL5_eV3rYth1ng}``
