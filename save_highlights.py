#! venv/bin/python
import os
import re
import sys
import string

from pyfiglet import Figlet

from constants import KINDLE_DIRECTORY, HIGHLIGHT_SEPARATOR
from upload_to_notion import upload_to_notion
from utilities import print_success, print_failure, print_process, print_name, read_write_library, simplify_string


def parse_reading(text):
    strings = text.split("\n")
    if len(strings) > 2:
        book_name_author = strings[0]
        highlight = strings[-1]
        match = re.findall(r"\(([^\(\)]*)\)", book_name_author)
        if match:
            book_title = book_name_author.replace(
                match[-1], '').strip()[:-2][1:]
            author = match[-1]
            book_title = book_title.strip()
            return book_title, author, highlight
    return None, None, None


def new_book(book_title, author, simple_title):
    book = {'title': book_title, 'author': author,
            'highlights': [], 'simple_title': simple_title}
    return book


def add_book(book_title, author, highlight, library, simple_title):
    for book in library:
        if book['simple_title'] == simple_title:
            for highlights in book['highlights']:
                if highlights['text'] == highlight:
                    return library
            book['highlights'].append({'text': highlight, 'saved': False})
            return library
    book = new_book(book_title, author, simple_title)
    book['highlights'].append({'text': highlight, 'saved': False})
    library.append(book)
    return library


def read_kindle(library):
    with open(os.path.join(KINDLE_DIRECTORY, "My Clippings.txt"), "r", encoding='utf-8') as file:
        readings = file.read()
    texts = readings.split(HIGHLIGHT_SEPARATOR)
    for text in texts:
        book_title, author, highlight = parse_reading(
            text.strip())
        if book_title:
            library = add_book(book_title, author, highlight,
                               library, simplify_string(book_title))
    return library


def main():
    f = Figlet(font='contessa')
    print_name(f.renderText('Kindle-To-Notion'))
    print_process('Reading Kindle....')
    lib = read_write_library('r')
    try:
        lib = read_kindle(lib)
    except FileNotFoundError as e:
        print_failure('Please connect Kindle and rerun the script.')
        sys.exit()
    path = read_write_library('w', lib)
    print_success(f'Saved Kindle Highlights in {path}')
    upload_to_notion(lib)
    print_success('Upload Successful')


if '__main__' == __name__:
    main()
