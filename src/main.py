from url_checker.checker import check_files
from url_checker.reporter import ConsoleReporter, MarkdownReporter
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../")
FILES = [os.path.join(DATA_PATH, "airports.csv"),
         os.path.join(DATA_PATH, "list.csv")]

def main():
    console = ConsoleReporter()
    summary = MarkdownReporter(os.path.join(os.path.dirname(__file__), "summary.md"))

    errors = check_files(FILES, reporters=[console, summary])

    if errors:
        print("\n❌ Some URLs are invalid.")
        exit(1)
    else:
        print("\n✅ All URLs are valid.")

if __name__ == "__main__":
    main()
