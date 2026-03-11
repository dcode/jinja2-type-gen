# AUTO-GENERATED FILE. DO NOT EDIT.
# fmt: off
# isort: skip_file
# ruff: noqa

from typing import Any, Literal, NotRequired, TypedDict, Unpack
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import pydantic


class FooMdJ2Context(TypedDict):
    title: str
    things: list[str]
    now: pydantic.AwareDatetime
class IndexHtmlJ2Context(TypedDict):
    title: str
    items: list[str]
    theme: NotRequired[Literal["light", "dark"]]

_JINJA_ENV: Environment | None = None

def configure_environment(**kwargs: Any) -> Environment:
    """
    Configure and return a Jinja2 Environment.
    """
    global _JINJA_ENV
    from jinja2_type_gen.extension import SignatureExtension

    # 1. Safely extract the user's extensions (defaulting to an empty list)
    user_extensions = list(kwargs.pop("extensions", []))
    # 2. Append our extension if it isn't already there
    if (
        SignatureExtension not in user_extensions
        and "jinja2_type_gen.extension.SignatureExtension" not in user_extensions
    ):
        user_extensions.append(SignatureExtension)

    # 3. Put the merged list back into kwargs
    kwargs["extensions"] = user_extensions
    # 4. Merge with defaults
    template_dir = (Path(__file__).parent / ".").resolve()
    defaults = {
        "loader": FileSystemLoader(template_dir),
        "autoescape": True,
    }
    _JINJA_ENV = Environment(**{**defaults, **kwargs})
    return _JINJA_ENV


def _get_jinja_env() -> Environment:
    """
    Internal getter used by rendering functions.
    Initializes lazy-loading if configure_environment() hasn't been called.
    """
    if _JINJA_ENV is None:
        return configure_environment()
    return _JINJA_ENV


def render_foo_md_j2(**context: Unpack[FooMdJ2Context]) -> str:
    return _get_jinja_env().get_template("foo.md.j2").render(**context)

def render_index_html_j2(**context: Unpack[IndexHtmlJ2Context]) -> str:
    return _get_jinja_env().get_template("index.html.j2").render(**context)
