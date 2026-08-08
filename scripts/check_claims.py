#!/usr/bin/env python3
"""Flags copy that a new case can quietly make untrue.

Several lines on the page are claims about the registry as a whole
rather than about one model: the only confirmed zero-day, the least
harmful of the group, a quadrant with nothing in it. Adding a case can
falsify any of them without touching the sentence itself, and nothing
else on the page would notice.

Run this after adding or rescoring a case. Anything it reports as STALE
is copy that now contradicts the data.

Exit status is 1 if a computable claim has gone stale, 0 otherwise.
Review-only reminders never fail the run, since no script can settle
them.
"""
import re
import sys

SRC = "index.html"
MID = 5          # the dashed quadrant dividers sit at 5 on both axes


# ---------------------------------------------------------------- parsing
def load_cases(text):
    js = re.search(r"<script>(.*?)</script>", text, re.S).group(1)
    cases = []
    for cid in re.findall(r'id:"(\w+)"', js):
        blk = re.search(r'\{\s*id:"' + cid + r'".*?\n  \}', js, re.S).group(0)
        get = lambda k: (re.search(k + r':"([^"]*)"', blk) or [None, ""])[1]
        num = lambda k: int(re.search(k + r":(\d+)", blk).group(1))
        cases.append({
            "id": cid,
            "alias": get("alias"),
            "lab": get("lab"),
            "date": get("date"),
            "charge": get("charge"),
            "caution": get("caution"),
            "complexity": num("complexity"),
            "harm": num("harm"),
        })
    return cases


# ------------------------------------------------------------ computable
def check_only_zero_day(cases):
    """Sol's caution and its complexity note both claim sole possession."""
    hits = [c["alias"] for c in cases if "zero-day" in c["charge"].lower()]
    ok = len(hits) <= 1
    return ok, "cases whose charge cites a zero-day: " + (", ".join(hits) or "none")


def check_most_dangerous(cases):
    """Sol's caution calls it the most dangerous escape on the registry."""
    ranked = sorted(cases, key=lambda c: c["complexity"] + c["harm"], reverse=True)
    top = ranked[0]
    ok = top["id"] == "sol"
    return ok, "highest combined score: %s at %d" % (
        top["alias"], top["complexity"] + top["harm"])


def check_least_harmful(cases):
    """Kimi's caution calls it the least harmful of the group."""
    low = min(cases, key=lambda c: (c["harm"], c["complexity"]))
    ok = low["id"] == "kimi"
    return ok, "lowest harm: %s at %d" % (low["alias"], low["harm"])


def check_empty_quadrant(cases):
    """The determined-cheaters note says nothing has landed there."""
    inside = [c["alias"] for c in cases
              if c["complexity"] > MID and c["harm"] < MID]
    ok = not inside
    return ok, "cases in determined cheaters: " + (", ".join(inside) or "none")


def check_registry_year(cases):
    """The masthead reads FIELD REGISTRY 2026."""
    years = sorted({c["date"].split()[-1] for c in cases})
    ok = years == ["2026"]
    return ok, "years represented: " + ", ".join(years)


COMPUTABLE = [
    ("Considered the most dangerous of the 2026 escapes",
     "Sol, caution",
     "another case outscores Sol on complexity plus harm",
     check_most_dangerous),
    ("the only confirmed zero-day",
     "Sol, caution and whyComplexity",
     "a second case is confirmed to have used a zero-day",
     check_only_zero_day),
    ("Least harmful of the group",
     "Kimi K3, caution",
     "a case scores lower on harm",
     check_least_harmful),
    ("No models have been added to this quadrant at the time of writing",
     "QUADRANT_NOTE, determined cheaters",
     "a case lands above 5 on complexity and below 5 on harm",
     check_empty_quadrant),
    ("FIELD REGISTRY 2026",
     "masthead, bureau line",
     "a case is disclosed outside 2026",
     check_registry_year),
]

# Claims no script can settle. Read them and decide.
REVIEW = [
    ("accompanied by an unreleased, unnamed pre-release model, still at large",
     "Sol, aka",
     "that model is named, released, or accounted for"),
    ("Third major lab in a month to disclose the same failure mode",
     "Muse Spark, caution",
     "the ordering of the disclosures is revised"),
    ("Details on the targeted company were withheld",
     "Muse Spark, caution",
     "the company is later named"),
    ("the first freely downloadable open-weight model caught doing it",
     "Kimi K3, caution",
     "an earlier open-weight case comes to light"),
    ("Last updated: <date>",
     "footer",
     "anything at all changes"),
]


def main():
    cases = load_cases(open(SRC).read())
    stale = 0

    print("Claims the data can settle")
    for quote, where, trigger, fn in COMPUTABLE:
        ok, detail = fn(cases)
        if not ok:
            stale += 1
        print("  %-6s %s" % ("OK" if ok else "STALE", quote))
        print("         %s  ::  %s" % (where, detail))
        if not ok:
            print("         goes stale when: %s" % trigger)

    print()
    print("Claims to read yourself")
    for quote, where, trigger in REVIEW:
        print("  %s" % quote)
        print("         %s  ::  revisit if %s" % (where, trigger))

    print()
    print("all claims hold" if not stale
          else "%d claim(s) now contradict the data" % stale)
    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
