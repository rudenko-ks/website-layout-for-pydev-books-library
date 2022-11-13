import os
import requests
from pathlib import Path
from itertools import count
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import unquote, urljoin, urlsplit


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
    book_img_url = soup.find('div', class_='bookimage').find('img')['src']
    print(f'Заголовок: {book_name}')

    if (book_comments := soup.find_all('div', class_='texts')):
        for comment_tag in book_comments:
            comment = comment_tag.find('span')
            print(comment.text)
    else:
        print('Пользователи пока что не оставили комментарии к данной книге.' +
              '\n')

    download_image(urljoin(url, book_img_url))
    return book_name


def download_image(url: str, folder: str = 'images/'):
    response = requests.get(url)
    response.raise_for_status()

    f_name = unquote(urlsplit(url).path.split('/')[-1])
    f_path = Path(folder, f_name)
    Path(folder).mkdir(parents=True, exist_ok=True)

    with open(f_path, 'wb') as file:
        file.write(response.content)


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
            print(f'\nНеправильная ссылка на книгу #{book_id}!  \n')
        else:
            if book_id >= 10:
                break


if __name__ == '__main__':
    main()
