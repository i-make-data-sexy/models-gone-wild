# ========================================================================
#   About This File
# ========================================================================

# Guards the pages against inline code, which a Content Security Policy
# without 'unsafe-inline' would block. Each page may load scripts only
# by src, apart from JSON data blocks, and may carry no <style> block,
# style attribute, or on* handler. The HTML the app's own scripts build
# in template literals may carry no style attribute or on* handler
# either. Vendored files in js/vendor/ are left out.



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

REPO  = Path(__file__).resolve().parent.parent

PAGES = [
    page for page in ("index.html", "methodology/index.html", "404.html")
    if (REPO / page).exists()
]

JS_FILES = sorted(path.name for path in (REPO / "js").glob("*.js"))



# ========================================================================
#   Helpers
# ========================================================================

def read(name: str) -> str:
    """
    Reads a file in the repo as UTF-8 text

    Args:
        name (str): The file's path from the repo root

    Returns:
        str: The file's contents
    """

    return (REPO / name).read_text(encoding="utf-8")


def opening_tags(html: str) -> list[str]:
    """
    Lists every opening tag in a page, comments left out

    Args:
        html (str): The page's markup

    Returns:
        list[str]: Each opening tag, from its < to its >
    """

    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)

    return re.findall(r"<[A-Za-z][^>]*>", html)


def regex_end(js: str, i: int) -> int:
    """
    Finds where a regex literal starting at a slash ends, or -1 for a division

    Args:
        js (str): The script's source
        i (int): The index of the slash

    Returns:
        int: The index just past the regex and its flags, or -1 when the slash divides
    """

    before = js[:i].rstrip()
    if before and before[-1] not in "(,=:[!&|?{};" and not before.endswith("return"):
        return -1

    i       += 1
    in_class = False

    while js[i] != "/" or in_class:
        if js[i] == "\\":
            i += 1
        elif js[i] == "[":
            in_class = True
        elif js[i] == "]":
            in_class = False
        i += 1

    i += 1
    while i < len(js) and js[i].isalpha():
        i += 1

    return i


def template_text(js: str) -> str:
    """
    Pulls the literal text out of every template literal in a script

    Args:
        js (str): The script's source

    Returns:
        str: The text of each template, one per line, without its ${} parts
    """

    out   = []
    modes = ["code"]
    i     = 0

    while i < len(js):
        c, mode = js[i], modes[-1]

        if mode == "template":
            if c == "\\":
                out.append(js[i:i + 2])
                i += 2
                continue
            if c == "`":
                modes.pop()
                out.append("\n")
            elif js.startswith("${", i):
                modes.append("expr")
                i += 2
                continue
            else:
                out.append(c)
            i += 1
            continue

        if js.startswith("//", i):
            i = js.find("\n", i) if "\n" in js[i:] else len(js)
        elif js.startswith("/*", i):
            i = js.index("*/", i) + 2
        elif c == "/" and regex_end(js, i) != -1:
            i = regex_end(js, i)
        elif c in "'\"":
            i += 1
            while js[i] != c:
                i += 2 if js[i] == "\\" else 1
            i += 1
        elif c == "`":
            modes.append("template")
            i += 1
        elif c == "{" and mode != "code":
            modes.append("brace")
            i += 1
        elif c == "}" and mode in ("expr", "brace"):
            modes.pop()
            i += 1
        else:
            i += 1

    return "".join(out)



# ========================================================================
#   Pages
# ========================================================================

@pytest.mark.parametrize("page", PAGES)
def test_page_loads_scripts_by_src_only(page: str) -> None:
    """
    Checks a page has no inline script, apart from JSON data blocks

    Args:
        page (str): The page's path from the repo root

    Returns:
        None
    """

    inline = [
        tag for tag in opening_tags(read(page))
        if re.match(r"<script\b", tag, re.I)
        and not re.search(r"\ssrc\s*=", tag, re.I)
        and not re.search(r"""\stype\s*=\s*["']application/json["']""", tag, re.I)
    ]
    assert inline == []


@pytest.mark.parametrize("page", PAGES)
def test_page_has_no_style_block(page: str) -> None:
    """
    Checks a page has no <style> block

    Args:
        page (str): The page's path from the repo root

    Returns:
        None
    """

    assert [tag for tag in opening_tags(read(page)) if re.match(r"<style\b", tag, re.I)] == []


@pytest.mark.parametrize("page", PAGES)
def test_page_has_no_inline_style_or_handler(page: str) -> None:
    """
    Checks no tag in a page carries a style attribute or an on* handler

    Args:
        page (str): The page's path from the repo root

    Returns:
        None
    """

    found = [
        tag for tag in opening_tags(read(page))
        if re.search(r"\s(style|on[a-z]+)\s*=", tag, re.I)
    ]
    assert found == []



# ========================================================================
#   Scripts
# ========================================================================

def test_template_scanner_reads_nested_templates() -> None:
    """
    Checks the scanner finds a template nested inside another's ${} part

    Args:
        None

    Returns:
        None
    """

    js = "const a = `<p>${b ? `<i style=\"x\">` : ''}</p>`; // `not this`\nconst q = s.replace(/\"/g, '`');"
    assert template_text(js) == '<p><i style="x">\n</p>\n'


@pytest.mark.parametrize("name", JS_FILES)
def test_templates_have_no_inline_style_or_handler(name: str) -> None:
    """
    Checks the HTML a script builds carries no style attribute or on* handler

    Args:
        name (str): The name of one of the app's files in js/

    Returns:
        None
    """

    found = re.findall(r"\s(?:style|on[a-z]+)\s*=", template_text(read(f"js/{name}")), re.I)
    assert found == []