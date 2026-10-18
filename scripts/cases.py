# ========================================================================
#   About This File
# ========================================================================

"""
The one loader the check scripts and the tests use to read the cases.

The cases live in the CASES array in js/cases.js, one object per case,
with the object's braces at four spaces and its keys at eight. A case's
block runs from its opening brace to the closing brace at four spaces, so
a nested object or list inside it never ends the block early. Keys on a
line of their own are aligned on one column (whyHarm:       "..."), and
keys packed several to a line are not (id:"sol", slug:"sol-hugging-face"),
so every field pattern here allows whitespace after the colon.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re

from functools import lru_cache
from pathlib   import Path



# ========================================================================
#   Global Variables
# ========================================================================

REPO = Path(__file__).resolve().parent.parent



# ========================================================================
#   Loading
# ========================================================================

@lru_cache(maxsize=1)
def load_cases_js() -> str:
    """
    Reads the case source from js/cases.js

    Args:
        None

    Returns:
        str: The whole file, About section included
    """

    return (REPO / "js" / "cases.js").read_text(encoding="utf-8")


def case_blocks(js: str) -> dict[str, str]:
    """
    Splits the case source into one block of text per case

    Args:
        js (str): The case source, as load_cases_js returns it

    Returns:
        dict[str, str]: Each case's id mapped to its block, in registry order
    """

    return {
        cid: re.search(r'\{\s*id:"' + cid + r'".*?\n    \}', js, re.S).group(0)
        for cid in re.findall(r'id:"(\w+)"', js)
    }



# ========================================================================
#   Fields
# ========================================================================

def text_field(block: str, key: str) -> str:
    """
    Reads one double-quoted field from a case's block

    Args:
        block (str): One case's block from case_blocks
        key (str): The field name, such as "date"

    Returns:
        str: The field's value, or an empty string when the case has none
    """

    found = re.search(r"(?<![\w$])" + key + r':\s*"([^"]*)"', block)

    return found.group(1) if found else ""


def number_field(block: str, key: str) -> int:
    """
    Reads one whole-number field from a case's block

    Args:
        block (str): One case's block from case_blocks
        key (str): The field name, such as "order"

    Returns:
        int: The field's value
    """

    return int(re.search(r"(?<![\w$])" + key + r":\s*(\d+)", block).group(1))