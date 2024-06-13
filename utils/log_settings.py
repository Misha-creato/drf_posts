import logging
from colorama import (
    init,
    Fore,
    Style,
)

init(autoreset=True)

LEVEL_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.MAGENTA,
}


class MyConsoleHandler(logging.StreamHandler):
    def emit(self, record):
        color = LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        formatter = logging.Formatter(
            f'{color}%(levelname)s %(asctime)s %(name)s %(funcName)s {Style.RESET_ALL}%(message)s'
        )
        self.setFormatter(formatter)
        # self.setLevel(logging.DEBUG)
        super().emit(record)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def get_log_user_data(user_data: dict) -> dict:
    data = user_data.copy()
    keys = [
        'password',
        'confirm_password',
        'new_password',
    ]
    for key in keys:
        data.pop(key, None)
    return data
