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
        formatter = logging.Formatter(f'{color}%(levelname)s {Style.RESET_ALL}%(message)s')
        self.setFormatter(formatter)
        super().emit(record)


logger = logging.getLogger('custom_handler')
