import time


def timer_decorator(func):

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"'{func.__name__}' took {end_time - start_time:.2f} seconds to run.")
        return result

    return wrapper


@timer_decorator
def a_slow_function(name, age):
    time.sleep(2)
    print(f"name = {name}, age = {age}")
    print("Function finished!")


a_slow_function(name="shubham", age="25")