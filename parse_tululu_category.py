import argparse
from itertools import count
import json
import os
from pathlib import Path
import sys
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from parse_tululu_books import check_for_redirect, parse_book_page, download_image, download_txt


def get_book_page(url: str) -> bool:
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response=response)
    return response


def save_books_as_json(books: list, folder: str = 'json/') -> None:
    path = Path(folder, 'books.json')
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(books, json_file, indent=4, ensure_ascii=False)


def get_all_category_pages(url_template: str, category_id: int) -> int:
    url = url_template.format(category=category_id, page=1)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(markup=response.text, features='lxml')
    count_page_selector = '.ow_px_td .center .npage'
    if count_page := soup.select(count_page_selector):
        return int(count_page[-1].text)
    else:
        return 0


def create_argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="""\
        Скрипт возвращает с сайта https://tululu.org/ информацию о каждой
        книге, скачивает изображение и файл книги с текстом в заданном
        диапазоне из категории "Научная фантастика".
        Полученная информация о книге выводится в консоль.
        Диапзон скачиваемых книг задаётся пользователем.
        По умолчанию скачиваются первые 5 страниц.""",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--start_page',
                        help='Начало диапазона скачиваемых страниц',
                        type=int,
                        default=1)
    parser.add_argument('--end_page',
                        help='Конец диапазона скачиваемых страниц',
                        type=int)
    parser.add_argument(
        '--dest_folder',
        help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.',
        type=str,
        default='books/')
    parser.add_argument('--json_path',
                        help='Указать свой путь к *.json файлу с результатами.',
                        type=str)
    parser.add_argument('--skip_imgs',
                        help='Не скачивать картинки.',
                        action='store_true')
    parser.add_argument('--skip_txt', help='Не скачивать книги.', action='store_true')
    return parser.parse_args()


def main():
    connection_timeout = 10
    sci_fi_category_id = 55
    book_download_url = f'https://tululu.org/txt.php'
    genre_page_url_template = 'https://tululu.org/l{category}/{page}/'

    args = create_argparser()
    if not args.json_path:
        args.json_path = args.dest_folder

    if not args.end_page:
        args.end_page = get_all_category_pages(genre_page_url_template,
                                               sci_fi_category_id)

    book_collection = []
    for page in range(args.start_page, args.end_page):
        genre_page_url = genre_page_url_template.format(category=sci_fi_category_id,
                                                        page=page)
        try:
            response = requests.get(genre_page_url)
            response.raise_for_status()
            check_for_redirect(response=response)
            soup = BeautifulSoup(markup=response.text, features='lxml')

            book_cards_selector = '.d_book .bookimage a'
            if book_cards := soup.select(book_cards_selector):
                for book_card in book_cards:
                    book_url_slug = book_card['href']
                    book_page_url = urljoin(genre_page_url, book_url_slug)

                    try:
                        if book_page := get_book_page(url=book_page_url):
                            book = parse_book_page(book_page)
                            book_id = ''.join(
                                char for char in book_url_slug if char.isdigit())
                            book_filename = f"{book_id}. {book['name']}"

                            book_file_path = ''
                            if not args.skip_txt:
                                book_file_path = download_txt(
                                    book_download_url, book_id, book_filename,
                                    args.dest_folder)

                            if not args.skip_imgs:
                                download_image(urljoin(book_page_url, book['img_url']),
                                               args.dest_folder)

                            book['book_path'] = book_file_path
                            book_collection.append(book)

                    except requests.HTTPError:
                        print(f'\nНеправильная ссылка на книгу: {book_page_url}')

        except KeyboardInterrupt:
            print(f'Остановлено пользователем.')
            sys.exit(0)
        except requests.HTTPError:
            print(f'\nНеправильная ссылка на категорию: {genre_page_url}')
        except requests.ConnectionError:
            print(f'\nОшибка подключения. Проверьте интернет соединение.')
            time.sleep(connection_timeout)
        except requests.ReadTimeout:
            print(f'\nВремя ожидания запроса истекло.')

    save_books_as_json(book_collection, args.json_path)


if __name__ == '__main__':
    main()
