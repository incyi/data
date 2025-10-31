import random
from pathlib import Path
import pandas as pd
from src.url_checker.checker import check_files, check_file
from src.url_checker.reporter import ConsoleReporter, MarkdownReporter

FILES = [
    Path("airports-nl.csv"),
    Path("airports-de.csv"),
    Path("list.csv"),
]

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)  # make sure folder exists
SUMMARY_FILE = REPORTS_DIR / "summary.md"

def main(files=None, reporters=None):
    files = files or FILES
    reporters = reporters or [ConsoleReporter(), MarkdownReporter("summary.md")]
    errors = check_files(files, reporters=reporters)
    if errors:
        for e in errors:
            print(e)
        if __name__ == "__main__":
            exit(1)
    return errors


def main():
    console = ConsoleReporter()
    summary = MarkdownReporter(SUMMARY_FILE)

    # Shuffle rows for each CSV before checking
    shuffled_files = []
    for file_path in FILES:
        df = pd.read_csv(file_path)
        df = df.sample(frac=1).reset_index(drop=True)  # shuffle rows
        tmp_file = Path(file_path.parent) / f"shuffled_{file_path.name}"
        df.to_csv(tmp_file, index=False)
        shuffled_files.append(tmp_file)

    errors = check_files(shuffled_files, reporters=[console, summary])

    if errors:
        print(f"\n{len(errors)} errors detected.")
        exit(1)
    else:
        print("\nAll URLs passed successfully.")
        exit(0)


if __name__ == "__main__":
    main()
