import pytest
from jinja2 import Environment

from jinja2_type_gen import SignatureExtension


def test_signature_extension_compiles_out():
    env = Environment(extensions=[SignatureExtension])

    template_source = """
Hello {% signature user: str, count: int = 1 %}World!
"""

    template = env.from_string(template_source)
    result = template.render()

    # It should render perfectly and the signature should not appear
    assert result.strip() == "Hello World!"


def test_signature_syntax_error():
    env = Environment(extensions=[SignatureExtension])

    template_source = """
Hello {% signature user: str, 123 invalid %}World!
"""

    from jinja2.exceptions import TemplateSyntaxError

    with (
        pytest.raises(TemplateSyntaxError, match="Invalid python signature syntax"),
        pytest.warns((SyntaxWarning, DeprecationWarning), match="invalid decimal literal"),
    ):
        env.from_string(template_source)
