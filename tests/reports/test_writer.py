from markdown_checker.reports.writer import write_report


def test_write_report_to_file(tmp_path):
    """write_report writes to the given path."""
    output_path = tmp_path / "out.md"
    write_report("# Content", output_path=output_path)
    assert output_path.read_text(encoding="utf-8") == "# Content"


def test_write_report_overwrites_existing_file(tmp_path):
    """write_report overwrites any existing content at the path."""
    output_path = tmp_path / "out.md"
    output_path.write_text("old content", encoding="utf-8")
    write_report("new content", output_path=output_path)
    assert output_path.read_text(encoding="utf-8") == "new content"


def test_write_report_to_stdout(capsys):
    """write_report writes to stdout when output_path is None."""
    write_report("hello", output_path=None)
    assert capsys.readouterr().out == "hello"
