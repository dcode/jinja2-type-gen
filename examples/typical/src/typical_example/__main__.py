import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Provide direct access to demo the local files without forcing an install step.
# In a real environment, you'd just `pip install .` inside this directory.
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


from typical_example.core import (  # noqa: E402
    extract_types_from_template,
    get_environment,
    render_index,
)

if TYPE_CHECKING:
    from typical_example.templates import IndexJ2Context


def main() -> None:
    env = get_environment()

    print("--- 1. Static Analysis Phase ---")
    print("Extracting Type Information from AST...")

    extracted_types = extract_types_from_template(env, "index.j2")

    print("\nGenerated details for 'index.j2':")
    for var_name, type_info in extracted_types.items():
        req_str = "Required" if type_info["required"] else "Optional"
        print(f"  - {var_name}: {type_info['type']} ({req_str})")

    print("\n--- 2. Runtime Execution Phase ---")
    print("Rendering 'index.j2' via Python...")

    # We use our statically valid TypedDict. If we passed the wrong types,
    # Mypy/Pyright would complain during CI/CD.
    context: "IndexJ2Context" = {
        "title": "Welcome to typical_example!",
        "items": ["First Item", "Second Item", "Third Item"],
        "theme": "blue",
    }

    # At runtime, zero bytecode is emitted for the `{% signature %}` block.
    rendered = render_index(env, context)

    print("\nRendered Output:")
    print("=" * 40)
    print(rendered.strip())
    print("=" * 40)


if __name__ == "__main__":
    main()
