import os
import json
import requests

from bs4 import BeautifulSoup
from argparse import ArgumentParser
from urllib.error import URLError
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin
from pathvalidate import sanitize_filepath


def get_args():
    parser = ArgumentParser("Select a range of IDs to download books")
    parser.add_argument(
        "-s",
        "--start_id",
        default="1",
        type=int,
        help="Starting range of IDs to download",
    )
    parser.add_argument(
        "-e",
        "--end_id",
        default="10",
        type=int,
        help="Ending range of IDs to download",
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


def check_for_redirect(response):
    if response.history:
        raise URLError("Url not found")


def get_book_params(soup, url):
    relative_img_url = soup.select_one(".bookimage img")["src"]
    img_url = urljoin(url, relative_img_url)
    img_name = relative_img_url.split("/")[-1]

    title_and_author = soup.select_one("body h1").text.split("::")
    title, author = map(str.strip, title_and_author)

    genres_soup = soup.select("span.d_book a")
    genres = [genre.text for genre in genres_soup]

    comments_soup = soup.select(".texts span")
    comments = [comment.text for comment in comments_soup]

    return (
        title,
        author,
        genres,
        comments,
        img_name,
        img_url,
    )


def download_image(url, img_name, imgs_folder):
    response = requests.get(url)
    response.raise_for_status()

    check_for_redirect(response)
    img_path = f"{imgs_folder}/{img_name}"
    with open(img_path, "wb") as file:
        file.write(response.content)
    return img_path


def download_txt(book_id, filename, books_folder_path):
    url = "https://tululu.org/txt.php"
    params = {"id": book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()

    check_for_redirect(response)
    book_name = sanitize_filepath(filename)
    book_path = f"{books_folder_path}/{book_name}.txt"
    with open(book_path, "w") as file:
        file.write(response.text)
    return book_path


def download_json(all_books_params, path, filename):
    with open(f"{path}/{filename}", "w") as file:
        file.write(json.dumps(all_books_params, ensure_ascii=False))


if __name__ == "__main__":
    load_dotenv()

    args = get_args()
    path = args.dest_folder

    imgs_folder_path = os.path.join(path, "all_category_images")
    books_folder_path = os.path.join(path, "all_category_books")
    Path(imgs_folder_path).mkdir(parents=True, exist_ok=True)
    Path(books_folder_path).mkdir(parents=True, exist_ok=True)

    all_books_params = []
    for book_id in range(args.start_id, args.end_id + 1):
        url = f"https://tululu.org/b{book_id}/"
        try:
            response = requests.get(url)
            response.raise_for_status()

            check_for_redirect(response)
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
                img_src = download_image(img_url, img_name, imgs_folder_path)
            if not args.skip_txt:
                filename = f"{book_id}.{title}"
                book_path = download_txt(book_id, filename, books_folder_path)

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
    download_json(all_books_params, path, "all_category_books_info.json")
