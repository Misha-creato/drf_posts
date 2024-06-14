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


class ColorFormatter(logging.Formatter):
    COLOR_CODES = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLOR_CODES:
            levelname_color = f"{self.COLOR_CODES[levelname]}{levelname}{Style.RESET_ALL}"
            name_color = f"{self.COLOR_CODES[levelname]}{record.name}{Style.RESET_ALL}"
            record.levelname = levelname_color
            record.name = name_color
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    console_handler = logging.StreamHandler()
    logger.setLevel(logging.DEBUG)
    formatter = ColorFormatter(
        f'%(asctime)s %(levelname)s %(message)s %(name)s %(funcName)s '
    )
    console_handler.setFormatter(formatter)
    logger.handlers = [console_handler]
    return logger


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
