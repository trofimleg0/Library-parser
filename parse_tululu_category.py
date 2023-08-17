import os
import requests

from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urljoin
from argparse import ArgumentParser
from pathvalidate import sanitize_filepath

if __name__ == "__main__":
    for page in range(1, 4):
        url = f"https://tululu.org/l55/{page}/"
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            relative_book_urls = soup.find("div", id="content").find_all(
                "table", class_="d_book"
            )
            for relative_book_url in relative_book_urls:
                book_url = urljoin(url, relative_book_url.find("a")["href"])
                response = requests.get(book_url)
                response.raise_for_status()
                print(book_url)
        except Exception as ex:
            raise requests.exceptions.HTTPError(ex)
