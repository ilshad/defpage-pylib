import json
import random
import string
import time
from datetime import datetime

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

def serialized(k):
    def _get(inst):
        return json.loads(getattr(inst, k) or u'null')
    def _set(inst, v):
        setattr(inst, k, json.dumps(v))
    return property(_get, _set)

def epochz(dt):
    """Converts given datetime into UTC with UNIX epoch timestump by integer.
    epochz :: datetime.datetime() -> integer(unix(UTC))
    Testing:
    >>> int(datetime.utcnow().strftime("%s")) == epochz(datetime.now())
    """
    delta = int(time.mktime(time.gmtime()) - time.mktime(datetime.now().timetuple()))
    epoch = int(time.mktime(dt.timetuple()))
    return epoch + delta
