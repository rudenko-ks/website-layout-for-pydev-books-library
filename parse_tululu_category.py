import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from main import check_for_redirect, parse_book_page, download_image, download_txt


def get_book_page(url: str) -> bool:
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response=response)
    return response


def save_books_as_json(books: list) -> None:
    with open('books.json', 'w', encoding='utf-8') as json_file:
        json.dump(books, json_file, indent=4, ensure_ascii=False)


def main():
    connection_timeout = 10
    sci_fi_category_id = 55
    book_download_url = f'https://tululu.org/txt.php'

    book_collection = []
    for page in range(1, 2):
        genre_page_url = f'https://tululu.org/l{sci_fi_category_id}/{page}/'

        try:
            response = requests.get(genre_page_url)
            response.raise_for_status()
            check_for_redirect(response=response)
            soup = BeautifulSoup(markup=response.text, features='lxml')

            book_cards_selector = '.d_book .bookimage a'
            if (book_cards := soup.select(book_cards_selector)):
                for book_card in book_cards:
                    book_url_slug = book_card['href']
                    book_page_url = urljoin(genre_page_url, book_url_slug)

                    try:
                        if book_page := get_book_page(url=book_page_url):
                            book = parse_book_page(book_page)
                            book_id = ''.join(
                                char for char in book_url_slug if char.isdigit())
                            book_filename = f"{book_id}. {book['name']}"
                            book_file_path = download_txt(book_download_url, book_id,
                                                          book_filename)
                            download_image(urljoin(book_page_url, book['img_url']))
                            book['book_path'] = book_file_path

                            book_collection.append(book)

                    except requests.HTTPError:
                        print(f'\nНеправильная ссылка на книгу: {book_page_url}!')

        except requests.HTTPError:
            print(f'\nНеправильная ссылка на категорию: {genre_page_url}')
        except requests.ConnectionError:
            print(f'\nОшибка подключения. Проверьте интернет соединение.')
            time.sleep(connection_timeout)
        except requests.ReadTimeout:
            print(f'\nВремя ожидания запроса истекло.')

    save_books_as_json(book_collection)


if __name__ == '__main__':
    main()
