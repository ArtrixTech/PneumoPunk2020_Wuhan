def retry(func, max_retries, *args):
    while max_retries:
        try:
            result = func(*args)
            if result:
                return result
            raise ValueError
        except ValueError:
            print('retried. ' + str(max_retries))
            import time
            import random
            time.sleep(random.randint(1, 4))
            max_retries -= 1
            return retry(func, max_retries, *args)
    raise ValueError('The function returned False all the time.')
