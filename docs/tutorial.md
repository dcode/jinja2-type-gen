# Step-by-Step Tutorial

Welcome to `jinja2-type-gen`! This tutorial will walk you through a practical, end-to-end example of how to configure compile-time type safety for your Jinja2 templates.

By the end of this tutorial, you will have:

1. Written a Jinja template with explicit type requirements.
1. Automatically generated a static Python type stub (`.pyi`) directly from the template.
1. Hooked the stub into your Python application to get instant Mypy/Pyright feedback when you pass incorrect data to the template context.

______________________________________________________________________

## 1. Setup Your Template

First, let's create a simple Jinja2 template and use the `{% signature %}` tag. This tag tells the `jinja2-type-gen` engine what context variables this template requires to render correctly.

Create a file named `templates/index.j2` with the following content:

```jinja title="templates/index.j2"
{% signature
    title: str,
    items: list[str],
    theme: Literal["light", "dark"] = "light"
%}

<h1>{{ title }}</h1>
<ul>
    {% for item in items %}
        <li>{{ item }}</li>
    {% endfor %}
</ul>
```

> \[!NOTE\]
> The `{% signature %}` block is purely metadata. At runtime, the `SignatureExtension` compiles this tag down to a zero-cost empty node, meaning it adds **no overhead** to your application's rendering pipeline.

______________________________________________________________________

## 2. Generate the Type Stubs

Instead of manually keeping your Python code in sync with your templates, `jinja2-type-gen` provides a CLI generation tool to inspect your templates and write `.pyi` type stubs automatically.

Run the following command against your template directory:

```bash
uv run jinja2-type-gen generate templates/ --output templates.pyi
```

Alternatively, if you use `pre-commit`, you can automate this check on every commit by adding the native hook to your `.pre-commit-config.yaml`:

```yaml title=".pre-commit-config.yaml"
repos:
  - repo: https://github.com/dcode/jinja2-type-gen
    rev: v0.1.0 # Use the latest release
    hooks:
      - id: jinja2-type-gen
        entry: jinja2-type-gen generate templates/ --output templates.pyi
        pass_filenames: false
```

Inside `templates.pyi`, you'll see a generated class `IndexJ2Context(TypedDict)` that strictly maps your template variables into native Python `typing` constructs:

```python title="templates.pyi"
from typing import Literal, NotRequired, TypedDict

class IndexJ2Context(TypedDict):
    title: str
    items: list[str]
    theme: NotRequired[Literal['light', 'dark']]
```

______________________________________________________________________

## 3. Link the Stubs into Python

Now that we have statically generated bounds for `index.j2`, let's wire it up inside an application. The goal is to enforce the dictionary shape of our context *before* it is passed to `template.render()`.

To prevent the `.pyi` file from affecting our application at execution runtime, we import the types strictly under Python's `TYPE_CHECKING` block.

Create or update your `app.py`:

```python title="app.py"
from typing import TYPE_CHECKING
from jinja2 import Environment, FileSystemLoader
from jinja2_type_gen import SignatureExtension

# Only import the stubs during static analysis (Mypy/Pyright/IDE)
if TYPE_CHECKING:
    from templates import IndexJ2Context

def main():
    env = Environment(
        loader=FileSystemLoader("templates"),
        extensions=[SignatureExtension]
    )
    template = env.get_template("index.j2")

    # We annotate our payload dictionary with the generated stub type
    context: "IndexJ2Context" = {
        "title": "Welcome Home",
        "items": ["User", "Settings", "Logout"],
        # Oh no! We accidentally provided "blue" instead of "light" or "dark".
        "theme": "blue",
    }

    html = template.render(**context)
    print(html)

if __name__ == "__main__":
    main()
```

______________________________________________________________________

## 4. Catch Errors with Static Analysis

Because `context` is mapped directly to our `IndexJ2Context` type dictionary, any modern IDE (like VSCode with Pylance) will instantly highlight the `theme: "blue"` line as an error.

To catch it in CI/CD, run `mypy`:

```bash
uv run mypy app.py
```

You will see an error identifying exactly where your Python code drifted from the template's requirements:

```text
app.py:19: error: Incompatible types (expression has type "str", TypedDict item "theme" has type "Literal['light', 'dark']")  [typeddict-item]
```

And that's it! You've successfully established a zero-overhead, strictly aligned boundary between your Jinja2 views and Python controllers.
