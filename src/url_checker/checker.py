import os
import pandas as pd
import requests
from requests.exceptions import RequestException


def check_files(files, reporters=None):
    """Check URLs in multiple CSV files."""
    errors = []
    reporters = reporters or []

    for file_path in files:
        errors.extend(check_file(file_path, reporters))

    # Notify reporters that processing is done
    for reporter in reporters:
        reporter.finish()

    return errors


def check_file(file_path, reporters):
    """Check a single CSV file for valid URLs."""
    errors = []

    if not os.path.exists(file_path):
        msg = f"File {file_path} not found"
        errors.append(msg)
        for reporter in reporters:
            reporter.report(file_path, "-", msg, ok=False)
        return errors

    try:
        df = pd.read_csv(file_path)
    except pd.errors.ParserError as e:
        msg = f"Could not parse {file_path}: {e}"
        errors.append(msg)
        for reporter in reporters:
            reporter.report(file_path, "-", msg, ok=False)
        return errors

    if "url" not in df.columns:
        msg = f"No 'url' column found in {file_path}"
        errors.append(msg)
        for reporter in reporters:
            reporter.report(file_path, "-", msg, ok=False)
        return errors

    for url in df["url"].dropna().astype(str):
        errors.extend(check_url(url, file_path, reporters))

    return errors


def check_url(url, file_path, reporters):
    """Check a single URL."""
    errors = []

    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code >= 400:
            response = requests.get(url, timeout=10, allow_redirects=True)
        if response.status_code >= 400:
            msg = f"{url} returned {response.status_code}"
            errors.append(msg)
            for reporter in reporters:
                reporter.report(file_path, url, msg, ok=False)
        else:
            for reporter in reporters:
                reporter.report(file_path, url, "OK", ok=True)

    except RequestException as e:
        msg = f"{url} failed: {e}"
        errors.append(msg)
        for reporter in reporters:
            reporter.report(file_path, url, msg, ok=False)

    return errors
