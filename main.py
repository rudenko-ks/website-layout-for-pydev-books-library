import os
import requests
from pathlib import Path
from itertools import count
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename, sanitize_filepath


def check_for_redirect(response: requests.Response):
    if response.history:
        raise requests.HTTPError


def get_book_name(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response=response)

    soup = BeautifulSoup(markup=response.text, features='lxml')
    book_tag = soup.find('div', id='content').find('h1')
    book_name, book_author = book_tag.text.strip().split(' \xa0 :: \xa0 ')
    return book_name


def download_txt(url: str, filename: str, folder: str = 'books/') -> str:
    """Функция для скачивания текстовых файлов.

    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.

    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response=response)

    f_ext = '.txt'
    f_name = sanitize_filename(filename)
    f_path = Path(folder, f'{f_name}{f_ext}')
    Path(folder).mkdir(parents=True, exist_ok=True)

    with open(f_path, 'wb') as file:
        file.write(response.content)

    return str(f_path)


def main():
    for book_id in count(1):
        book_info_url = f'https://tululu.org/b{book_id}/'
        book_download_url = f"https://tululu.org/txt.php?id={book_id}"

        try:
            book_name = get_book_name(book_info_url)
            book_filename = f'{book_id}. {book_name}'
            download_txt(book_download_url, book_filename)
        except requests.HTTPError:
            print(f'Неправильная ссылка на книгу #{book_id}!')
        else:
            if book_id >= 10:
                break


if __name__ == '__main__':
    main()
