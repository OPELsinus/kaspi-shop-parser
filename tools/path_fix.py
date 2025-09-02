def protect_path(value: str) -> str:
    import re

    return re.sub(r'[<>:"/\\|?*]', '_', value)


def protect_url(value: str) -> str:
    from urllib.parse import quote

    return quote(value, safe='~()*!.\'')


if __name__ == '__main__':
    print(protect_path('c://asdkljasdj'))
    print(protect_url('https:// google.kz'))
