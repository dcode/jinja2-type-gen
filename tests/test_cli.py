from pathlib import Path

from jinja2_type_gen.cli import main


def test_cli_generate_creates_stub_file(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    # Create a valid j2 template with a signature
    (template_dir / "index.j2").write_text(
        "{% signature title: str, count: int = 0 %}{{ title }}"
    )

    output_file = tmp_path / "templates.pyi"

    # Run CLI generate command
    result = main(["generate", str(template_dir), "--output", str(output_file)])

    assert (
        result == 1
    ), "CLI should exit with code 1 when the file is freshly generated or modified"
    assert output_file.exists(), "The output stub file must be generated"

    # Run it again to ensure it exits with 0
    result2 = main(["generate", str(template_dir), "--output", str(output_file)])
    assert result2 == 0, "CLI should exit with code 0 when no changes were needed"

    stub_content = output_file.read_text()

    # TypedDict verification
    assert "class IndexJ2Context(TypedDict):" in stub_content
    assert "title: str" in stub_content
    assert "count: NotRequired[int]" in stub_content


def test_cli_handles_invalid_syntax(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    # Create an invalid j2 template
    (template_dir / "bad.j2").write_text("{% signature 1bad syntax %}")

    output_file = tmp_path / "templates.pyi"

    # Run CLI generate command
    result = main(["generate", str(template_dir), "--output", str(output_file)])

    assert result != 0, "CLI should exit with a non-zero code on syntax errors"
    assert not output_file.exists(), "Should not overwrite stub if generation fails"
