import os

class ConsoleReporter:
    def report(self, file, url, message, ok=True):
        if ok:
            print(f"✅ {url} in {file}: {message}")
        else:
            print(f"❌ {url} in {file}: {message}")

    def finish(self):
        pass


class MarkdownReporter:
    def __init__(self, path):
        self.path = path
        self.lines = ["| File | URL | Status |", "|------|-----|--------|"]

    def report(self, file, url, message, ok=True):
        status = f"✅ {message}" if ok else f"❌ {message}"
        self.lines.append(f"| {file} | {url} | {status} |")

    def finish(self):
        with open(self.path, "w") as f:
            f.write("\n".join(self.lines))
