import math
import time

# Retry decorator with exponential backoff
def retry(tries, delay=3, backoff=2):
       if backoff < 1:
           raise ValueError("backoff must be greater than 0")
       tries = math.floor(tries)
       if tries < 0:
           raise ValueError("tries must be 0 or greater")
       if delay <= 0:
           raise ValueError("delay must be greater than 0")
       def deco_retry(f):
           def f_retry(*args, **kwargs):
                mtries, mdelay = tries, delay # make mutable
                try:
                    while mtries > 0:
                        mtries -= 1
                        try:
                            rv = f(*args, **kwargs)
                            return rv
                        except Exception,e:
                            time.sleep(mdelay) # wait...
                            mdelay *= backoff  # make future wait longer
                    raise Exception
                except Exception, e:
                    raise Exception, 'Timeout executing %s'%str(f)

           return f_retry
       return deco_retry



def status_to_exitcode(status):
    map = {
        'success': 0,
        'error': 1,
        'failure': 2,
        'warning': 3,
        'terminated': 1,
        'timeout': 1
    }
    return map.get(status)