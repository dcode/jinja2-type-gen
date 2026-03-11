from typing import TYPE_CHECKING
from jinja2 import Environment, PackageLoader

from jinja2_type_gen import SignatureExtension, TemplateTypeAnalyzer

if TYPE_CHECKING:
    from typical_example.templates import IndexJ2Context


def get_environment() -> Environment:
    """Configures and returns a dedicated Jinja Environment with SignatureExtension."""
    return Environment(
        loader=PackageLoader("typical_example", "templates"),
        extensions=[SignatureExtension],
        autoescape=True,
    )


def extract_types_from_template(env: Environment, template_name: str) -> dict:
    """Extracts type signatures using the template source."""
    if env.loader is None:
        raise ValueError("Environment loader is None")
    source, _, _ = env.loader.get_source(env, template_name)
    analyzer = TemplateTypeAnalyzer()
    return analyzer.analyze_source(source)


def render_index(env: Environment, context: "IndexJ2Context") -> str:
    """Renders the index template using the strictly typed context."""
    template = env.get_template("index.j2")
    return template.render(**context)
