# Contributing to `jinja2-type-gen`

Welcome, Developer. This guide explains the core design philosophy and technical boundaries of `jinja2-type-gen`. We build for Python 3.14+ utilizing the latest language features for maximum performance and strict typing.

## Design Philosophy

This project bridges formal grammar/parsing theory with the internal mechanics of the Jinja2 templating engine. We operate under the following mandates:

1. **JIT Compatibility (Python 3.14+)**: Hot paths are designed to be friendly to CPython's Tier 2 optimizer. We prefer concrete types, `__slots__`, and localized variable lookups over dynamic dispatch.
1. **Safety & Efficiency First**: Our AST analysis must be bounded. We avoid arbitrary recursion to prevent `RecursionError` on malicious or deeply nested inputs. Parsing operations prefer string references and memoryviews where applicable.
1. **Strict Typing**: Every new module or function must utilize precise Type Hinting (PEP 695 type aliases, `Self`, `Unpack`).
1. **Sandbox Isolation**: Template evaluation during analysis is strictly prohibited. We parse to Internal-land AST using an `ImmutableSandboxedEnvironment`.

## Understanding the AST Transformation

When contributing to the `analyzer.py` or `extension.py`, understand that we are operating in Jinja's "Internal-land".

- **User-land**: The syntax developers write (e.g., `{% signature foo: int %}`).
- **Internal-land**: The `nodes.Node` tree Jinja constructs.

The `SignatureExtension` does *not* create a custom AST node because doing so can complicate compilation. Instead, it parses the tag, validates it using Python's native `ast` module, and returns a standard `nodes.Output` node populated with an empty string `nodes.Const("")`. It attaches metadata to this node (`signature_metadata`). This guarantees $O(1)$ runtime cost and eliminates potential code execution (RCE prevention).

## Setting Up

1. Clone the repository.
1. Ensure you have Python 3.14+ installed.
1. We recommend using `uv` for dependency management.
1. Run `pytest` to execute the test suite.

## Code Style & Testing

- Format code using `ruff`.
- All new functionality must be accompanied by comprehensive `pytest` cases. Include "unhappy paths", such as malformed syntax or deep nesting.
- When adding complex algorithms, document the time complexity ($O(n)$) and space complexity in the docstring.

Thank you for helping us maintain a safe, high-performance static analyzer.
