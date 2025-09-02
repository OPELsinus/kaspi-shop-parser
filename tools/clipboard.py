def clipboard_set(value):
    import pyperclip

    pyperclip.copy(value)


def clipboard_get(raise_err=False, empty=False):
    import pyperclip

    result = pyperclip.paste()
    if not len(result):
        if raise_err:
            raise Exception('Clipboard is empty')
        else:
            return None
    if empty:
        clipboard_set('')
    return result


if __name__ == '__main__':
    clipboard_set('test')
    print(clipboard_get())
