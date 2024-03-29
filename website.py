import argparse
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def get_book_descriptions(book_information_file):
    with open(book_information_file, 'r', encoding='utf8') as json_file:
        book_descriptions = json.load(json_file)
    for book_description in book_descriptions:
        if book_description['image_path']:
            book_description['image_path'] = os.path.join('../media/images', book_description['image_path'].split('/')[4]).replace('\\', '/')
        book_filename = book_description['title'].replace(':', '')
        book_description['text_path'] = os.path.join('../media/books', f'{book_filename}.txt').replace('\\', '/')
    return book_descriptions


def on_reload():
    print('Reloading')
    book_information_file = main.book_information_file
    cards_per_page = main.cards_per_page
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    book_descriptions = get_book_descriptions(book_information_file)
    chunked_book_descriptions = list(chunked(book_descriptions, cards_per_page))
    os.makedirs('pages', exist_ok=True)
    for books_chunk_number, books_chunk in enumerate(chunked_book_descriptions, start=1):
        rendered_page = template.render(books=books_chunk, pages=range(1, len(chunked_book_descriptions)+1), current_page=books_chunk_number, last_page=len(chunked_book_descriptions))
        with open(os.path.join('pages', f'index{books_chunk_number}.html'), 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--book_information_file', help='Название .json файла с информацией о книгах, по умолчанию "book_information.json"', type=str, default='book_information.json')
    parser.add_argument('--cards_per_page', help='Количество карточек книг на одной странице', type=int, default=20)
    args = parser.parse_args()
    main.book_information_file = args.book_information_file
    main.cards_per_page = args.cards_per_page
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.', default_filename='pages/index1.html')


if __name__ == '__main__':
    main()
