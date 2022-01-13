import json
import os
from pathlib import Path

from termcolor import cprint

from constants import LIBRARY_FILE, DATA_FOLDER

print_success = lambda text: cprint(text, 'green', attrs=['blink'])
print_failure = lambda text: cprint(text, 'red', attrs=['bold'])
print_process = lambda text: cprint(text, 'cyan',attrs=['bold'])
print_name = lambda text: cprint(text, 'yellow', attrs=['bold'])


def read_write_library(operation, lib=None):
    path = os.path.join(DATA_FOLDER, LIBRARY_FILE)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w') as library:
            json.dump(list(), library)
    with open(path, operation, encoding='utf8') as library:
        if operation == 'r':
            return json.load(library)
        json.dump(lib, library, ensure_ascii=False)
    return path
