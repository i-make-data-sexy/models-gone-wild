# ========================================================================
#   About This File
# ========================================================================

# Guards the design tokens outside the stylesheets. The pages and the
# app's own scripts may carry no hex color, since every color lives as a
# token in css/variables.css. The pages color through classes, and the
# scripts read each color with cssToken() at startup. Every token a
# script reads must be defined, or it would draw with an empty color.
# Vendored files in js/vendor/ are left out.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re

from pathlib import Path

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

SITE  = Path(__file__).resolve().parent.parent / "public"

PAGES = ["index.html", "methodology/index.html", "404.html"]

JS_FILES = sorted(path.name for path in (SITE / "js").glob("*.js"))

HEX      = re.compile(r"(?<![&\w])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")



# ========================================================================
#   Helpers
# ========================================================================

def read(name: str) -> str:
    """
    Reads a file in public/ as UTF-8 text

    Args:
        name (str): The file's path from public/

    Returns:
        str: The file's contents
    """

    return (SITE / name).read_text(encoding="utf-8")


def hex_colors(text: str) -> list[str]:
    """
    Lists every hex color in a file's text, HTML entities left out

    Args:
        text (str): The file's contents

    Returns:
        list[str]: Each hex color found, in order
    """

    return HEX.findall(text)


def token_values() -> dict[str, str]:
    """
    Reads every token defined in css/variables.css

    Args:
        None

    Returns:
        dict[str, str]: Each token's name mapped to its value
    """

    return dict(re.findall(r"^\s*(--[\w-]+)\s*:\s*([^;]+);", read("css/variables.css"), re.M))



# ========================================================================
#   No Hex Colors
# ========================================================================

def test_matcher_skips_entities_and_finds_colors() -> None:
    """
    Checks the matcher ignores an HTML entity and catches each hex length

    Args:
        None

    Returns:
        None
    """

    tokens = token_values()
    self_  = tokens["--disc-self"]
    tip    = tokens["--disc-tip"]
    text   = f'arrow &#{ord("→")}; then fill="{self_}" stroke="#fff" glow="{tip}cc"'

    assert hex_colors(text) == [self_, "#fff", f"{tip}cc"]


@pytest.mark.parametrize("page", PAGES)
def test_page_has_no_hex_color(page: str) -> None:
    """
    Checks a page colors its markup through classes, not hex values

    Args:
        page (str): The page's path from public/

    Returns:
        None
    """

    assert hex_colors(read(page)) == []


@pytest.mark.parametrize("name", JS_FILES)
def test_script_has_no_hex_color(name: str) -> None:
    """
    Checks a script reads its colors from the tokens, not hex values

    Args:
        name (str): The name of one of the app's files in js/

    Returns:
        None
    """

    assert hex_colors(read(f"js/{name}")) == []



# ========================================================================
#   Tokens the Script Reads
# ========================================================================

def test_script_tokens_are_defined() -> None:
    """
    Checks every token a script passes to cssToken() is defined in variables.css

    Args:
        None

    Returns:
        None
    """

    defined = set(token_values())
    read_by = {
        token
        for name in JS_FILES
        for token in re.findall(r"""cssToken\(\s*["'](--[\w-]+)["']\s*\)""", read(f"js/{name}"))
    }

    assert read_by
    assert sorted(read_by - defined) == []