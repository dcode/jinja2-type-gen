# Typical Example

This directory contains a standalone `uv` workspace project that demonstrates how to use the `jinja2-type-gen` library. This builds upon the `simple` example by using a typical `src` package layout, including separate `tests/` and `templates/` directories.

## Structure

- **`src/typical_example/core.py`**: Contains the logic to instantiate the Jinja Environment and analyze/render templates.
- **`templates/`**: Contains the Jinja templates.
  - `base.j2`: The layout base template.
  - `index.j2`: The child template showing the `{% signature ... %}` block.
- **`tests/`**: Contains an example test for the functionality.
- **`example.py`**: The runner script.

## Running the Example

Make sure you are in this directory, then run:

```bash
uv run example.py
```

To run the unit tests:

```bash
uv run pytest
```
