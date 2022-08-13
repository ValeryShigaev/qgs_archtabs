from typing import Callable


def error_handler(sign: str) -> Callable:
    """
    Writes exceptions to logfile, returns True if no exceptions or False if
    there are

    :param sign: logger text
    :type sign: str
    :rtype: Callable
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs) -> bool:
            try:
                func(*args, **kwargs)
                print(sign)
                print("success")
                return True
            except Exception as e:
                print(sign)
                print(e)
                return False
        return wrapper
    return decorator
