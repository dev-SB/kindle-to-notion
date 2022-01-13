import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from tqdm import tqdm

from constants import NOTION_URL, LIBRARY_FILE, DATABASE_KEYWORD, BLOCK_KEYWORD, NEW_HIGHLIGHT_JSON_FILE, DATA_FOLDER

load_dotenv()

INTEGRATION_KEY = os.getenv('NOTION_INTEGRATION_KEY')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')


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


def convert_json(response):
    if response.status_code == 200:
        response = response.json()
        return response
    else:
        print(f'error {response.text}')
        return False


def query_notion_db():
    database_url = NOTION_URL + DATABASE_KEYWORD + DATABASE_ID + '/query'
    response = requests.post(database_url,
                             headers={"Authorization": f"Bearer {INTEGRATION_KEY}", "Notion-Version": "2021-08-16"})
    return convert_json(response)


def query_page_highlights(page_id):
    block_url = f'{NOTION_URL}{BLOCK_KEYWORD}{page_id}/children'
    response = requests.get(block_url,
                            headers={"Authorization": f"Bearer {INTEGRATION_KEY}", "Notion-Version": "2021-08-16"})
    return convert_json(response)


def get_highlight_json(highlight):
    with open(NEW_HIGHLIGHT_JSON_FILE, 'r') as f:
        data = json.load(f)
    data['bulleted_list_item']['text'][0]['text']['content'] = highlight
    return data


def get_payload(highlights):
    return {"children": [get_highlight_json(highlight['text']) for highlight in highlights if not highlight['saved']]}


def save_highlights_notion(highlights, page_id):
    block_url = f'{NOTION_URL}{BLOCK_KEYWORD}{page_id}/children'
    response = requests.patch(block_url, headers={
        "Authorization": f"Bearer {INTEGRATION_KEY}", "Notion-Version": "2021-08-16"}, json=get_payload(highlights))
    return convert_json(response)


def process_notion_lib(notion_lib):
    notion_db_list = {}
    for book in notion_lib['results']:
        title_text = book['properties']['Name']['title']
        if len(title_text) > 0:
            title = title_text[0]['text']['content']
            notion_db_list[title] = {'title': title, 'id': book['id']}
    return notion_db_list


def process_notion_highlight(book_highlights):
    highlights = []
    for res in book_highlights['results']:
        highlights.append(res['bulleted_list_item']
                          ['text'][0]['text']['content'])
    return highlights


def merge_lib_notion_lib(lib, notion_lib):
    for book in lib:
        if notion_lib.get(book['title'], -1) != -1:
            book['notion_id'] = notion_lib[book['title']]['id']
            for highlight in book['highlights']:
                if not highlight['saved'] and highlight['text'] in notion_lib[book['title']]['highlights']:
                    highlight['saved'] = True
    read_write_library('w', lib)
    return lib


def get_notion_highlights(notion_lib):
    for book in notion_lib.values():
        book['highlights'] = process_notion_highlight(
            query_page_highlights(book['id']))
    return notion_lib


def upload_to_notion():
    lib = read_write_library('r')
    notion_lib = get_notion_highlights(process_notion_lib(query_notion_db()))
    lib = merge_lib_notion_lib(lib, notion_lib)
    for book in tqdm(lib):
        if 'notion_id' in book.keys():
            status = save_highlights_notion(
                book['highlights'], book['notion_id'])
            if status:
                for highlight in book['highlights']:
                    highlight['saved'] = True
                read_write_library('w', lib)
