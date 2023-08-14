import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from pathvalidate import sanitize_filepath


def download_txt(book_id, filename):
    url = "https://tululu.org/txt.php"
    params = {"id": book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    if not check_for_redirect(response):
        book_name = sanitize_filepath(filename)
        with open(f"{image_path}{book_name}.txt", "w") as file:
            file.write(response.text)


def check_for_redirect(response):
    if len(response.history) > 0:
        return True
    return False


if __name__ == "__main__":
    load_dotenv()

    image_path = os.environ["IMAGE_PATH"]
    Path(image_path).mkdir(parents=True, exist_ok=True)

    for book_id in range(1, 11):
        url = f"https://tululu.org/b{book_id}/"
        try:
            response = requests.get(url)
            response.raise_for_status()

            if not check_for_redirect(response):
                soup = BeautifulSoup(response.text, "lxml")
                book_name_and_author = (
                    soup.find("td", class_="ow_px_td")
                    .find("div", id="content")
                    .find("h1")
                    .text.split("::")
                )
                book_name, author = map(str.strip, book_name_and_author)
                download_txt(book_id, f"{book_id}.{book_name}")

        except Exception as ex:
            raise requests.exceptions.HTTPError(ex)
