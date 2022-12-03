# Parse Books Library
The script returns information about each book from https://tululu.org/, downloads the image and the book file with the text. Received information about the book is displayed in the console. The range of books to be downloaded is set by the user. By default, the first 10 books are downloaded.

## How to install
This should be enough for quickstart:
- Python3 should be already installed.
- Create virtual environment (optional)
```shell
python -m venv .venv
source .venv/bin/activate
```
- Install all requirements:
```shell
pip install -r requirements.txt
```
## How to run scripts
### parse_tululu_books.py
```shell
python parse_tululu_books.py [-h] [--start_id] [--end_id]
```
options:
`-h, --help` show this help message and exit
`--start_id START_ID` The beginning of the range of books to be downloaded (`default=1`)
`--end_id END_ID` End of the downloadable books range (`default=10`)

### parse_tululu_category.py
```shell
python parse_tululu_category.py [-h] [--start_page] [--end_page] [--dest_folder] [--json_path] [--skip_imgs] [--skip_txt]
```
options:
`-h, --help` show this help message and exit
`--start_page START_ID` The beginning of the range of books to be downloaded (`default=1`)
`--end_page END_ID` End of the downloadable books range. if not present, then download all pages
`--dest_folder PATH` Path to directory with parsing results: pictures, books, JSON (`default="books\"`)
`--json_path PATH` Specify path to `*.json` file with results (`default="books\"`)
`--skip_imgs` Do not download pictures (`default=False`)
`--skip_txt` Do not download books (`default=False`)


> Written with [StackEdit](https://stackedit.io/).
