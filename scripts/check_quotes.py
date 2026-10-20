# ========================================================================
#   About This File
# ========================================================================

"""
Lists every single-quoted span in the case copy and the glossary, so a
quotation never ships in single quotes.

Somebody's words, partial or full, take double quotes. Single quotes are
only for a word or two used as a label or term. A span of three words or
more is almost always a quotation, so it fails the run. One or two words
is printed for a reader to judge, since 'hyper-focused' can be a term.

An opening quote follows a space or a parenthesis and starts a word, so
an apostrophe inside a word (VAHI's) never opens a span. The aka field
is a single-quoted string in the script, not a quotation, so it is
skipped, with any alignment spaces between the key and its value. The
page script is not scanned: it holds code, not copy.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re
import sys

from pathlib import Path



# ========================================================================
#   Scanning
# ========================================================================

def quote_spans(text: str) -> list:
    """
    Finds every single-quoted span in a file's text, skipping the aka field

    Args:
        text (str): The whole file

    Returns:
        list: (line, span, word count) tuples in file order
    """

    opener = re.compile(r"(?<=[\s(])'(?=[A-Za-z])")
    aka    = re.compile(r"(?<![\w$])aka:\s*$")
    spans  = []

    for m in opener.finditer(text):
        if aka.search(text[max(0, m.start() - 40):m.start()]):
            continue

        end = text.find("'", m.end())

        while end != -1 and end + 1 < len(text) and text[end + 1].isalpha():
            end = text.find("'", end + 1)

        span = text[m.start():end + 1]
        spans.append((text.count("\n", 0, m.start()) + 1, span, len(span.strip("'").split())))

    return spans



# ========================================================================
#   Main
# ========================================================================

def main() -> int:
    """
    Prints every span with its verdict

    Args:
        None

    Returns:
        int: 1 when any span is a quotation in single quotes, 0 otherwise
    """

    repo      = Path(__file__).resolve().parent.parent
    max_words = 2
    failed    = 0

    for name in ("public/js/cases.js", "public/js/glossary.js"):
        for line, span, words in quote_spans((repo / name).read_text(encoding="utf-8")):
            if words > max_words:
                failed += 1
                print(f"  QUOTE  {name} line {line}  {span}  ({words} words, use double quotes)")
            else:
                print(f"  READ   {name} line {line}  {span}  (a term is fine, a quotation is not)")

    print("quotes OK" if not failed else f"{failed} quotation(s) in single quotes")

    return 1 if failed else 0



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    sys.exit(main())