import os
import json
import requests

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin
from pathvalidate import sanitize_filepath


def get_args():
    parser = ArgumentParser("Select a range of IDs to download books")
    parser.add_argument(
        "-s", "--start_id", default="1", type=int, help="IDs start range"
    )
    parser.add_argument(
        "-e", "--end_id", default="10", type=int, help="IDs end range"
    )
    parser.add_argument(
        "-d", "--dest_folder", default=".", type=str, help="The path where the parsing result will be recorded"
    )
    parser.add_argument(
        "-i", "--skip_imgs", default=False, type=bool, help="Allows you not to download images if state=True"
    )
    parser.add_argument(
        "-t", "--skip_txt", default=False, type=bool, help="Allows you not to download books is state=True"
    )

    return parser.parse_args()


def check_for_redirect(response):
    if len(response.history) > 0:
        return True
    return False


def get_book_params(soup, url, books_folder, images_folder):
    relative_img_url = soup.select_one(".bookimage img")["src"]
    img_url = urljoin(url, relative_img_url)
    img_name = relative_img_url.split("/")[-1]

    title_and_author = soup.select_one("body h1").text.split("::")
    title, author = map(str.strip, title_and_author)

    genres_soup = soup.select("span.d_book a")
    genres = [genre.text for genre in genres_soup]

    comments_soup = soup.select(".texts span")
    comments = [comment.text for comment in comments_soup]

    img_src = os.path.join(images_folder, img_name)
    book_path = os.path.join(books_folder, sanitize_filepath(title))

    return (
        title,
        author,
        genres,
        comments,
        img_name,
        img_src,
        book_path,
        img_url,
    )


def download_image(url, img_name, path, images_folder_name):
    response = requests.get(url)
    response.raise_for_status()

    img_path = os.path.join(path, images_folder_name)
    Path(img_path).mkdir(parents=True, exist_ok=True)
    if not check_for_redirect(response):
        with open(f"{img_path}/{img_name}", "wb") as file:
            file.write(response.content)


def download_txt(book_id, filename, path, books_folder_name):
    url = "https://tululu.org/txt.php"
    params = {"id": book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()

    book_path = os.path.join(path, books_folder_name)
    Path(book_path).mkdir(parents=True, exist_ok=True)
    if not check_for_redirect(response):
        book_name = sanitize_filepath(filename)
        with open(f"{book_path}/{book_name}.txt", "w") as file:
            file.write(response.text)


def download_json(all_books_params, path, filename):
    with open(f"{path}/{filename}", "w") as file:
        file.write(json.dumps(all_books_params, ensure_ascii=False))


if __name__ == "__main__":
    load_dotenv()
    args = get_args()
    path = args.dest_folder
    books_folder_name = "books"
    images_folder_name = "images"
    
    all_books_params = []
    for book_id in range(args.start_id, args.end_id + 1):
        url = f"https://tululu.org/b{book_id}/"
        try:
            response = requests.get(url)
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
                if not args.skip_imgs:
                    download_image(img_url, img_name, path, images_folder_name)
                if not args.skip_txt:
                    download_txt(book_id, f"{book_id}.{title}", path, books_folder_name)
        except Exception as ex:
            raise requests.exceptions.HTTPError(ex)
    download_json(all_books_params, path, "books_info.json")
