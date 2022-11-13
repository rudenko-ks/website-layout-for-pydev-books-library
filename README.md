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
```shell
python main.py [-h] [--start_id] [--end_id]
```
options:
`-h, --help` show this help message and exit

`--start_id START_ID` The beginning of the range of books to be downloaded

`--end_id END_ID` End of the downloadable books range

> Written with [StackEdit](https://stackedit.io/).
