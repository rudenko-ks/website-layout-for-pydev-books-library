import requests
from pathlib import Path
from itertools import count


def main():
    books_path = 'books/'
    Path(books_path).mkdir(parents=True, exist_ok=True)

    for book_id in count():
        url = f"https://tululu.org/txt.php?id={book_id}"
        response = requests.get(url)
        response.raise_for_status()

        book_name = f"id{book_id}.txt"
        book_file = Path(books_path, book_name)
        with open(book_file, 'wb') as file:
            file.write(response.content)

        if book_id >= 10:
            break


if __name__ == '__main__':
    main()
