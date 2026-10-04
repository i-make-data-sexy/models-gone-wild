#!/usr/bin/env python3
"""Keeps the scout's record of every story it has already looked at.

The daily scout (see scout/SCOUT.md) searches for new escapes and
emails Annie a proposal when it finds one. Without a memory it would
find the same story every morning. This script is that memory: a JSON
ledger of every URL the scout has judged, what it decided, and a log of
each run, which the Monday note is built from.

URLs are compared after normalizing, so the same article reached with a
tracking parameter, a trailing slash, or "www." still counts as seen.

Subcommands:
  check URL [URL ...]   Prints SEEN or NEW for each URL
  add URL --status S    Records a URL (statuses listed in STATUSES)
  status CASE --status S
                        Changes the status of every URL for a candidate
  run --checked N --new N --updates N
                        Logs one daily run
  week [--today YYYY-MM-DD]
                        Prints the Monday note for the seven days before

Exit status is 0 unless the arguments are wrong.
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta
from urllib.parse import urlsplit, urlunsplit

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(REPO, "scout", "seen.json")

# What the scout decided about a story. "case" means it is already in
# the registry, "proposed" and "answered" track an emailed candidate
# through Annie's reply, and the rest close it out.
STATUSES = ("case", "proposed", "answered", "rejected", "irrelevant",
            "borderline", "update")


# ========================================================================
#   The Ledger
# ========================================================================

def normalize(url: str) -> str:
    """
    Reduces a URL to the form used for comparison, so trivial differences do not make an old story look new
    Args:
        url (str): Any URL as the search returned it
    Returns:
        str: Lowercased host without "www.", path without a trailing slash, and no query or fragment
    """
    parts = urlsplit(url.strip())
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path.rstrip("/") or "/"
    return urlunsplit(("https", host, path, "", ""))


def load() -> dict:
    """
    Reads the ledger, starting an empty one if the file does not exist yet
    Returns:
        dict: The ledger, with a "stories" list and a "runs" list
    """
    if not os.path.exists(LEDGER):
        return {"stories": [], "runs": []}
    with open(LEDGER) as f:
        return json.load(f)


def save(ledger: dict) -> None:
    """
    Writes the ledger back with stable formatting so its git diffs stay readable
    Args:
        ledger (dict): The ledger to write
    """
    with open(LEDGER, "w") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ========================================================================
#   Subcommands
# ========================================================================

def check(ledger: dict, urls: list) -> None:
    """
    Prints whether each URL is already in the ledger
    Args:
        ledger (dict): The ledger
        urls (list): URLs to look up
    """
    seen = {s["url"]: s for s in ledger["stories"]}
    for url in urls:
        hit = seen.get(normalize(url))
        if hit:
            print(f"SEEN  {hit['status']:10} {hit.get('case') or '-':10} {url}")
        else:
            print(f"NEW   {url}")


def add(ledger: dict, url: str, status: str, case: str, title: str, today: str) -> None:
    """
    Records a story, or updates its status if the URL is already there
    Args:
        ledger (dict): The ledger
        url (str): The story's URL
        status (str): One of STATUSES
        case (str): The registry or candidate id it belongs to, or an empty string
        title (str): The headline, for a person reading the file
        today (str): The date to stamp a new entry with, as YYYY-MM-DD
    """
    key = normalize(url)
    for story in ledger["stories"]:
        if story["url"] == key:
            story["status"] = status
            # One article can cover several cases (Politico broke both
            # the Census and SEC cases), so ids accumulate
            ids = [c for c in (story.get("case") or "").split(",") if c]
            if case and case not in ids:
                ids.append(case)
            story["case"] = ",".join(ids) or None
            return
    ledger["stories"].append({"url": key, "title": title, "case": case or None,
                              "status": status, "first_seen": today})


def week(ledger: dict, today: date) -> str:
    """
    Builds the Monday note covering the seven days before the given date
    Args:
        ledger (dict): The ledger
        today (date): The Monday the note goes out
    Returns:
        str: The note's text, a few lines long
    """
    start = today - timedelta(days=7)
    runs = [r for r in ledger["runs"] if start <= date.fromisoformat(r["date"]) < today]
    checked = sum(r["checked"] for r in runs)
    new = sum(r["new"] for r in runs)
    updates = sum(r["updates"] for r in runs)
    waiting = [s["case"] for s in ledger["stories"] if s["status"] == "proposed" and s.get("case")]
    lines = [f"Models Gone Wild scout, week of {start.strftime('%b %-d')}: "
             f"{len(runs)} of 7 daily runs, {checked} stories checked, "
             f"{new} new cases, {updates} updates."]
    if len(runs) < 7:
        lines.append(f"{7 - len(runs)} runs are missing from the log, so the job may have failed on those days.")
    if waiting:
        lines.append("Still waiting on your answers: " + ", ".join(sorted(set(waiting))) + ".")
    elif not new and not updates:
        lines.append("Nothing needs you.")
    return "\n".join(lines)


def main() -> int:
    """
    Parses the subcommand and runs it against the ledger
    Returns:
        int: 0 on success, 2 when the arguments are wrong
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("urls", nargs="+")
    p = sub.add_parser("add")
    p.add_argument("url")
    p.add_argument("--status", required=True, choices=STATUSES)
    p.add_argument("--case", default="")
    p.add_argument("--title", default="")
    p = sub.add_parser("status")
    p.add_argument("case")
    p.add_argument("--status", required=True, choices=STATUSES)
    p = sub.add_parser("run")
    p.add_argument("--checked", type=int, required=True)
    p.add_argument("--new", type=int, required=True)
    p.add_argument("--updates", type=int, required=True)
    p = sub.add_parser("week")
    p.add_argument("--today", default=date.today().isoformat())
    opts = ap.parse_args()

    ledger = load()
    today = date.today().isoformat()
    if opts.cmd == "check":
        check(ledger, opts.urls)
        return 0
    if opts.cmd == "week":
        print(week(ledger, date.fromisoformat(opts.today)))
        return 0
    if opts.cmd == "add":
        add(ledger, opts.url, opts.status, opts.case, opts.title, today)
    elif opts.cmd == "status":
        for story in ledger["stories"]:
            if opts.case in (story.get("case") or "").split(","):
                story["status"] = opts.status
    elif opts.cmd == "run":
        ledger["runs"].append({"date": today, "checked": opts.checked,
                               "new": opts.new, "updates": opts.updates})
    save(ledger)
    return 0


if __name__ == "__main__":
    sys.exit(main())
