import os
import pandas as pd
import requests

def check_files(files, reporters=None):
    errors = []
    reporters = reporters or []

    for f in files:
        if not os.path.exists(f):
            msg = f"File {f} not found"
            errors.append(msg)
            for r in reporters:
                r.report(f, "-", msg, ok=False)
            continue

        try:
            df = pd.read_csv(f)
        except Exception as e:
            msg = f"Could not read {f}: {e}"
            errors.append(msg)
            for r in reporters:
                r.report(f, "-", msg, ok=False)
            continue

        if "url" not in df.columns:
            msg = f"No 'url' column found in {f}"
            errors.append(msg)
            for r in reporters:
                r.report(f, "-", msg, ok=False)
            continue

        for url in df["url"].dropna().astype(str):
            try:
                r = requests.head(url, timeout=10, allow_redirects=True)
                if r.status_code >= 400:
                    r = requests.get(url, timeout=10, allow_redirects=True)
                if r.status_code >= 400:
                    msg = f"{url} returned {r.status_code}"
                    errors.append(msg)
                    for rep in reporters:
                        rep.report(f, url, msg, ok=False)
                else:
                    for rep in reporters:
                        rep.report(f, url, "OK", ok=True)
            except Exception as e:
                msg = f"{url} failed: {e}"
                errors.append(msg)
                for rep in reporters:
                    rep.report(f, url, msg, ok=False)

    for r in reporters:
        r.finish()

    return errors
