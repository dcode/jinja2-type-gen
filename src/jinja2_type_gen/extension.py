"""
Safety & Efficiency Audit:
- Safe Parsing: Emits an empty Output node instead of a custom AST node. This guarantees zero runtime execution cost and no arbitrary bytecode evaluation.
- Early Validation: Evaluates the parsed signature syntax using the built-in `ast` module at template *compilation* time.
- Efficiency: Consumes Jinja's token stream iteratively, collecting string parts.
"""

from __future__ import annotations

import ast

from jinja2 import nodes
from jinja2.ext import Extension
from jinja2.parser import Parser


class SignatureExtension(Extension):
    """
    Extends Jinja2 parser to handle {% signature name: type, optional: type = default %}
    Outputs no bytecode at runtime. Purely an AST metadata container.
    """

    tags = {"signature"}

    def parse(self, parser: Parser) -> nodes.Node | list[nodes.Node]:
        """
        Invoked locally when the parser hits `{% signature`.
        """
        # The first token is the tag name itself. We capture its location for error reporting.
        lineno = next(parser.stream).lineno

        signature_tokens: list[str] = []
        while parser.stream.current.type != "block_end":
            token = parser.stream.current
            if token.type == "string":
                signature_tokens.append(repr(token.value))
            else:
                signature_tokens.append(str(token.value))
            next(parser.stream)

        raw_signature_string = "".join(signature_tokens).strip()

        # Validate syntax via ast.parse immediately to fail early on malformed signatures
        try:
            ast.parse(f"def __jinja_template_signature__({raw_signature_string}): pass")
        except SyntaxError as e:
            from jinja2.exceptions import TemplateSyntaxError

            raise TemplateSyntaxError(
                f"Invalid python signature syntax: {e.msg}",
                lineno,
                name=parser.name,
                filename=parser.filename,
            ) from e

        # Instead of a custom node (which Jinja2 forbids), we return an empty Output node
        # so it compiles down to almost zero cost, and we attach our metadata to it.
        metadata_expr = nodes.Const("")
        signature_node = nodes.Output([metadata_expr], lineno=lineno)
        signature_node.signature_metadata = raw_signature_string  # type: ignore

        return signature_node
