def try_except_decorator(retry_cout=2, retry_delay=1, print_exc=False):
    import traceback
    from time import sleep

    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(retry_cout):
                try:
                    result = func(*args, **kwargs)
                    return result
                except (Exception,):
                    if print_exc:
                        traceback.print_exc()
                    sleep(retry_delay)
            raise Exception('retry_cout <= 0')

        return wrapper

    return decorator


if __name__ == '__main__':
    @try_except_decorator()
    def test():
        print(float([1, None]))


    test()
