# jinja2-type-gen

> High-performance static analysis for Jinja2. Target: Python 3.14+

Generate Python type signatures (`TypedDict` via PEP 589) and initialization functions from Jinja2 templates, enabling zero-cost type safety for your templating engine.

## The Architecture

`jinja2-type-gen` is engineered as a zero-copy, linear-time AST parser. It operates entirely in Jinja's "Internal-land", intercepting the token stream via `SignatureExtension` and generating an empty `nodes.Output`. This guarantees **zero runtime execution cost** and absolute protection against arbitrary code execution (RCE) via our `ImmutableSandboxedEnvironment`.

See [ARCHITECTURE.md](ARCHITECTURE.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for deep dives into the AST transformation pipeline.

## Features

- **JIT-Optimized AST Traversal:** Leverages Python 3.14+ structural pattern matching, `__slots__`, and an iterative stack-based traversal to eliminate `RecursionError` on deeply nested trees.
- **Strict Typing:** Outputs compliant Python 3.14+ `TypedDict` structures for your context dictionaries, supporting `Unpack` and `NotRequired`.
- **Sandbox Security:** The type extraction is purely static. The signature syntax is verified via python's native `ast` module at compilation time.
- **Rendering Shims:** Generates type-safe wrapper modules (`__init__.py`) containing functions that force static evaluation of template arguments in your IDE.

## Installation

```bash
uv tool install jinja2-type-gen
# or
pip install jinja2-type-gen
```

## Usage

### Command-Line Interface

Analyze a directory of templates and generate type stubs:

```bash
jinja2-type-gen generate ./src/templates/ --output ./src/templates.pyi
```

Generate type stubs along with helper rendering functions:

```bash
jinja2-type-gen generate ./src/templates/ --output ./src/templates/__init__.py --create-renderers
```

### Pre-commit Hook

Add the following to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/dcode/jinja2-type-gen
    rev: v0.1.0 # Use the latest version
    hooks:
      - id: jinja2-type-gen
        args: ["./src/templates/", "--output", "./src/templates.pyi"]
```

## Performance & Safety Audit

The core static analyzer runs in $O(N)$ time relative to the number of AST nodes. It natively resolves `include` and `extends` statements iteratively. By binding to `ImmutableSandboxedEnvironment`, we enforce strict parsing boundaries.

## License

BSD-3-Clause
