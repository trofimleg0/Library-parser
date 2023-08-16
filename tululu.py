import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin
from pathvalidate import sanitize_filepath


def parse_one_page(soup, url):
    relative_book_img_url = soup.find(class_="bookimage").find("img")["src"]
    absolute_book_img_url = urljoin(url, relative_book_img_url)

    book_name_and_author = (
        soup.find("td", class_="ow_px_td")
        .find("div", id="content")
        .find("h1")
        .text.split("::")
    )
    book_name, author = map(str.strip, book_name_and_author)
    book_genres_soup = soup.find("span", class_="d_book").find_all("a")

    book_genres = []
    for book_genre_soup in book_genres_soup:
        book_genres.append(book_genre_soup.text)

    print("Заголовок: ", book_name)
    print("Автор: ", author)
    print("Жанр: ", book_genres)

    return absolute_book_img_url, relative_book_img_url, book_name


def download_image(url, book_img_path, path):
    response = requests.get(url)
    response.raise_for_status()

    image_path = os.path.join(path, "images")
    Path(image_path).mkdir(parents=True, exist_ok=True)

    if not check_for_redirect(response):
        book_img_name = book_img_path.split("/")[-1]
        with open(f"{image_path}/{book_img_name}", "wb") as file:
            file.write(response.content)


def download_txt(book_id, filename, path):
    url = "https://tululu.org/txt.php"
    params = {"id": book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()

    book_path = os.path.join(path, "books")
    Path(book_path).mkdir(parents=True, exist_ok=True)

    if not check_for_redirect(response):
        book_name = sanitize_filepath(filename)
        with open(f"{book_path}/{book_name}.txt", "w") as file:
            file.write(response.text)


def check_for_redirect(response):
    if len(response.history) > 0:
        return True
    return False


if __name__ == "__main__":
    load_dotenv()
    path = os.environ["WD"]

    for book_id in range(1, 11):
        url = f"https://tululu.org/b{book_id}/"
        try:
            response = requests.get(url)
            response.raise_for_status()

            if not check_for_redirect(response):
                soup = BeautifulSoup(response.text, "lxml")
                (
                    absolute_book_img_url,
                    relative_book_img_url,
                    book_name,
                ) = parse_one_page(soup, url)

                download_image(
                    absolute_book_img_url, relative_book_img_url, path
                )
                download_txt(book_id, f"{book_id}.{book_name}", path)
        except Exception as ex:
            raise requests.exceptions.HTTPError(ex)
