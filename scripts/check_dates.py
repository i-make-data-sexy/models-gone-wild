#!/usr/bin/env python3
"""Checks that each case's escape date, disclosure date, and lag agree.

`date` is when the model first got out, `disclosed` is when the case
went public, and `lag` is the gap between them in words. The lag is
typed by hand, so a corrected date can leave it wrong without anything
else on the page noticing. This script recomputes it.

Where both dates are day-precise, the lag must be "<N> days later" for
the exact count. Where the escape date is an estimate (a month, or a
phrase like "Late July 2026"), the lag is judged by hand and is only
printed here for a reader to check.

It also confirms that `order` is possible given the escape dates. An
estimate is a window rather than a day, so a month-only case may sit on
either side of a dated case inside that month; the check only fails
when the sequence cannot be true. It also fails if a case is disclosed
before it could have escaped.

Exit status is 1 on any failure, 0 otherwise.
"""
import re
import sys
from datetime import datetime, timedelta

SRC = "index.html"


def load_cases(text: str) -> list:
    """
    Pulls every case's dates, lag, and timeline order out of the registry script embedded in the page
    Args:
        text (str): The full contents of index.html
    Returns:
        list: One dict per case with its id, date, disclosed, lag, estimated flag, and order
    """
    js = re.search(r"<script>(.*?)</script>", text, re.S).group(1)
    cases = []
    for cid in re.findall(r'id:"(\w+)"', js):
        blk = re.search(r'\{\s*id:"' + cid + r'".*?\n  \}', js, re.S).group(0)
        get = lambda k: (re.search(k + r':"([^"]*)"', blk) or [None, ""])[1]
        cases.append({
            "id": cid,
            "date": get("date"),
            "disclosed": get("disclosed"),
            "lag": get("lag"),
            "estimated": bool(re.search(r"estimated\s*:\s*true", blk)),
            "order": int(re.search(r"order:(\d+)", blk).group(1)),
        })
    return cases


def parse_day(s: str) -> datetime | None:
    """
    Parses a full 'Month D, YYYY' date
    Args:
        s (str): The date string from the registry
    Returns:
        datetime | None: The parsed day, or None when the string is coarser than a full date
    """
    try:
        return datetime.strptime(s, "%B %d, %Y")
    except ValueError:
        return None


def window(c: dict) -> tuple | None:
    """
    Works out the earliest and latest day a case's escape date could mean
    Args:
        c (dict): One case from load_cases
    Returns:
        tuple | None: The first and last possible day. A full date is its
            own window, a bare month is the whole month, 'Late <Month>' is
            the 21st onward, 'Early' is the first ten days, and 'Mid-' is
            the eleventh through the twentieth. None when the date does not
            parse.
    """
    d = parse_day(c["date"])
    if d:
        return d, d
    m = re.match(r"(Late |Early |Mid-)?(\w+) (\d{4})$", c["date"])
    if not m:
        return None
    lo, hi = {"Late ": (21, 31), "Early ": (1, 10), "Mid-": (11, 20), None: (1, 31)}[m.group(1)]
    first = datetime.strptime(f"{m.group(2)} 1, {m.group(3)}", "%B %d, %Y")
    last = (first.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    return first.replace(day=lo), first.replace(day=min(hi, last.day))


def main() -> int:
    """
    Checks every case's lag against its dates and confirms the timeline order is possible
    Args:
        None
    Returns:
        int: 1 on any failure, 0 otherwise
    """
    cases = load_cases(open(SRC).read())
    bad = 0

    print("Lag between escape and disclosure")
    for c in cases:
        esc, dis = parse_day(c["date"]), parse_day(c["disclosed"])
        if not dis:
            print(f"  FAIL   {c['id']:10} disclosed date is not a full date: {c['disclosed']!r}")
            bad += 1
            continue
        if esc and not c["estimated"]:
            days = (dis - esc).days
            want = f"{days} days later"
            ok = c["lag"] == want and days >= 0
            print(f"  {'OK  ' if ok else 'FAIL'}   {c['id']:10} {c['date']} -> {c['disclosed']}  ::  {c['lag']!r}"
                  + ("" if ok else f"  (expected {want!r})"))
            bad += not ok
        else:
            win = window(c)
            if win is None or win[0] > dis:
                print(f"  FAIL   {c['id']:10} estimate {c['date']!r} does not parse, or falls after disclosure")
                bad += 1
            else:
                print(f"  READ   {c['id']:10} {c['date']} (est.) -> {c['disclosed']}  ::  {c['lag']!r}")

    print("\nTimeline order is possible given the escape dates")
    seq = sorted(cases, key=lambda c: c["order"])
    for a, b in zip(seq, seq[1:]):
        wa, wb = window(a), window(b)
        # Case a precedes case b in the timeline. That is only impossible
        # when the earliest b could be is still before the latest a could be.
        ok = wa and wb and wa[0] <= wb[1]
        print(f"  {'OK  ' if ok else 'FAIL'}   {a['id']} ({a['date']}) before {b['id']} ({b['date']})")
        bad += not ok

    print("\n" + ("dates OK" if not bad else f"{bad} problem(s)"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
