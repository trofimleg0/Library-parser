import os
import json
import requests

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from dotenv import load_dotenv
from urllib.parse import urljoin
from parse_tululu import (
    check_for_redirect,
    download_image,
    download_txt,
    get_book_params,
)


def get_args():
    parser = ArgumentParser("Select a range of pages to download books")
    parser.add_argument(
        "-s", "--start_page", default="1", type=int, help="Pages start range"
    )
    parser.add_argument(
        "-e", "--end_page", default="4", type=int, help="Pages end range"
    )
    args = parser.parse_args()

    return args.start_page, args.end_page


def extract_number_from_string(input_string):
    number = "".join(filter(str.isdigit, input_string))
    return int(number) if number else None


if __name__ == "__main__":
    load_dotenv()
    path = os.environ["WD"]
    books_folder_name = os.environ["BOOKS"]
    images_folder_name = os.environ["IMAGES"]

    start_page, end_page = get_args()
    all_books_params = []
    for page in range(start_page, end_page + 1):
        url = f"https://tululu.org/l55/{page}/"
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

                if not check_for_redirect(response):
                    soup = BeautifulSoup(response.text, "lxml")
                    (
                        title,
                        author,
                        genres,
                        comments,
                        img_name,
                        img_src,
                        book_path,
                        img_url,
                    ) = get_book_params(
                        soup, url, books_folder_name, images_folder_name
                    )
                    book_params = {
                        "title": title,
                        "author": author,
                        "genres": genres,
                        "comments": comments,
                        "img_src": img_src,
                        "book_path": book_path,
                    }
                    all_books_params.append(book_params)
                    book_id = extract_number_from_string(relative_book_url)
                    # download_image(img_url, img_name, path, images_folder_name)
                    # download_txt(book_id, f"{book_id}.{title}", path, books_folder_name)
        except Exception as ex:
            raise requests.exceptions.HTTPError(ex)
    all_books_params_json = "books_info_by_category.json"
    with open(f"{path}/{all_books_params_json}", "w") as file:
        file.write(json.dumps(all_books_params, ensure_ascii=False))
