from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from jinja2_type_gen.analyzer import TemplateTypeAnalyzer
from jinja2_type_gen.extension import SignatureExtension


def generate_stubs(
    directory: Path, output_file: Path, create_renderers: bool = False
) -> int:
    if not directory.is_dir():
        print(f"Error: Directory '{directory}' does not exist.", file=sys.stderr)
        return 1

    env = Environment(
        loader=FileSystemLoader(str(directory)), extensions=[SignatureExtension]
    )
    analyzer = TemplateTypeAnalyzer(env=env)

    try:
        assert env.loader is not None
        templates = env.loader.list_templates()
    except Exception as e:
        print(f"Error listing templates: {e}", file=sys.stderr)
        return 1

    stub_lines = []
    needed_imports = {"TypedDict"}
    needed_modules: set[str] = set()

    if create_renderers:
        needed_imports.update({"Any", "Unpack"})

        rel_to_dir = os.path.relpath(directory, output_file.parent)
        if hasattr(os, "name") and os.name == "nt":
            rel_to_dir = rel_to_dir.replace("\\", "/")

        renderer_lines = [
            "_JINJA_ENV: Environment | None = None",
            "",
            "def configure_environment(**kwargs: Any) -> Environment:",
            '    """',
            "    Configure and return a Jinja2 Environment.",
            '    """',
            "    global _JINJA_ENV",
            "    from jinja2_type_gen.extension import SignatureExtension",
            "",
            "    # 1. Safely extract the user's extensions (defaulting to an empty list)",
            '    user_extensions = list(kwargs.pop("extensions", []))',
            "    # 2. Append our extension if it isn't already there",
            "    if (",
            "        SignatureExtension not in user_extensions",
            '        and "jinja2_type_gen.extension.SignatureExtension" not in user_extensions',
            "    ):",
            "        user_extensions.append(SignatureExtension)",
            "",
            "    # 3. Put the merged list back into kwargs",
            '    kwargs["extensions"] = user_extensions',
            "    # 4. Merge with defaults",
            f'    template_dir = (Path(__file__).parent / "{rel_to_dir}").resolve()',
            "    defaults = {",
            '        "loader": FileSystemLoader(template_dir),',
            '        "autoescape": True,',
            "    }",
            "    _JINJA_ENV = Environment(**{**defaults, **kwargs})",
            "    return _JINJA_ENV",
            "",
            "",
            "def _get_jinja_env() -> Environment:",
            '    """',
            "    Internal getter used by rendering functions.",
            "    Initializes lazy-loading if configure_environment() hasn't been called.",
            '    """',
            "    if _JINJA_ENV is None:",
            "        return configure_environment()",
            "    return _JINJA_ENV",
            "",
            "",
        ]
    else:
        renderer_lines = []

    has_errors = False
    first_template = True
    for template_name in templates:
        if not (template_name.endswith(".j2") or template_name.endswith(".html")):
            continue

        try:
            source, _, _ = env.loader.get_source(env, template_name)
            types = analyzer.analyze_source(source)
        except Exception as e:
            print(f"Error analyzing '{template_name}': {e}", file=sys.stderr)
            has_errors = True
            continue

        if not types:
            continue

        class_name = "".join(
            part.title()
            for part in template_name.replace("/", "_").replace(".", "_").split("_")
        )
        class_name += "Context"

        if not first_template:
            stub_lines.extend(["", ""])
        stub_lines.append(f"class {class_name}(TypedDict):")
        for var_name, type_info in types.items():
            # Ruff demands double quotes
            type_str = type_info["type"].replace("'", '"')

            if "Any" in type_str:
                needed_imports.add("Any")
            if "Callable" in type_str:
                needed_imports.add("Callable")
            if "Literal" in type_str:
                needed_imports.add("Literal")

            if not type_info["required"]:
                type_str = f"NotRequired[{type_str}]"
                needed_imports.add("NotRequired")

            import re

            for match in re.finditer(
                r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.[a-zA-Z_]", type_str
            ):
                needed_modules.add(match.group(1))

            stub_lines.append(f"    {var_name}: {type_str}")

        if create_renderers:
            function_name = "render_" + template_name.replace("/", "_").replace(
                ".", "_"
            ).replace("\\", "_")
            renderer_lines.append(
                f"def {function_name}(**context: Unpack[{class_name}]) -> str:"
            )
            renderer_lines.append(
                f'    return _get_jinja_env().get_template("{template_name}").render(**context)'
            )
            renderer_lines.append("")

    if has_errors:
        return 1

    import_line = "from typing import " + ", ".join(sorted(needed_imports))
    final_lines = [
        "# AUTO-GENERATED FILE. DO NOT EDIT.",
        "# fmt: off",
        "# isort: skip_file",
        "# ruff: noqa",
        "",
        import_line,
    ]
    if create_renderers:
        final_lines.append("from pathlib import Path")
        final_lines.append("from jinja2 import Environment, FileSystemLoader")

    if needed_modules:
        for mod in sorted(needed_modules):
            final_lines.append(f"import {mod}")

    final_lines.extend(["", ""] + stub_lines + [""] + renderer_lines)
    output_content = "\n".join(final_lines)
    if not output_content.endswith("\n"):
        output_content += "\n"

    if output_file.exists() and output_file.read_text() == output_content:
        print(f"Stubs in {output_file} are already up-to-date.")
        return 0

    output_file.write_text(output_content)
    print(f"Generated updated {output_file}")
    # Return 1 to indicate files were modified (important for pre-commit hooks
    # since we run with pass_filenames: false)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Jinja2 Type Signature Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser(
        "generate", help="Generate .pyi stubs from template directory"
    )
    generate_parser.add_argument(
        "directory", help="The directory containing .j2 templates"
    )
    generate_parser.add_argument(
        "--output", default="templates.pyi", help="The output stub file name"
    )
    generate_parser.add_argument(
        "--create-renderers",
        action="store_true",
        help="Generate functional render modules",
    )

    args = parser.parse_args(argv)

    if args.command == "generate":
        return generate_stubs(
            Path(args.directory), Path(args.output), args.create_renderers
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
