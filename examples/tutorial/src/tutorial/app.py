# We can import the real module now
from tutorial.templates import IndexHtmlJ2Context, render_index_html_j2


def main() -> None:
    # We annotate our payload dictionary with the generated stub type
    context: IndexHtmlJ2Context = {
        "title": "Welcome Home",
        "items": ["User", "Settings", "Logout"],
        # Oh no! We accidentally provided "blue" instead of "light" or "dark".
        "theme": "dark",
    }

    html = render_index_html_j2(**context)
    print(html)


if __name__ == "__main__":
    main()
