# ========================================================================
#   About This File
# ========================================================================

"""
Checks that each case's escape date, disclosure date, and lag agree.

`date` is when the model first got out, `disclosed` is when the case
went public, and `lag` is the gap between them in words. The lag is
typed by hand, so a corrected date can leave it wrong without anything
else on the page noticing. This script recomputes it.

Where both dates are day-precise, the lag must be "<N> days later" for
the exact count. Where the escape date is an estimate (a month, or a
phrase like "Late July 2026"), the lag is judged by hand and is only
printed here for a reader to check.

It also confirms that `order` is possible given the escape dates. An
estimate is a window rather than a day: a bare month is the whole month,
"Late <Month>" is the 21st onward, "Early" is the first ten days, "Mid-"
is the eleventh through the twentieth, and "Summer <year>" runs June 1
through September 22, the widest reading of a news report's "this
summer". A month-only case may sit on either side of a dated case inside
that month, so the check only fails when the sequence cannot be true. It
also fails if a case is disclosed before it could have escaped.

A case whose source never dates the escape says "Date not disclosed",
with the lag "escape date not disclosed". It may fall anywhere before
its disclosure, and it sits after every dated case on the timeline.

Where a case carries a `notice`, its dates are checked too. A "told"
notice must run escape, lab knew, victim told, and its gap must be
"<N> days after <lab> knew" for the exact count. A "found" notice must
have the victim going public before the lab knew.

Exit status is 1 on any failure, 0 otherwise.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re
import sys

from datetime import datetime, timedelta

# Local
from cases import case_blocks, load_cases_js, number_field, text_field



# ========================================================================
#   Global Variables
# ========================================================================

UNDATED = "Date not disclosed"



# ========================================================================
#   Loading
# ========================================================================

def load_cases(js: str) -> list:
    """
    Pulls every case's dates, lag, and timeline order out of the case source

    Args:
        js (str): The case source from js/cases.js

    Returns:
        list: One dict per case with its id, lab, dates, lag, estimated flag, order, and notice
    """

    cases = []

    for cid, block in case_blocks(js).items():
        found  = re.search(r"notice:\s*\{([^}]*)\}", block)
        notice = dict(re.findall(r'(\w+):\s*"([^"]*)"', found.group(1))) if found else {}

        cases.append({
            "id":        cid,
            "lab":       text_field(block, "lab"),
            "notice":    notice,
            "date":      text_field(block, "date"),
            "disclosed": text_field(block, "disclosed"),
            "lag":       text_field(block, "lag"),
            "estimated": bool(re.search(r"estimated\s*:\s*true", block)),
            "order":     number_field(block, "order"),
        })

    return cases



# ========================================================================
#   Dates
# ========================================================================

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


def window(c: dict) -> tuple[datetime, datetime] | None:
    """
    Works out the earliest and latest day a case's escape date could mean

    Args:
        c (dict): One case from load_cases

    Returns:
        tuple[datetime, datetime] | None: The first and last possible day, or None when the date does not parse
    """

    if c["date"] == UNDATED:
        return datetime.min, parse_day(c["disclosed"]) or datetime.max

    d = parse_day(c["date"])

    if d:
        return d, d

    s = re.match(r"Summer (\d{4})$", c["date"])

    if s:
        y = int(s.group(1))
        return datetime(y, 6, 1), datetime(y, 9, 22)

    m = re.match(r"(Late |Early |Mid-)?(\w+) (\d{4})$", c["date"])

    if not m:
        return None

    lo, hi = {"Late ": (21, 31), "Early ": (1, 10), "Mid-": (11, 20), None: (1, 31)}[m.group(1)]
    first = datetime.strptime(f"{m.group(2)} 1, {m.group(3)}", "%B %d, %Y")
    last  = (first.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    return first.replace(day=lo), first.replace(day=min(hi, last.day))



# ========================================================================
#   Checks
# ========================================================================

def check_lags(cases: list) -> int:
    """
    Checks every case's lag against its escape and disclosure dates

    Args:
        cases (list): The cases from load_cases

    Returns:
        int: The number of failures
    """

    undated_lag = "escape date not disclosed"
    bad         = 0

    print("Lag between escape and disclosure")

    for c in cases:
        esc, dis = parse_day(c["date"]), parse_day(c["disclosed"])

        if not dis:
            print(f"  FAIL   {c['id']:10} disclosed date is not a full date: {c['disclosed']!r}")
            bad += 1
            continue

        if c["date"] == UNDATED:
            ok = c["lag"] == undated_lag and not c["estimated"]
            print(f"  {'OK  ' if ok else 'FAIL'}   {c['id']:10} {UNDATED} -> {c['disclosed']}  ::  {c['lag']!r}"
                  + ("" if ok else f"  (expected {undated_lag!r}, with no estimated flag)"))
            bad += not ok
        elif esc and not c["estimated"]:
            days = (dis - esc).days
            want = f"{days} days later"
            ok   = c["lag"] == want and days >= 0
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

    return bad


def check_order(cases: list) -> int:
    """
    Confirms the timeline order is possible given the escape dates

    Args:
        cases (list): The cases from load_cases

    Returns:
        int: The number of failures
    """

    bad = 0
    seq = sorted(cases, key=lambda c: c["order"])

    print("\nTimeline order is possible given the escape dates")

    for a, b in zip(seq, seq[1:]):
        wa, wb = window(a), window(b)
        ok     = wa and wb and wa[0] <= wb[1] and not (a["date"] == UNDATED and b["date"] != UNDATED)
        print(f"  {'OK  ' if ok else 'FAIL'}   {a['id']} ({a['date']}) before {b['id']} ({b['date']})")
        bad += not ok

    return bad


def check_notices(cases: list) -> int:
    """
    Checks each victim notice's dates against the case's other dates

    Args:
        cases (list): The cases from load_cases

    Returns:
        int: The number of failures
    """

    bad = 0

    print("\nVictim notice against the other dates")

    for c in cases:
        n = c["notice"]

        if not n:
            continue

        kind, esc = n.get("kind"), window(c)
        knew      = parse_day(n.get("knew", ""))

        if kind == "told":
            told = parse_day(n.get("told", ""))

            if not (knew and told):
                print(f"  FAIL   {c['id']:10} a told notice needs full knew and told dates")
                bad += 1
                continue

            want = f"{(told - knew).days} days after {c['lab']} knew"
            ok   = told >= knew and n.get("gap") == want and (esc is None or esc[0] <= knew)
            print(f"  {'OK  ' if ok else 'FAIL'}   {c['id']:10} knew {n['knew']} -> told {n['told']}  ::  {n.get('gap')!r}"
                  + ("" if ok else f"  (expected {want!r}, after the escape)"))
            bad += not ok
        elif kind == "found":
            pub = parse_day(n.get("victimDisclosed", ""))
            ok  = bool(pub and knew and pub < knew)
            print(f"  {'OK  ' if ok else 'FAIL'}   {c['id']:10} victim went public {n.get('victimDisclosed')} before the lab knew {n.get('knew')}")
            bad += not ok
        elif kind == "untold":
            print(f"  READ   {c['id']:10} {n.get('who')} not told before the case went public")
        else:
            print(f"  FAIL   {c['id']:10} unknown notice kind {kind!r}")
            bad += 1

    return bad



# ========================================================================
#   Main
# ========================================================================

def main() -> int:
    """
    Runs the lag, order, and notice checks over every case

    Args:
        None

    Returns:
        int: 1 on any failure, 0 otherwise
    """

    cases = load_cases(load_cases_js())
    bad   = check_lags(cases) + check_order(cases) + check_notices(cases)

    print("\n" + ("dates OK" if not bad else f"{bad} problem(s)"))

    return 1 if bad else 0



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    sys.exit(main())