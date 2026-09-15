from Crypto.Util.number import bytes_to_long as b2l
from Crypto.Random import get_random_bytes as rand

class RNJail:
    def __init__(rnjail, maxAllowedAttempts, intendedTargetValue):
        rnjail.intendedTargetValue = intendedTargetValue
        rnjail.maxAllowedAttempts = maxAllowedAttempts
        rnjail.SAFE_GLOBALS = locals()
        rnjail.SAFE_GLOBALS['__builtins__'] = {}
        del rnjail.SAFE_GLOBALS['intendedTargetValue']
    
    def evalInteger(rnj, s: str) -> int:
        i = eval(s, rnj.SAFE_GLOBALS)
        try:
            return int(i)
        except:
            return 0

    def validateInput(rnjail, s: str) -> tuple[bool, str]:
        if len(s) > 10:
            return False, 'too long!'
        for b in dir(__builtins__):
            if b.lower() in s.lower():
                return False, 'no functions!'
        if any(i in s for i in '[,;\"\'`]'):
            return False, 'scary letters...'
        return True, ''
    
    def startRnj(rnjail):
        print(f'i\'m thinking of a number... you get {rnjail.maxAllowedAttempts} tries to figure it out\n')
        for i in range(rnjail.maxAllowedAttempts):
            user_input = input(f'guess #{i+1}: ')
            ok, err = rnjail.validateInput(user_input)
            if not ok:
                print(f'invalid input: {err}')
                continue
            try:
                v = rnjail.evalInteger(user_input)
            except:
                print('that didn\'t work')
                continue

            if v == rnjail.intendedTargetValue:
                print(f'i guess you\'ve earned this... {open("flag.txt").read().strip()}')
                return
            elif v < rnjail.intendedTargetValue:
                print('you gotta think bigger...')
            else:
                print('i can\'t count that high...')
        print('better luck next time')

if __name__ == '__main__':
    game = RNJail(2,  b2l(rand(1024)))
    game.startRnj()