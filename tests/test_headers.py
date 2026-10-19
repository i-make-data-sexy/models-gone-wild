# ========================================================================
#   About This File
# ========================================================================

# Security header tests. The preview server reads the same snippet nginx
# includes, so each page, asset, and 404 a reader can reach must carry
# all three headers with the values below.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
from collections.abc import Callable

# Third party
import pytest

# Local
from conftest import serve



# ========================================================================
#   Global Variables
# ========================================================================

EXPECTED = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy":        "strict-origin-when-cross-origin",
    "X-Frame-Options":        "SAMEORIGIN",
}

PATHS = [
    "/",
    "/methodology/",
    "/poster/sol-hugging-face/",
    "/css/styles.css",
    "/js/cases.js",
    "/js/vendor/html2canvas.min.js",
    "/no-such-page/",
]



# ========================================================================
#   Snippet
# ========================================================================

def test_snippet_lists_the_three_headers() -> None:
    """
    Checks deploy/nginx/headers.conf holds exactly the three expected headers

    Args:
        None

    Returns:
        None
    """

    assert dict(serve.read_headers()) == EXPECTED



# ========================================================================
#   Responses
# ========================================================================

@pytest.mark.parametrize("path", PATHS)
def test_response_carries_security_headers(fetch: Callable[[str], tuple], path: str) -> None:
    """
    Checks a page, an asset, or a 404 returns all three security headers

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        path (str): The path under the prefix

    Returns:
        None
    """

    _, headers, _ = fetch(path)

    for name, value in EXPECTED.items():
        assert headers.get(name) == value