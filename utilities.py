import json
import os
from pathlib import Path
import re
import string
from termcolor import cprint

from constants import LIBRARY_FILE, DATA_FOLDER


def print_success(text): return cprint(text, 'green', attrs=['blink'])
def print_failure(text): return cprint(text, 'red', attrs=['bold'])
def print_process(text): return cprint(text, 'cyan', attrs=['bold'])
def print_name(text): return cprint(text, 'yellow', attrs=['bold'])


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


def simplify_string(og_string):
    simple_title = re.sub(rf"[{string.punctuation}]", "", og_string)
    return simple_title.lower().replace(' ', '').strip()
