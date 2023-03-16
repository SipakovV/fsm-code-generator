import time
from functools import wraps


def print_timing(func):
    '''
    create a timing decorator function
    use
    @print_timing
    just above the function you want to time
    '''
    @wraps(func)  # improves debugging
    def wrapper(*arg):
        start = time.perf_counter()  # needs python3.3 or higher
        result = func(*arg)
        end = time.perf_counter()
        fs = '{}\t\t\t:{:.6f} ms'
        print(fs.format(func.__name__, (end - start) * 1000))
        return result
    return wrapper