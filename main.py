import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def get_book_info_by_id(id):
    url = f'https://tululu.org/b{id}'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('td', class_='ow_px_td').find('h1').text.split('::')
    return title.strip(), author.strip()


def download_books_in_folder(book_ids, folder):
    url = "https://tululu.org/txt.php"
    params = {}
    os.makedirs(folder, exist_ok=True)
    for id in book_ids:
        try:
            params['id'] = id
            response = requests.get(url, params=params)
            response.raise_for_status()
            check_for_redirect(response)
            title, author = get_book_info_by_id(id)
            with open(sanitize_filepath(os.path.join(folder, sanitize_filename(f'{id}. {title}.txt'))), 'wb') as file:
                file.write(response.content)
        except requests.HTTPError:
            print(f'id {id} - неверный')


def main():
    book_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # download_books_in_folder(book_ids, 'books')



if __name__ == '__main__':
    main()
