import random
import string

def random_string(length):
    chars = []
    while length:
        chars.extend(random.sample(string.letters+string.digits, 1))
        length -= 1
    return "".join(chars)
    
def is_int(info, req):
    try:
        z = int(info['match']['name'])
        return True
    except (TypeError, ValueError):
        return False
