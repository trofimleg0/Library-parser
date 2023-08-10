import os
import requests
from pathlib import Path
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()

    image_path = os.environ['IMAGE_PATH']
    Path(image_path).mkdir(parents=True, exist_ok=True)
    
    for i in range(1, 11):
        with open(f'{image_path}/id{i}.txt', 'w') as file:
            url = f'https://tululu.org/txt.php?id={i}'
            response = requests.get(url)
            response.raise_for_status()
            file.write(response.text)
