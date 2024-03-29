# Парсер книг с сайта tululu.org

Парсер помогает собрать информацию и скачать книги в выбранном диапазоне айди, либо по категории в выбранном диапазоне страниц.

### Как установить

Python должен быть установлен.
Для запуска необходимо установить библиотеки с помощью `pip`:
```
pip install -r requirements.txt
```

### Аргументы
Для запуска парсера по id необходимо ввести 2 аргумента:
1. `start_id` - выбирает начало диапазона.
2. `end_id` - выбирает конец диапазона.

Чтобы парсер начал работу необходимо запустить файл `main.py` с двумя аргументами, например:
```
python parse_tululu_id.py 1 10
```
В этом случае парсер попробует скачать книги с id от 1 до 10.

Для запуска парсера по категории нет обязательных аргументов, но можно кастомизировать парсинг используя опциональные аргументы:
1. `--start_page` - Начальная страница, по умолчанию 1.
2. `--end_page` - Конечная страница, по умолчанию 10000.
3. `--category` - Категория для парсера, по умолчанию "l55" - научная фантастика.
4. `--dest_folder` - Путь к каталогу с результатами парсинга: картинкам, книгам, JSON, по умолчанию "media".
5. `--skip_img` - Не скачивать картинки, по умолчанию False.
6. `--skip_text` - Не скачивать текст, по умолчанию False.
7. `--json_name` - Название .json файла с результатами, по умолчанию "book_information.json".

Для запуска необходимо ввести название файла и необходимые аргументы, например:
```
python parse_tululu_category.py --start_page 20 --end_page 30
```
В этом случае попробует скачать все книги с 20 по 30 страницу в категории по умолчанию.

Для запуска офлайн версии вебсайта необходимо запустить файл `website.py`. Для запуска есть 2 аргумента:
1. `--book_information_file` - файл с информацией о книгах, по умолчанию `book_information.json`.
2. `--cards_per_page` - количество карт книг на одну страницу, по умолчанию `20`.
Для корректной работы сайта необходимы уже скачанные книги и обложки, и информация о них, размещенные в папках:
1. `media/books` - для текстовых файлов книг.
2. `media/images` - для файлов обложек.
3. `book_information.json` - для `.json` файла с информацией о книгах, можно поменять на другой json файл используя нужный аргумент.

При запуске файла сайт начнёт работать по адресу `http://127.0.0.1:5500`

Для ознакомления с работой и функционалом сайта в репозиторий был добавлен контент с сайта [tululu.org](https://tululu.org/), онлайн версия ознакомительного примера из репозитория доступна по адресу на [github.pages.io](https://zhartem21.github.io/library-parse/pages/index1.html)

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).