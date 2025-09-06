class ConsoleReporter:
    """Report results to the console."""

    def report(self, file_path, url, message, ok=True):
        if ok:
            print(f"✅ {url} in {file_path}: {message}")
        else:
            print(f"❌ {url} in {file_path}: {message}")

    def finish(self):
        # Empty method because ConsoleReporter prints immediately to console
        pass


class MarkdownReporter:
    """Write a Markdown summary table for GitHub Actions."""

    def __init__(self, path):
        self.path = path
        self.lines = ["| File | URL | Status |", "|------|-----|--------|"]

    def report(self, file_path, url, message, ok=True):
        status = f"✅ {message}" if ok else f"❌ {message}"
        self.lines.append(f"| {file_path} | {url} | {status} |")

    def finish(self):
        with open(self.path, "w", encoding="utf-8") as file_handler:
            file_handler.write("\n".join(self.lines))
