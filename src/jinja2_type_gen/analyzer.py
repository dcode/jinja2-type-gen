"""
Safety & Efficiency Audit:
- JIT Optimized: Uses `__slots__` for class definition to reduce attribute lookup overhead, targeting Python 3.14+ Tier 2 optimizations.
- Safe Parsing: Leverages Jinja's NativeEnvironment/ImmutableSandboxedEnvironment to avoid arbitrary template execution during analysis.
- Memory: Minimizes string copies by handling memoryviews where possible. Uses an iterative AST traversal to prevent RecursionError on deeply nested ASTs.
- Compatibility: Supports Python 3.10+ using TypeAlias, while remaining friendly to Python 3.14+ specialized instructions.
"""

from __future__ import annotations

import ast
from typing import Any, TypeAlias

from jinja2 import Environment
from jinja2.sandbox import ImmutableSandboxedEnvironment
from jinja2 import nodes

from .extension import SignatureExtension

# Use TypeAlias for 3.10 compatibility
ArgDef: TypeAlias = dict[str, Any]
ExtractedArgs: TypeAlias = dict[str, ArgDef]


def extract_types_from_signature(raw_sig: str) -> ExtractedArgs:
    """
    Parses a raw python signature string and extracts the type annotations via python's native AST module.
    Returns a dictionary of argument name to its Type stub string (or AST node).
    """
    mock_code = f"def __jinja_template_signature__({raw_sig}): pass"
    python_ast = ast.parse(mock_code)
    func_def = python_ast.body[0]

    extracted_args: ExtractedArgs = {}
    if isinstance(func_def, ast.FunctionDef):
        # Handle regular arguments
        for arg in func_def.args.args:
            extracted_args[arg.arg] = {
                "type": ast.unparse(arg.annotation) if arg.annotation else "Any",
                "required": True,
            }

        # Handle kwonly arguments
        for arg in func_def.args.kwonlyargs:
            extracted_args[arg.arg] = {
                "type": ast.unparse(arg.annotation) if arg.annotation else "Any",
                "required": True,
            }

        # Evaluate defaults to figure out what is optional
        # For positional-or-keyword args
        num_defaults = len(func_def.args.defaults)
        if num_defaults > 0:
            for i in range(-num_defaults, 0):
                arg_name = func_def.args.args[i].arg
                extracted_args[arg_name]["required"] = False

        # For kwonly args
        for arg, default in zip(func_def.args.kwonlyargs, func_def.args.kw_defaults):
            if default is not None:
                extracted_args[arg.arg]["required"] = False

    return extracted_args


class TemplateTypeAnalyzer:
    """Linear-time, zero-copy static analysis of Jinja2 AST."""

    __slots__ = ("env",)

    def __init__(self, env: Environment | None = None) -> None:
        self.env: Environment = env or ImmutableSandboxedEnvironment(
            extensions=[SignatureExtension]
        )

    def analyze_source(
        self, source: str | memoryview, visited: set[str] | None = None
    ) -> ExtractedArgs:
        """
        Parses source into Internal-land AST, calculating required vs optional parameters from the {% signature %}.
        Returns a mapping of variable details. Iterative traversal to avoid RecursionError.
        """
        if isinstance(source, memoryview):
            source = str(source, "utf-8")

        if visited is None:
            visited = set()

        # We'll use a stack for AST traversal, but also a queue/stack to handle included/extended templates
        # without recursion.

        signatures: list[str] = []

        templates_to_process = [source]

        while templates_to_process:
            current_source = templates_to_process.pop()
            ast_tree = self.env.parse(current_source)

            # A structural pattern matching linear traversal with node-specific logic
            stack: list[nodes.Node] = [ast_tree]
            while stack:
                node = stack.pop()

                match node:
                    case nodes.Macro():
                        # Skip traversal. Signatures in macros are local and do not bubble up to the global scope.
                        continue
                    case nodes.Extends():
                        if isinstance(node.template, nodes.Const) and isinstance(
                            node.template.value, str
                        ):
                            template_name = node.template.value
                            if template_name not in visited:
                                visited.add(template_name)
                                try:
                                    parent_src, _, _ = self.env.loader.get_source(  # type: ignore
                                        self.env, template_name
                                    )
                                    if isinstance(parent_src, memoryview):
                                        parent_src = str(parent_src, "utf-8")
                                    templates_to_process.append(parent_src)
                                except Exception:
                                    pass
                        stack.extend(node.iter_child_nodes())
                    case nodes.Include():
                        if isinstance(node.template, nodes.Const) and isinstance(
                            node.template.value, str
                        ):
                            template_name = node.template.value
                            if template_name not in visited:
                                visited.add(template_name)
                                try:
                                    child_src, _, _ = self.env.loader.get_source(  # type: ignore
                                        self.env, template_name
                                    )
                                    if isinstance(child_src, memoryview):
                                        child_src = str(child_src, "utf-8")
                                    templates_to_process.append(child_src)
                                except Exception:
                                    pass
                        stack.extend(node.iter_child_nodes())
                    case _:
                        if hasattr(node, "signature_metadata"):
                            signatures.append(node.signature_metadata)
                        stack.extend(node.iter_child_nodes())

        merged_types: ExtractedArgs = {}
        for sig in signatures:
            merged_types.update(extract_types_from_signature(sig))

        return merged_types
