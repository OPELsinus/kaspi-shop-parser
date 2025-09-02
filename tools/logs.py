import logging
from contextlib import suppress
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Union

import requests


def init_logger(
        logger_name: str = 'rpa.robot',
        datefmt: str = '%Y-%m-%d,%H:%M:%S',

        console_level: int = logging.INFO,
        console_format: str = '%(asctime)s||%(levelname)s||%(message)s',

        file_level: int = logging.INFO,
        file_format: str = '%(asctime)s||%(levelname)s||%(message)s',
        file_path: Union[Path, str] = None,

        tg_level: int = logging.WARNING,
        tg_format: str = '%(message)s',
        tg_token: str = None,
        tg_chat_id: str = None
) -> logging.Logger:
    class ArgsFormatter(logging.Formatter):
        def __init__(self, *args, sep=' ', **kwargs):
            super().__init__(*args, **kwargs)
            self.sep = sep

        def format(self, record):
            if record.args:
                record.msg = self.sep.join([str(i) for i in [record.msg, *record.args]])
                record.args = None
            return super(ArgsFormatter, self).format(record)

    class PostHandler(logging.Handler):
        def __init__(self, tg_token_, chat_id_, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.tg_token = tg_token_
            self.chat_id = chat_id_
            self.url = f'https://api.telegram.org/bot{self.tg_token}/sendMessage'

        def emit(self, record):
            data = self.format(record)
            data = {'chat_id': self.chat_id, 'text': str(data)}
            with suppress(Exception):
                requests.post(self.url, json=data, verify=False, timeout=1)

    logging.basicConfig(level=console_level, format=console_format, datefmt=datefmt)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ArgsFormatter(console_format, datefmt=datefmt))
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    if file_path:
        log_path = Path(file_path).resolve()
        log_path.parent.mkdir(exist_ok=True, parents=True)
        file_handler = TimedRotatingFileHandler(log_path.__str__(), 'W3', 1, 5, "utf-8")
        file_handler.setFormatter(ArgsFormatter(file_format, datefmt=datefmt))
        file_handler.setLevel(file_level)
        logger.addHandler(file_handler)

    if tg_token and tg_chat_id:
        tg_handler = PostHandler(tg_token, tg_chat_id)
        tg_handler.setFormatter(ArgsFormatter(tg_format, datefmt=datefmt, sep='\n'))
        tg_handler.setLevel(tg_level)
        logger.addHandler(tg_handler)

    return logger


if __name__ == '__main__':
    test_logger = init_logger(
        file_path='test.log',
        tg_token='5604299504:AAEmE_2Tu_HcF6G-keZgR8M1MOQuoyb7xsI',
        tg_chat_id='531139435'
    )
    test_logger.info('info test')
    test_logger.warning('warning test')
