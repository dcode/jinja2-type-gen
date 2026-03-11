from jinja2 import Environment

from jinja2_type_gen import SignatureExtension, TemplateTypeAnalyzer


def main():
    template_str = """
{# We define our strictly typed signature here #}
{% signature
    user_name: str,
    item_count: int,
    is_premium: bool = False
%}
<html>
    <body>
        <h1>Welcome, {{ user_name }}!</h1>
        <p>You have {{ item_count }} items in your cart.</p>
        {% if is_premium %}
            <p>Thanks for being a premium member. Enjoy free shipping!</p>
        {% endif %}
    </body>
</html>
"""

    print("--- 1. Static Analysis Phase ---")
    analyzer = TemplateTypeAnalyzer()

    print("Extracting Type Information from AST...")
    extracted_types = analyzer.analyze_source(template_str)

    print("\nGenerated .pyi TypedDict representation:")
    print("class TemplateArgs(TypedDict):")
    for var_name, type_info in extracted_types.items():
        if type_info["required"]:
            print(f"    {var_name}: {type_info['type']}")
        else:
            print(f"    {var_name}: NotRequired[{type_info['type']}]")

    print("\n--- 2. Runtime Execution Phase ---")
    # At runtime, our extension produces zero bytecode for the signature node.
    env = Environment(extensions=[SignatureExtension])
    template = env.from_string(template_str)

    # Missing optional arg falls back perfectly (handled by python/jinja as usual if passed,
    # but the strict type checker would complain if we wrote the typed wrapper)
    rendered = template.render(user_name="Architect", item_count=42, is_premium=True)

    print("\nRendered Output:")
    print(rendered.strip())


if __name__ == "__main__":
    main()
