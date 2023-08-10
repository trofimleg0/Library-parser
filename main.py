import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.error import URLError

def check_for_redirect(response):
    if len(response.history) > 0:
        return True
    return False

if __name__ == '__main__':
    load_dotenv()

    image_path = os.environ['IMAGE_PATH']
    Path(image_path).mkdir(parents=True, exist_ok=True)
    
    
    for book_id in range(1, 11):
        url = f'https://tululu.org/txt.php?id={book_id}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            if not check_for_redirect(response):
                with open(f'{image_path}/id{book_id}.txt', 'w') as file:
                    file.write(response.text)
        except Exception as ex:
            raise requests.exceptions.HTTPError(ex)
        