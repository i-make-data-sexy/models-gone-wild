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
MID = 5          # The dashed quadrant dividers sit at 5 on both axes


# ========================================================================
#   Parsing
# ========================================================================

def load_cases(text: str) -> list:
    """
    Pulls every case out of the registry script embedded in the page
    Args:
        text (str): The full contents of index.html
    Returns:
        list: One dict per case with its id, alias, lab, date, charge, caution, complexity, and harm
    """
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


# ========================================================================
#   Computable
# ========================================================================

def check_only_zero_day(cases: list) -> tuple:
    """
    Confirms no more than one case cites a zero-day, the sole-possession claim in Sol's caution and complexity note
    Args:
        cases (list): The cases returned by load_cases
    Returns:
        tuple: Whether the claim holds, and a line naming the cases whose charge cites a zero-day
    """
    hits = [c["alias"] for c in cases if "zero-day" in c["charge"].lower()]
    ok = len(hits) <= 1
    return ok, "cases whose charge cites a zero-day: " + (", ".join(hits) or "none")


def check_most_dangerous(cases: list) -> tuple:
    """
    Confirms Sol still has the highest complexity plus harm, as its caution calls it the most dangerous escape on the registry
    Args:
        cases (list): The cases returned by load_cases
    Returns:
        tuple: Whether the claim holds, and a line naming the top-scoring case and its combined score
    """
    ranked = sorted(cases, key=lambda c: c["complexity"] + c["harm"], reverse=True)
    top = ranked[0]
    ok = top["id"] == "sol"
    return ok, "highest combined score: %s at %d" % (
        top["alias"], top["complexity"] + top["harm"])


def check_least_harmful(cases: list) -> tuple:
    """
    Confirms Kimi still scores lowest on harm, as its caution calls it the least harmful of the group
    Args:
        cases (list): The cases returned by load_cases
    Returns:
        tuple: Whether the claim holds, and a line naming the lowest-harm case and its score, with complexity breaking ties
    """
    low = min(cases, key=lambda c: (c["harm"], c["complexity"]))
    ok = low["id"] == "kimi"
    return ok, "lowest harm: %s at %d" % (low["alias"], low["harm"])


def check_cheater_quadrant(cases: list) -> tuple:
    """
    Confirms OpenAIResearcher still sits in the determined-cheaters quadrant its note places it in
    Args:
        cases (list): The cases returned by load_cases
    Returns:
        tuple: Whether the claim holds, and a line listing every case in the high-complexity, low-harm quadrant
    """
    inside = [c["alias"] for c in cases
              if c["complexity"] > MID and c["harm"] < MID]
    ok = "OpenAIResearcher" in inside
    return ok, "cases in determined cheaters: " + (", ".join(inside) or "none")


def check_registry_year(cases: list) -> tuple:
    """
    Confirms every escape falls in 2026, the year the FIELD REGISTRY 2026 masthead is keyed to
    Args:
        cases (list): The cases returned by load_cases
    Returns:
        tuple: Whether the claim holds, and a line listing the escape years represented
    """
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
    ("OpenAIResearcher sits here",
     "QUADRANT_NOTE, determined cheaters",
     "OpenAIResearcher is rescored out of the quadrant",
     check_cheater_quadrant),
    ("FIELD REGISTRY 2026",
     "masthead, bureau line",
     "a case escapes outside 2026",
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
    ("OpenAI has since confirmed the agents were its own, according to rubyhack.ai",
     "OpenAIResearcher, caution",
     "OpenAI walks the confirmation back, or names the model"),
    ("rubyhack.ai also ties this swarm to the Hugging Face breach, a link this registry could not confirm",
     "Unnamed agent (RubyGems), caution",
     "an independent source confirms or refutes the link to Sol's case"),
    ("tried a caching flaw nobody had found yet",
     "Unnamed agent (RubyGems), whyComplexity",
     "the attempt is shown to have worked, which would end Sol's claim to the only confirmed zero-day"),
    ("Intrusion into three unnamed companies",
     "Gemini, wantedFor and caution",
     "any of the three companies is later named"),
    ("Google \u00b7 unnamed model",
     "Gemini, org",
     "the Gemini version involved is confirmed, which reporting has not fixed beyond ruling out the newest models"),
    ("the minister says the breach did not come up",
     "Unnamed agent (Medicare), caution",
     "OpenAI or Marles gives a different account of the September 1 meeting"),
    ("Related OpenAI agents used urlquery.net",
     "Unnamed agent (Medicare), mo and whyComplexity",
     "Transluce's attribution of the AIHW activity to OpenAI is disputed or withdrawn"),
    ("OpenAI \u00b7 unnamed agent",
     "Unnamed agent (Medicare), org",
     "OpenAI names the model behind the Medicare access"),
    ("one of the three not yet reached when Anthropic published",
     "Opus, Mythos, notice",
     "Anthropic reports reaching the third organization"),
    ("Hugging Face found it on its own and disclosed it July 16, 2026",
     "Sol, notice",
     "the Sol correction pass revises the escape date, the disclosure, or when OpenAI knew"),
    ("RubyGems was not told by OpenAI before the case went public, according to rubyhack.ai",
     "Unnamed agent (RubyGems), notice",
     "OpenAI or Ruby Central says RubyGems was told earlier"),
    ("Last updated: <date>",
     "footer",
     "anything at all changes"),
]


def main() -> int:
    """
    Runs every computable claim check against the registry and prints the review-only reminders
    Args:
        None
    Returns:
        int: 1 if any computable claim has gone stale, 0 otherwise
    """
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
