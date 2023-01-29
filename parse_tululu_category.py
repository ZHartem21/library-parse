import argparse
import json
import os
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def parse_category_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    selector = 'table.d_book tr td a[href^="/b"]'
    books = soup.select(selector)
    book_urls = [urljoin(response.url, book['href']) for book in books]
    book_urls = list(dict.fromkeys(book_urls))
    return book_urls


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    title_and_author_selector = '#content > h1:nth-child(2)'
    title, author = soup.select_one(title_and_author_selector).text.split('::')

    genre_selector = 'td.ow_px_td span.d_book a'
    parsed_genres = soup.select(genre_selector)
    genres = [genre.text for genre in parsed_genres]

    comment_selector = 'div.texts span.black'
    parsed_comments = soup.select(comment_selector)
    comments = [comment.text for comment in parsed_comments]

    image_selector = 'div.bookimage img'
    image_source = soup.select_one(image_selector)['src']
    image_path = urljoin(response.url, image_source)
    if image_source == '/images/nopic.gif':
        image_path = None
    try:
        text_selector = 'a[href^="/txt.php?"]'
        text_path = soup.select_one(text_selector)['href']
    except IndexError:
        text_path = None
    except TypeError:
        text_path = None

    parsed_book = {
        'title': title.strip(),
        'author': author.strip(),
        'image_path': image_path,
        'text_path': text_path,
        'comments': comments,
        'genres': genres,
    }
    return parsed_book


def parse_category(page_start, page_end, category='l55'):
    category = category + '/'
    category_url = urljoin('https://tululu.org/', category)
    parsed_book_urls = []
    for page in range(page_start, page_end+1):
        try:
            url = urljoin(category_url, str(page))
            print(url)
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            parsed_book_urls.extend(parse_category_page(response))
        except requests.HTTPError:
            print(f'Страницы {page} Не существует, загружаются книги на страницах {page_start} - {page - 1}')
            break
    return parsed_book_urls


def download_image(image_path, dest_folder):
    folder = os.path.join(dest_folder, 'images')
    os.makedirs(folder, exist_ok=True)
    library_url = 'https://tululu.org/'
    url = urljoin(library_url, image_path)
    response = requests.get(url)
    response.raise_for_status()
    filename = urlparse(url).path.split('/')[2]
    with open(sanitize_filepath(os.path.join(folder, filename)), 'wb') as file:
        file.write(response.content)


def download_text(text_path, book_title, dest_folder):
    folder = os.path.join(dest_folder, 'books')
    os.makedirs(folder, exist_ok=True)
    library_url = 'https://tululu.org/'
    url = urljoin(library_url, text_path)
    response = requests.get(url)
    response.raise_for_status()
    with open(sanitize_filepath(os.path.join(folder, f'{book_title}.txt')), 'wb') as file:
        file.write(response.content)


def download_books_in_category(page_start, page_end, category, dest_folder, skip_img=False, skip_text=False, json_name='book_information.json'):
    parsed_book_urls = parse_category(page_start, page_end, category)
    os.makedirs(dest_folder, exist_ok=True)
    parsed_books = []
    for book_url in parsed_book_urls:
        response = requests.get(book_url)
        response.raise_for_status()
        parsed_book = parse_book_page(response)
        if parsed_book['text_path']:
            parsed_books.append(parsed_book)
        if not skip_text and parsed_book['text_path']:
            download_text(parsed_book['text_path'], parsed_book['title'], dest_folder)

        if not skip_img and parsed_book['image_path']:
            download_image(parsed_book['image_path'], dest_folder)

    json_path = os.path.join(dest_folder, json_name)
    with open(json_path, 'w', encoding='utf8') as json_file:
        json.dump(parsed_books, json_file, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', help='Начальная страница, по умолчанию 1', type=int, default=1)
    parser.add_argument('--end_page', help='Конечная страница, по умолчанию 10000', type=int, default=10000)
    parser.add_argument('--category', help='Категория для парсера, по умолчанию "l55" - научная фантастика', type=str, default='l55')
    parser.add_argument('--dest_folder', help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON, по умолчанию "tulululib"', type=str, default='tulululib')
    parser.add_argument('--skip_img', help='Не скачивать картинки, по умолчанию False', type=bool, action='store_true')
    parser.add_argument('--skip_text', help='Не скачивать текст, по умолчанию False', type=bool, action='store_true')
    parser.add_argument('--json_name', help='Название .json файла с результатами, по умолчанию "book_information.json"', type=str, default='book_information.json')
    args = parser.parse_args()
    download_books_in_category(args.start_page, args.end_page, args.category, args.dest_folder, args.skip_img, args.skip_text, args.json_name)


if __name__ == '__main__':
    main()