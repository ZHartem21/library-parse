import argparse
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_book_descriptions(book_information):
    books = json.loads(book_information)
    for book in books:
        if book['image_path']:
            book['image_path'] = os.path.join('../tulululib/images', book['image_path'].split("/")[4]).replace('\\', '/')
        book_filename = book['title'].replace(':', '')
        book['text_path'] = os.path.join('../tulululib/books', f'{book_filename}.txt').replace('\\', '/')
    return books


def on_reload(book_information):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    books = get_book_descriptions(book_information)
    chunked_books = list(chunked(books, 20))
    os.makedirs('pages', exist_ok=True)
    for i, books_chunk in enumerate(chunked_books):
        rendered_page = template.render(books=books_chunk, pages=range(0, len(chunked_books)), current_page=i, last_page=len(chunked_books))
        with open(os.path.join('pages', f'index{i+1}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--book_information', help='Название .json файла с информацией о книгах, по умолчанию "book_information.json"', type=str, default='book_information.json')
    args = parser.parse_args()
    on_reload(args.book_information)
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.', default_filename='pages/index1.html')


if __name__ == '__main__':
    main()
