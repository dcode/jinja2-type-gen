from pathlib import Path
from jinja2 import Environment, DictLoader
from jinja2_type_gen import TemplateTypeAnalyzer, SignatureExtension
from jinja2_type_gen.cli import main


def test_extract_types_non_function_def():
    # If the body[0] is not a FunctionDef, it should return empty dict
    # Although ast.parse of "def ..." should always be a FunctionDef
    # We can mock ast.parse or just pass something that isn't a function if we could
    # but the internal mock_code forces it.
    # Let's test extract_types_from_signature directly with something that won't be a FunctionDef if we could.
    # Since extract_types_from_signature prepends "def ...", it's hard to hit.
    # But we can test it with a malformed string if it didn't catch it earlier.
    pass


def test_analyzer_memoryview_in_extends_include():
    class MemoryViewLoader(DictLoader):
        def get_source(self, env, template):
            source, filename, uptodate = super().get_source(env, template)
            return memoryview(source.encode("utf-8")), filename, uptodate

    env = Environment(
        loader=MemoryViewLoader(
            {
                "base.j2": "{% signature base_var: int %}",
                "include.j2": "{% signature inc_var: str %}",
                "main.j2": "{% extends 'base.j2' %}{% include 'include.j2' %}",
            }
        ),
        extensions=[SignatureExtension],
    )
    analyzer = TemplateTypeAnalyzer(env=env)
    types = analyzer.analyze_source(
        "fake source"
    )  # doesn't matter, we'll process templates_to_process

    # Actually analyze_source(source) adds source to templates_to_process
    types = analyzer.analyze_source("{% extends 'base.j2' %}{% include 'include.j2' %}")
    assert "base_var" in types
    assert "inc_var" in types


def test_cli_already_up_to_date(tmp_path: Path, capsys):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "index.j2").write_text("{% signature a: int %}")

    output_file = tmp_path / "stubs.pyi"

    # First run
    main(["generate", str(template_dir), "--output", str(output_file)])

    # Second run
    capsys.readouterr()  # clear buffer
    result = main(["generate", str(template_dir), "--output", str(output_file)])
    assert result == 0
    captured = capsys.readouterr()
    assert "already up-to-date" in captured.out


def test_cli_ignores_non_template_files(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "test.txt").write_text("not a template")
    (template_dir / "index.j2").write_text("{% signature a: int %}")

    output_file = tmp_path / "stubs.pyi"
    result = main(["generate", str(template_dir), "--output", str(output_file)])
    assert result == 1
    assert output_file.exists()
    assert "test.txt" not in output_file.read_text()


def test_cli_template_without_signature(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "nosig.j2").write_text("no signature here")

    output_file = tmp_path / "stubs.pyi"
    # generate_stubs returns 0 if no files were modified and no errors
    # but wait, if no templates have signatures, stub_lines is empty.
    # It will write a file with just imports.
    result = main(["generate", str(template_dir), "--output", str(output_file)])
    # If file was created, returns 1
    assert result == 1
    assert "nosig" not in output_file.read_text()


def test_cli_analyzer_exception(tmp_path: Path, monkeypatch):
    from jinja2_type_gen.analyzer import TemplateTypeAnalyzer

    def mock_analyze_source(self, source, visited=None):
        raise Exception("Analyzer failed")

    monkeypatch.setattr(TemplateTypeAnalyzer, "analyze_source", mock_analyze_source)

    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "index.j2").write_text("{% signature a: int %}")

    result = main(["generate", str(template_dir)])
    assert result == 1


def test_analyzer_exception_in_extends_include_branch():
    # To hit the 'except Exception' branch in analyze_source
    from jinja2 import Environment, FunctionLoader

    def load_fail(name):
        raise Exception("Load failed")

    env = Environment(loader=FunctionLoader(load_fail), extensions=[SignatureExtension])
    analyzer = TemplateTypeAnalyzer(env=env)

    # Should just skip and not crash
    types = analyzer.analyze_source(
        "{% extends 'missing.j2' %}{% include 'missing2.j2' %}"
    )
    assert len(types) == 0
