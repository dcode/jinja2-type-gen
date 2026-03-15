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


def test_cli_generate_creates_renderers(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "index.j2").write_text("{% signature title: str %}{{ title }}")

    output_file = tmp_path / "templates.py"

    result = main(
        ["generate", str(template_dir), "--output", str(output_file), "--create-renderers"]
    )
    assert result == 1
    content = output_file.read_text()
    assert "def render_index_j2" in content
    assert "Unpack[IndexJ2Context]" in content
    assert "configure_environment" in content


def test_cli_invalid_directory(tmp_path: Path):
    result = main(["generate", "non_existent_dir", "--output", "out.py"])
    assert result == 1


def test_cli_handles_invalid_syntax(tmp_path: Path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "bad.j2").write_text("{% signature user: str, = ) %}")

    output_file = tmp_path / "templates.pyi"
    result = main(["generate", str(template_dir), "--output", str(output_file)])
    assert result == 1  # generate_stubs returns 1 if has_errors is True
    assert not output_file.exists()
