"""
Step 1: download the paper lists.

Paper Copilot (github.com/papercopilot/paperlists) publishes one JSON file per
conference per year, with every submission's title, abstract and decision.
We download a fixed snapshot (a pinned commit), so everyone gets the same data.

Usage:  python download.py
Result: data/iclr2019.json, data/icml2019.json, data/nips2019.json, ... (~600 MB)
"""
import http.client
import time
import urllib.error
import urllib.request
from pathlib import Path

SNAPSHOT = "9fcfd1234879a8e5630b5116dde411ec143dd763"  # paperlists commit, 30 June 2026
CONFERENCES = ["iclr", "icml", "nips"]
YEARS = range(2019, 2027)
DATA = Path(__file__).parent / "data"

RAW_URL = "https://raw.githubusercontent.com/papercopilot/paperlists/{snapshot}/{conf}/{conf}{year}.json"
# Some large files are stored with Git LFS. For those the raw URL only returns a short
# "pointer" text, and the real file lives at this second address.
LFS_URL = "https://media.githubusercontent.com/media/papercopilot/paperlists/{snapshot}/{conf}/{conf}{year}.json"


def fetch(url):
    """Download a URL, retrying a few times if the connection drops."""
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=300) as response:
                expected = response.headers.get("Content-Length")
                body = response.read()
            if expected is None or len(body) == int(expected):
                return body
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None  # this conference-year does not exist in the snapshot
        except (OSError, http.client.HTTPException):
            pass  # dropped connection: try again
        print("    retrying...")
        time.sleep(3)
    raise RuntimeError(f"Could not download {url}")


def main():
    DATA.mkdir(exist_ok=True)
    for conf in CONFERENCES:
        for year in YEARS:
            path = DATA / f"{conf}{year}.json"
            if path.exists():
                continue
            print(f"downloading {path.name}")
            body = fetch(RAW_URL.format(snapshot=SNAPSHOT, conf=conf, year=year))
            if body is None:
                print("    not in this snapshot, skipped")
                continue
            if body.startswith(b"version https://git-lfs"):
                body = fetch(LFS_URL.format(snapshot=SNAPSHOT, conf=conf, year=year))
            path.write_bytes(body)


if __name__ == "__main__":
    main()
