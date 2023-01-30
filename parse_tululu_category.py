import argparse
import json
import os
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath
from parse_tululu_id import parse_book_page, download_image, download_text, check_for_redirect


def parse_category_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    selector = 'table.d_book tr td a[href^="/b"]'
    books = soup.select(selector)
    book_urls = [urljoin(response.url, book['href']) for book in books]
    book_urls = list(dict.fromkeys(book_urls))
    return book_urls


def parse_category(page_start, page_end, category='l55'):
    category = f'{category}/'
    category_url = urljoin('https://tululu.org/', category)
    parsed_book_urls = []
    for page in range(page_start, page_end+1):
        try:
            url = urljoin(category_url, str(page))
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            parsed_book_urls.extend(parse_category_page(response))
        except requests.HTTPError:
            print(f'Страницы {page} Не существует, загружаются книги на страницах {page_start} - {page - 1}')
            break
        except requests.ConnectionError:
            time.sleep(10)
            page = page - 1
            continue
    return parsed_book_urls


def download_books_in_category(page_start, page_end, category, dest_folder, skip_img=False, skip_text=False, json_name='book_information.json'):
    parsed_book_urls = parse_category(page_start, page_end, category)
    os.makedirs(dest_folder, exist_ok=True)
    parsed_books = []
    for book_url in parsed_book_urls:
        try:
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            parsed_book = parse_book_page(response)
            if parsed_book['text_path']:
                parsed_books.append(parsed_book)
            if not skip_text and parsed_book['text_path']:
                download_text(parsed_book['text_path'], parsed_book['title'], dest_folder)
                if not skip_img and parsed_book['image_path']:
                    download_image(parsed_book['image_path'], dest_folder)
        except requests.HTTPError:
            print(f'Ссылка {book_url} - неверная')
            continue
        except requests.ConnectionError:
            time.sleep(10)
            book_url = parsed_book_urls[parsed_book_urls.index(book_url)-1]
            continue
    json_path = os.path.join(dest_folder, json_name)
    with open(json_path, 'w', encoding='utf8') as json_file:
        json.dump(parsed_books, json_file, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', help='Начальная страница, по умолчанию 1', type=int, default=1)
    parser.add_argument('--end_page', help='Конечная страница, по умолчанию 10000', type=int, default=10000)
    parser.add_argument('--category', help='Категория для парсера, по умолчанию "l55" - научная фантастика', type=str, default='l55')
    parser.add_argument('--dest_folder', help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON, по умолчанию "tulululib"', type=str, default='tulululib')
    parser.add_argument('--skip_img', help='Не скачивать картинки, по умолчанию False', action='store_true')
    parser.add_argument('--skip_text', help='Не скачивать текст, по умолчанию False', action='store_true')
    parser.add_argument('--json_name', help='Название .json файла с результатами, по умолчанию "book_information.json"', type=str, default='book_information.json')
    args = parser.parse_args()
    download_books_in_category(args.start_page, args.end_page, args.category, args.dest_folder, args.skip_img, args.skip_text, args.json_name)


if __name__ == '__main__':
    main()