#! venv/bin/python
import os
import re
import sys

from constants import KINDLE_DIRECTORY, HIGHLIGHT_SEPARATOR
from upload_to_notion import read_write_library, upload_to_notion


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
            return book_title.strip(), author, highlight
    return None, None, None


def new_book(book_title, author):
    book = {'title': book_title, 'author': author,
            'highlights': []}
    return book


def add_book(book_title, author, highlight, library):
    for book in library:
        if book['title'] == book_title:
            for highlights in book['highlights']:
                if highlights['text'] == highlight:
                    return library
            book['highlights'].append({'text': highlight, 'saved': False})
            return library
    book = new_book(book_title, author)
    book['highlights'].append({'text': highlight, 'saved': False})
    library.append(book)
    return library


def read_kindle(library):
    with open(os.path.join(KINDLE_DIRECTORY, "My Clippings.txt"), "r", encoding='utf-8') as file:
        readings = file.read()
    texts = readings.split(HIGHLIGHT_SEPARATOR)
    for text in texts:
        book_title, author, highlight = parse_reading(text.strip())
        if book_title:
            library = add_book(book_title, author, highlight, library)
    return library


def main():
    lib = read_write_library('r')
    try:
        lib = read_kindle(lib)
    except FileNotFoundError as e:
        sys.exit('Please connect Kindle.')
    read_write_library('w', lib)
    upload_to_notion()


if '__main__' == __name__:
    main()
