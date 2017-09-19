from random import randrange, shuffle, choice
import string


def generate_pin_code():
    secret = list(randrange(0,9) for _ in range(4))
    shuffle(secret)
    return "".join(map(str, secret))


def generate_code():
    secret = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(9))
    return secret
