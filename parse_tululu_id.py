import argparse
import os
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


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


def download_books(start_id, end_id, dest_folder='tulululib'):
    for book_id in range(start_id, end_id+1):
        try:
            url = f'https://tululu.org/b{book_id}'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            parsed_book = parse_book_page(response)
            if parsed_book['text_path']:
                download_text(parsed_book['text_path'], parsed_book['title'], dest_folder)
            if parsed_book['image_path']:
                download_image(parsed_book['image_path'], dest_folder)
        except requests.ConnectionError:
            time.sleep(10)
            book_id = book_id - 1
            continue
        except requests.HTTPError:
            print(f'Не получается скачать id - {book_id}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', help='Начальный book_id', type=int)
    parser.add_argument('end_id', help='Конечный book_id', type=int)
    args = parser.parse_args()
    download_books(args.start_id, args.end_id)


if __name__ == '__main__':
    main()
