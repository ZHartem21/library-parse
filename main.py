import argparse
import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def parse_book_page(page_content):
    soup = BeautifulSoup(page_content, 'lxml')

    title, author = soup.find('td', class_='ow_px_td').find('h1').text.split('::')

    parsed_genres = soup.find('span', class_='d_book').find_all('a')
    genres = []
    for genre in parsed_genres:
        genres.append(genre.text)

    comments = []
    parsed_comments = soup.find_all('div', class_='texts')
    if parsed_comments:
        for comment in parsed_comments:
            comments.append(comment.find('span', class_='black').text) 

    image_path = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin('https://tululu.org/', image_path)
    if image_path == '/images/nopic.gif':
        image_url = None

    book_info = {
        'title': title.strip(),
        'author': author.strip(),
        'genres': genres,
        'comments': comments,
        'image_url': image_url,
    }
    return book_info


def download_image(url, filename, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    if url:
        response = requests.get(url)
        response.raise_for_status()
        with open(sanitize_filepath(os.path.join(folder, sanitize_filename(filename))), 'wb') as file:
            file.write(response.content)


def download_text(url, filename, folder='books/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    with open(sanitize_filepath(os.path.join(folder, sanitize_filename(filename))), 'wb') as file:
        file.write(response.content)


def download_books(start_id, end_id):
    for book_id in range(start_id, end_id+1):
        try:
            url = f'https://tululu.org/b{book_id}'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            book_info = parse_book_page(response.text)
            text_filename = f'{book_id}. {book_info["title"]}.txt'
            download_text(f'https://tululu.org/txt.php?id={book_id}', text_filename)
            image_filename = f'{book_id}.jpg'
            download_image(book_info['image_url'], image_filename)
            print(book_info['title'], book_info['author'], book_info['genres'])
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
