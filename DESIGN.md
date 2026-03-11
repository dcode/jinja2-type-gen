# `jinja2-type-gen` Design Document

## 1. Overview

The `jinja2-type-gen` project provides strict, compile-time/static type safety to Jinja2 templates without compromising runtime performance. It bridges the gap between static Python analysis (Mypy/Pyright) and dynamic template metaprogramming.

## 2. Core Architecture

The system is divided into two phases: **Static Analysis** and **Runtime Execution**.

### 2.1 Static Analysis Phase

During CI/CD, pre-commit, or language server execution, templates are parsed to construct `.pyi` stub files (or memory structures) that denote the precise context variables required to render a template.

### 2.2 Runtime Execution Phase

During live execution, the `SignatureExtension` processes the type annotations but emits **zero bytecode**, ensuring that the execution of `Template.render()` incurs zero latency overhead compared to a standard Jinja string.

## 3. Technical Implementation

- **The Jinja Extension:** `SignatureExtension` registers the `{% signature ... %}` tag.
- **AST Parsing:** When triggered, it intercepts the lexer stream directly to extract the signature string. It verifies grammatical correctness using Python's native `ast.parse()` to prevent unexpected or malicious payloads.
- **Node Injection:** Instead of violating Jinja's strict node typing rules with a custom node, the extension returns an empty `nodes.Output` node and decorates it with a `signature_metadata` attribute containing the raw signature string.
- **Code Generation (Analyzer):** The `TemplateTypeAnalyzer` linearly traverses the returned AST for the `signature_metadata` attribute and processes it through `ast.parse()` to determine the explicit TypeHints and requirement status (based on whether arg defaults are present). This allows developers to generate `TypedDict` stubs.

## 4. Work Effort Roadmap & Milestones

### Milestone 1: Proof of Concept (Completed)

- [x] Create project scaffolding (`uv`, `hatchling`).
- [x] Implement runtime zero-overhead `SignatureExtension`.
- [x] Implement linear-time `TemplateTypeAnalyzer` extracting simple python signatures.
- [x] Demonstrate functionality via `examples/{simple,typical}` workspaces and recursive pytest test discovery.

### Milestone 2: Complex Types & Scope Management (2-3 Weeks)

- [x] **Advanced Scoping:** Ensure that variables declared globally in `{% signature %}` do not pollute nested `{% macro %}` scopes or local `{% set %}` scopes.
- [x] **Template Inheritance:** Implement logic to merge signatures when templates use `{% extends "base.j2" %}`. A required variable in the base template should bubble up to the child template's signature.
- [x] **Cross-Template Validation:** Ensure consistency when data is passed via `{% include "partial.j2" %}`.

### Milestone 3: CI/CD & Developer Tooling (1-2 Weeks)

- [x] **CLI Tool Generation:** Build a CLI entrypoint (e.g., `jinja2-type-gen generate src/templates/`) that automatically scans a directory of `.j2` files and drops a `templates.pyi` stub file.
- [x] **Pre-commit Hook:** Provide a native pre-commit hook that validates templates against python function calls or ensures stubs are up-to-date.

### Milestone 4: Open Source Release (1 Week)

- [x] Comprehensive Markdown documentation and docstrings.
- [ ] Publish to PyPI via `python-semantic-release`.
- [ ] Establish CI matrices testing against Python 3.10 through 3.14.
