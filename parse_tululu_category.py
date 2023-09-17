import os
import requests

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from urllib.error import URLError
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin
from parse_tululu import (
    check_for_redirect,
    download_image,
    download_txt,
    download_json,
    get_book_params,
)


def get_args():
    parser = ArgumentParser("Select a range of pages to download books")
    parser.add_argument(
        "-s", "--start_page", default=1, type=int, help="Start page range"
    )
    parser.add_argument(
        "-e", "--end_page", default=1, type=int, help="End page range"
    )
    parser.add_argument(
        "-c",
        "--category_id",
        default=55,
        type=int,
        help="ID of the book category",
    )
    parser.add_argument(
        "-d",
        "--dest_folder",
        default=".",
        type=str,
        help="The path where the parsing result will be recorded",
    )
    parser.add_argument(
        "-i",
        "--skip_imgs",
        default=False,
        type=bool,
        help="Allows you not to download images if it's True",
    )
    parser.add_argument(
        "-t",
        "--skip_txt",
        default=False,
        type=bool,
        help="Allows you not to download books if it's True",
    )

    return parser.parse_args()


def get_book_id(relative_book_url):
    book_id = "".join(filter(str.isdigit, relative_book_url))
    return int(book_id) if book_id else None


if __name__ == "__main__":
    load_dotenv()
    args = get_args()
    path = args.dest_folder

    imgs_folder_path = os.path.join(path, "images")
    books_folder_path = os.path.join(path, "books")
    Path(imgs_folder_path).mkdir(parents=True, exist_ok=True)
    Path(books_folder_path).mkdir(parents=True, exist_ok=True)

    all_books_params = []
    for page in range(args.start_page, args.end_page + 1):
        url = f"https://tululu.org/l{args.category_id}/{page}/"
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            soup_book_urls = soup.find("div", id="content").find_all(
                "table", class_="d_book"
            )

            for soup_book_url in soup_book_urls:
                relative_book_url = soup_book_url.find("a")["href"]
                book_url = urljoin(url, relative_book_url)
                response = requests.get(book_url)
                response.raise_for_status()

                check_for_redirect(response)
                book_id = get_book_id(relative_book_url)
                soup = BeautifulSoup(response.text, "lxml")
                (
                    title,
                    author,
                    genres,
                    comments,
                    img_name,
                    img_url,
                ) = get_book_params(soup, url)

                if not args.skip_imgs:
                    img_src = download_image(
                        img_url, img_name, imgs_folder_path
                    )
                if not args.skip_txt:
                    filename = f"{book_id}.{title}"
                    book_path = download_txt(
                        book_id, filename, books_folder_path
                    )

                book_params = {
                    "title": title,
                    "author": author,
                    "genres": genres,
                    "comments": comments,
                    "img_src": os.path.relpath(img_src),
                    "book_path": os.path.relpath(book_path),
                }
                all_books_params.append(book_params)
        except URLError:
            print(f"{url} - Book not found")
            continue
        except Exception as ex:
            raise requests.exceptions.HTTPError(ex)
    download_json(all_books_params, path, "books_info.json")
