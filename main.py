import os

import requests


def download_tutulu_books_in_folder(book_ids, folder):
    url = "https://tululu.org/txt.php"
    params = {}
    os.makedirs(folder, exist_ok=True)
    for id in book_ids:
        params['id'] = id
        response = requests.get(url, params=params)
        response.raise_for_status()
        with open(os.path.join(folder, f'id{id}.txt'), 'wb') as file:
            file.write(response.content)


def main():
    book_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    download_tutulu_books_in_folder(book_ids, 'books')


if __name__ == '__main__':
    main()
