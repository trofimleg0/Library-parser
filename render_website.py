import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked

def on_reload():
    with open("books_info_by_category.json", "r") as file:
        books = json.loads(file.read())
    env = Environment(
        loader=FileSystemLoader("."), autoescape=select_autoescape(["html"])
    )

    grouped_books = list(chunked(books, 2))
    template = env.get_template("template.html")
    rendered_page = template.render(grouped_books=grouped_books)

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == "__main__":
    on_reload()

    server = Server()
    server.watch("./template.html", on_reload)
    server.serve(root=".")
