from src.url_checker.checker import check_files
from src.url_checker.reporter import ConsoleReporter

def test_empty_file_list():
    # Should return empty errors list if no files
    console = ConsoleReporter()
    result = check_files([], reporters=[console])
    assert result == []
