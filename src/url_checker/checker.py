# src/url_checker/checker.py

# ----------------------
# Standard library
# ----------------------
import os
import ssl
import socket
from datetime import datetime, timezone
from typing import List
from urllib.parse import urlparse

# ----------------------
# Third-party
# ----------------------
import pandas as pd
import requests
from requests.exceptions import RequestException


def check_files(files: List[str], reporters=None) -> List[str]:
    """Check URLs in multiple CSV files."""
    errors: List[str] = []
    reporters = reporters or []

    for file_path in files:
        errors.extend(check_file(file_path, reporters))

    # Notify reporters that processing is done
    for reporter in reporters:
        reporter.finish()

    return errors


def check_file(file_path: str, reporters=None) -> List[str]:
    """Check a single CSV file for valid URLs."""
    errors: List[str] = []
    reporters = reporters or []

    if not os.path.exists(file_path):
        msg = f"File {file_path} not found"
        report_error(file_path, "-", msg, errors, reporters)
        return errors

    try:
        df = pd.read_csv(file_path)
    except pd.errors.ParserError as e:
        msg = f"Could not parse {file_path}: {e}"
        report_error(file_path, "-", msg, errors, reporters)
        return errors

    if "url" not in df.columns:
        msg = f"No 'url' column found in {file_path}"
        report_error(file_path, "-", msg, errors, reporters)
        return errors

    for url in df["url"].dropna().astype(str):
        errors.extend(check_url(url, file_path, reporters))

    return errors


def check_url(url: str, file_path: str, reporters=None) -> List[str]:
    """Check a single URL including HTTP status and SSL/TLS certificate validity."""
    errors: List[str] = []
    reporters = reporters or []

    # ----------------------
    # 1️⃣ Check HTTP(S) response
    # ----------------------
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code >= 400:
            response = requests.get(url, timeout=10, allow_redirects=True)
        if response.status_code >= 400:
            msg = f"{url} returned {response.status_code}"
            report_error(file_path, url, msg, errors, reporters)
        else:
            report_error(file_path, url, "OK", errors, reporters, ok=True)
    except RequestException as e:
        msg = f"{url} failed: {e}"
        report_error(file_path, url, msg, errors, reporters)

    # ----------------------
    # 2️⃣ Check SSL/TLS certificate if HTTPS
    # ----------------------
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return errors

    hostname = parsed.hostname
    if not hostname:
        msg = f"{url} has invalid hostname"
        report_error(file_path, url, msg, errors, reporters)
        return errors

    try:
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                not_after_str = cert.get("notAfter")
                if not_after_str:
                    not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                    not_after = not_after.replace(tzinfo=timezone.utc)
                    if not_after < datetime.now(timezone.utc):
                        msg = f"{url} SSL certificate expired on {not_after}"
                        report_error(file_path, url, msg, errors, reporters)
    except ssl.SSLError as e:
        msg = f"{url} SSL error: {e}"
        report_error(file_path, url, msg, errors, reporters)
    except socket.timeout:
        msg = f"{url} SSL check timed out"
        report_error(file_path, url, msg, errors, reporters)
    except socket.gaierror as e:
        msg = f"{url} SSL check failed (hostname error): {e}"
        report_error(file_path, url, msg, errors, reporters)

    return errors


def report_error(
    file_path: str,
    url: str,
    msg: str,
    errors: List[str],
    reporters=None,
    *,
    ok: bool = False
):
    """Append error and notify reporters."""
    reporters = reporters or []
    if not ok:
        errors.append(msg)
    for reporter in reporters:
        reporter.report(file_path, url, msg, ok=ok)
