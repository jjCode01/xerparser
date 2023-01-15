# xerparser
# decorators.py


def rounded(ndigits: int = 2):
    def inner(function):
        def wrapper(*args, **kwargs):
            value = function(*args, **kwargs)
            if isinstance(value, float):
                value = round(value, ndigits)
            elif isinstance(value, int):
                value = float(value)
            return value

        return wrapper

    return inner
