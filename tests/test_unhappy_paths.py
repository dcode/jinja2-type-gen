import pytest
from jinja2.exceptions import TemplateSyntaxError

from jinja2_type_gen import TemplateTypeAnalyzer


def test_malformed_signature():
    analyzer = TemplateTypeAnalyzer()

    # Missing types or invalid python syntax inside signature
    template_source = "{% signature user: str, = ) %}"

    with pytest.raises(TemplateSyntaxError):
        analyzer.analyze_source(template_source)


def test_deep_nesting_limits():
    analyzer = TemplateTypeAnalyzer()

    # Create a deeply nested includes template source
    # Jinja's native parser might throw if too deep, but we must ensure our analyzer doesn't throw a RecursionError.
    source = ""
    for _ in range(100):
        source += "{% if True %}"
    source += "{% signature deep_var: int %}"
    for _ in range(100):
        source += "{% endif %}"

    # Should parse without RecursionError
    types = analyzer.analyze_source(source)
    assert "deep_var" in types
    assert types["deep_var"]["type"] == "int"


def test_jinja2_template_injection():
    # An attempt to inject a potentially dangerous template tag inside the signature
    analyzer = TemplateTypeAnalyzer()

    # The extension consumes everything until block_end.
    # If the user tries to inject python syntax that is valid but maybe malicious, ast.parse will catch syntax or we should ensure we don't execute it.
    # The analyzer uses ImmutableSandboxedEnvironment, so we are protected.

    # Syntax valid python, but attempting to do something unexpected
    template_source = "{% signature __import__('os').system('ls'): str %}"

    # This will fail ast.parse as an invalid function argument list
    with pytest.raises(TemplateSyntaxError, match="Invalid python signature syntax"):
        analyzer.analyze_source(template_source)


def test_ast_evaluation_safety():
    # If a signature contains defaults that look like function calls,
    # they are stringified, not executed.
    analyzer = TemplateTypeAnalyzer()
    template_source = "{% signature a: int = exit(1) %}"

    # It parses successfully because ast.parse allows default arguments as function calls.
    # However, it is never executed. It's just extracted.
    types = analyzer.analyze_source(template_source)
    assert types["a"]["required"] is False
    assert types["a"]["type"] == "int"
