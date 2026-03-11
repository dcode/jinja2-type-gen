from jinja2_type_gen import TemplateTypeAnalyzer


def test_analyzer_extracts_signature():
    analyzer = TemplateTypeAnalyzer()

    template_source = """
{% signature
    name: str,
    age: int,
    is_admin: bool = False
%}
Hello {{ name }}, you are {{ age }} years old.
"""

    types = analyzer.analyze_source(template_source)

    assert "name" in types
    assert types["name"]["required"] is True
    assert types["name"]["type"] == "str"

    assert "age" in types
    assert types["age"]["required"] is True
    assert types["age"]["type"] == "int"

    assert "is_admin" in types
    assert types["is_admin"]["required"] is False
    assert types["is_admin"]["type"] == "bool"


def test_analyzer_extracts_complex_types():
    analyzer = TemplateTypeAnalyzer()

    template_source = """
{% signature
    users: list[dict[str, Any]],
    callback: Callable[[int], str] | None = None
%}
"""

    types = analyzer.analyze_source(template_source)

    assert "users" in types
    assert types["users"]["type"] == "list[dict[str, Any]]"
    assert types["users"]["required"] is True

    assert "callback" in types
    assert types["callback"]["type"] == "Callable[[int], str] | None"
    assert types["callback"]["required"] is False


def test_analyzer_ignores_macro_scope():
    analyzer = TemplateTypeAnalyzer()

    template_source = """
{% macro my_macro() %}
    {% signature
        macro_arg: int
    %}
    {{ macro_arg }}
{% endmacro %}

{% signature
    global_arg: str
%}
{{ my_macro() }}
{{ global_arg }}
"""

    types = analyzer.analyze_source(template_source)

    assert "global_arg" in types
    assert types["global_arg"]["type"] == "str"
    assert (
        "macro_arg" not in types
    ), "Macro signatures should not leak into global template scope."


def test_analyzer_resolves_extends():
    from jinja2 import Environment, DictLoader
    from jinja2_type_gen import SignatureExtension

    env = Environment(
        loader=DictLoader(
            {
                "base.j2": "{% signature base_title: str %}<title>{{ base_title }}</title>{% block content %}{% endblock %}",
                "child.j2": "{% extends 'base.j2' %}{% block content %}{% signature child_param: int %}{{ child_param }}{% endblock %}",
            }
        ),
        extensions=[SignatureExtension],
    )
    analyzer = TemplateTypeAnalyzer(env=env)

    types = analyzer.analyze_source(env.loader.get_source(env, "child.j2")[0])

    assert "child_param" in types
    assert types["child_param"]["type"] == "int"
    assert (
        "base_title" in types
    ), "Signature from extended template should be bubbled up."
    assert types["base_title"]["type"] == "str"


def test_analyzer_resolves_include():
    from jinja2 import Environment, DictLoader
    from jinja2_type_gen import SignatureExtension

    env = Environment(
        loader=DictLoader(
            {
                "partial.j2": "{% signature partial_data: dict[str, Any] %}{{ partial_data }}",
                "main.j2": "{% signature main_data: str %}<h1>{{ main_data }}</h1>{% include 'partial.j2' %}",
            }
        ),
        extensions=[SignatureExtension],
    )
    analyzer = TemplateTypeAnalyzer(env=env)

    types = analyzer.analyze_source(env.loader.get_source(env, "main.j2")[0])

    assert "main_data" in types
    assert types["main_data"]["type"] == "str"
    assert (
        "partial_data" in types
    ), "Signature from included template should be bubbled up."
    assert types["partial_data"]["type"] == "dict[str, Any]"
