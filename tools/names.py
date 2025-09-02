def get_hostname() -> str:
    import socket

    return socket.gethostbyname(socket.gethostname())


def get_username() -> str:
    from win32api import GetUserNameEx, NameSamCompatible

    return GetUserNameEx(NameSamCompatible)


if __name__ == '__main__':
    print(get_hostname())
    print(get_username())
