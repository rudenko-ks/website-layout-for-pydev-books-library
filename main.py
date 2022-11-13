import os
import requests
from pathlib import Path
from itertools import count
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import unquote, urljoin, urlsplit
import argparse
from argparse import RawTextHelpFormatter


def check_for_redirect(response: requests.Response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(response: requests.Response) -> dict:
    soup = BeautifulSoup(markup=response.text, features='lxml')
    book_tag = soup.find('div', id='content').find('h1')
    book_name, book_author = book_tag.text.strip().split(' \xa0 :: \xa0 ')
    book_img_url = soup.find('div', class_='bookimage').find('img')['src']

    book_genres = []
    if (genres_tag := soup.find('span', class_='d_book').find_all('a')):
        for genre in genres_tag:
            book_genres.append(genre.text)

    book_comments = []
    if (comment_tags := soup.find_all('div', class_='texts')):
        for comment_tag in comment_tags:
            comment = comment_tag.find('span')
            book_comments.append(comment.text)

    return {
        'name': book_name,
        'author': book_author,
        'genres': book_genres,
        'img_url': book_img_url,
        'comments': book_comments
    }


def download_image(url: str, folder: str = 'images/'):
    response = requests.get(url)
    response.raise_for_status()

    f_name = unquote(urlsplit(url).path.split('/')[-1])
    f_path = Path(folder, f_name)
    Path(folder).mkdir(parents=True, exist_ok=True)

    with open(f_path, 'wb') as file:
        file.write(response.content)


def download_txt(url: str,
                 book_id: int,
                 filename: str,
                 folder: str = 'books/') -> str:
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response=response)

    f_ext = '.txt'
    f_name = sanitize_filename(filename)
    f_path = Path(folder, f'{f_name}{f_ext}')
    Path(folder).mkdir(parents=True, exist_ok=True)

    with open(f_path, 'wb') as file:
        file.write(response.content)

    return str(f_path)


def create_argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="""\
        Скрипт возвращает с сайта https://tululu.org/ информацию о каждой книге, скачивает изображение и файл книги с текстом.
        Полученная информация о книге выводится в консоль.
        Диапзон скачиваемых книг задаётся пользователем.
        По умолчанию скачиваются первые 10 книг.""",
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('--start_id',
                        help='Начало диапазона скачиваемых книг',
                        type=int,
                        default=1)
    parser.add_argument('--end_id',
                        help='Конец диапазона скачиваемых книг',
                        type=int,
                        default=10)
    return parser.parse_args()


def main():
    args = create_argparser()

    for book_id in range(args.start_id, args.end_id):
        book_page_url = f'https://tululu.org/b{book_id}/'
        book_download_url = f"https://tululu.org/txt.php"

        try:
            response = requests.get(book_page_url)
            response.raise_for_status()
            check_for_redirect(response=response)
            book = parse_book_page(response)

            book_filename = f"{book_id}. {book['name']}"
            download_txt(book_download_url, book_id, book_filename)
            download_image(urljoin(book_page_url, book['img_url']))

            print(f'\nЗаголовок: {book["name"]}')
            print(f'Жанр книги: {book["genres"]}')

            if book["comments"]:
                print("\n".join(comment for comment in book["comments"]))
            else:
                print(
                    'Пользователи пока что не оставили комментарии к данной книге.'
                )

        except requests.HTTPError:
            print(f'\nНеправильная ссылка на книгу #{book_id}!')


if __name__ == '__main__':
    main()
