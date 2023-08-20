import json
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_books_params(filename):
    with open(filename, 'r') as file:
        books = json.loads(file.read())
    return books


if __name__ == '__main__':
    books = get_books_params("books_info_by_category.json")
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')
    rendered_page = template.render(books=books)

    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)
