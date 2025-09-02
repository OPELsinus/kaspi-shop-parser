from pathlib import Path
from typing import Union


def net_use(path: Union[Path, str], username: str, password: str, delete_all=False):
    import subprocess

    if delete_all:
        command = f'net use * /delete /y'
        result = subprocess.run(command, shell=True, capture_output=True, encoding='cp866')
        print('delete', ' '.join(str(result.stdout).split(sep=None)))

    path = str(path)[:-1] if str(path)[-1] == '\\' else str(path)
    command = rf'net use "{path}" /user:{username} {password}'.replace(r'\\\\', r'\\')
    result = subprocess.run(command, shell=True, capture_output=True, encoding='cp866')
    if len(result.stderr):
        print('net_use', path, ' '.join(str(result.stderr).split(sep=None)))
    if len(result.stdout):
        print('net_use', path, ' '.join(str(result.stdout).split(sep=None)))


if __name__ == '__main__':
    net_use('localhost', 'test', 'test')
