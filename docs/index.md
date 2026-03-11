# jinja2-type-gen

Strict, compile-time/static type safety for Jinja2 templates without compromising runtime performance.

## Overview

`jinja2-type-gen` bridges the gap between static Python analysis (Mypy/Pyright) and dynamic template metaprogramming. During CI/CD or language server execution, templates are parsed to construct `.pyi` stub files that denote the precise context variables required to render a template. During live execution, the `SignatureExtension` processes the type annotations but emits **zero bytecode**, ensuring execution incurs zero latency overhead compared to a standard Jinja string.

## Core Features

- **Zero Runtime Overhead:** Execution incurs zero latency overhead compared to a standard Jinja string.
- **Advanced Scoping:** Variables declared globally in `{% signature %}` do not pollute nested `{% macro %}` scopes or local `{% set %}` scopes.
- **Template Inheritance:** Securely merges signatures when templates use `{% extends "base.j2" %}`. A required variable in the base template bubbles up to the child template's signature.
- **Cross-Template Validation:** Ensures type consistency when data is passed via `{% include "partial.j2" %}`.
- **CLI/Pre-commit Tooling:** A CLI entrypoint and pre-commit hook automatically scans directories to generate `templates.pyi` `TypedDict` stubs.

## Setup

1. Install the package:

```bash
pip install jinja2-type-gen
```

2. Register the extension in your application's Jinja `Environment`:

```python
from jinja2 import Environment
from jinja2_type_gen import SignatureExtension

env = Environment(extensions=[SignatureExtension])
```

## Basic Usage

Embed a `{% signature %}` block within your `index.j2` file using native Python 3 type hints:

```html+jinja

{% signature
    title: str,
    items: list[str],
    is_admin: bool = False
%}
<h1>{{ title }}</h1>
<ul>
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
</ul>
```

Generate type stubs via the CLI:

```bash
jinja2-type-gen generate src/templates/ --output src/templates.pyi
```
