from src.url_checker.checker import check_files
from src.url_checker.reporter import ConsoleReporter, MarkdownReporter
import tempfile
import pandas as pd
from unittest.mock import patch
import requests

def test_empty_file_list():
    console = ConsoleReporter()
    result = check_files([], reporters=[console])
    assert result == []

def test_file_not_found():
    console = ConsoleReporter()
    errors = check_files(["nonexistent.csv"], reporters=[console])
    assert len(errors) == 1
    assert "not found" in errors[0]

def test_missing_url_column(tmp_path):
    file = tmp_path / "test.csv"
    pd.DataFrame({"name": ["a", "b"]}).to_csv(file, index=False)
    console = ConsoleReporter()
    errors = check_files([file], reporters=[console])
    assert any("No 'url' column found" in e for e in errors)

def test_valid_url(tmp_path):
    """Test that a valid URL passes without errors."""
    df = pd.DataFrame({"url": ["https://example.com"]})
    file = tmp_path / "urls.csv"
    df.to_csv(file, index=False)
    console = ConsoleReporter()
    with patch("requests.head") as mock_head:
        mock_head.return_value.status_code = 200
        errors = check_files([file], reporters=[console])
    assert errors == []

def test_invalid_url(tmp_path):
    df = pd.DataFrame({"url": ["https://example.com/bad"]})
    file = tmp_path / "urls.csv"
    df.to_csv(file, index=False)
    console = ConsoleReporter()
    with patch("requests.head") as mock_head, patch("requests.get") as mock_get:
        mock_head.return_value.status_code = 404
        mock_get.return_value.status_code = 404
        errors = check_files([file], reporters=[console])
    assert any("returned 404" in e for e in errors)

def test_url_exception(tmp_path):
    df = pd.DataFrame({"url": ["https://bad.url"]})
    file = tmp_path / "urls.csv"
    df.to_csv(file, index=False)
    console = ConsoleReporter()
    with patch("requests.head", side_effect=requests.RequestException("fail")):
        errors = check_files([file], reporters=[console])
    assert any("failed" in e for e in errors)

def test_markdown_reporter(tmp_path):
    file = tmp_path / "summary.md"
    reporter = MarkdownReporter(file)
    reporter.report("test.csv", "https://example.com", "OK", ok=True)
    reporter.finish()
    content = file.read_text()
    assert "| test.csv | https://example.com | ✅ OK |" in content
