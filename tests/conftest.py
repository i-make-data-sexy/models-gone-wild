# ========================================================================
#   About This File
# ========================================================================

# Shared fixtures for the test suite. The app is static, so there is no
# Flask test client. Instead a session fixture runs the PreviewHandler
# from scripts/serve.py, which serves the repo at the real prefix and
# answers the same redirects nginx does in production.
#
# The browser marker and its default deselection live here rather than
# in a pytest.ini, since the repo root is the web root and nginx would
# serve a root .ini file to the public.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import http.client
import importlib.util
import sys
import threading

from collections.abc import Callable, Iterator
from functools       import partial
from http.server     import ThreadingHTTPServer
from pathlib         import Path
from types           import ModuleType

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

REPO    = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
PYTHON  = REPO / "venv" / "bin" / "python3"
BROWSER = "browser"



# ========================================================================
#   Script Loading
# ========================================================================

def load_script(name: str) -> ModuleType:
    """
    Imports one of the scripts in scripts/ by file name

    Args:
        name (str): The script's file name without .py

    Returns:
        ModuleType: The imported module
    """

    spec   = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)

    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


serve       = load_script("serve")
cases       = load_script("cases")
check_slugs = load_script("check_slugs")



# ========================================================================
#   Markers
# ========================================================================

def pytest_configure(config: pytest.Config) -> None:
    """
    Registers the browser marker

    Args:
        config (pytest.Config): The pytest configuration

    Returns:
        None
    """

    config.addinivalue_line("markers", f"{BROWSER}: needs headless Chrome, run with -m browser")


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """
    Deselects browser tests unless the run names a marker with -m

    Args:
        config (pytest.Config): The pytest configuration
        items (list): The collected test items, edited in place

    Returns:
        None
    """

    if config.getoption("markexpr"):
        return
    browser = [item for item in items if item.get_closest_marker(BROWSER)]
    if browser:
        config.hook.pytest_deselected(items=browser)
        items[:] = [item for item in items if not item.get_closest_marker(BROWSER)]



# ========================================================================
#   Case Slugs
# ========================================================================

def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """
    Feeds every case's poster slug to any test that takes a slug

    Args:
        metafunc (pytest.Metafunc): The test function being collected

    Returns:
        None
    """

    if "slug" in metafunc.fixturenames:
        slugs = [slug for _, slug in check_slugs.read_cases()]
        metafunc.parametrize("slug", slugs)



# ========================================================================
#   Preview Server
# ========================================================================

class QuietHandler(serve.PreviewHandler):
    """
    The preview handler with its request log silenced
    """

    def log_message(self, format: str, *args: object) -> None:
        """
        Drops the per-request log line

        Args:
            format (str): The log format string
            *args (object): The values for the format string

        Returns:
            None
        """


@pytest.fixture(scope="session")
def server_port() -> Iterator[int]:
    """
    Runs the preview server on a free port for the whole session

    Args:
        None

    Returns:
        Iterator[int]: The port the server listens on
    """

    handler = partial(QuietHandler, directory=str(REPO))
    server  = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread  = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server.server_address[1]
    server.shutdown()
    server.server_close()


@pytest.fixture(scope="session")
def base_url(server_port: int) -> str:
    """
    Gives the app's home page URL on the preview server

    Args:
        server_port (int): The port the preview server listens on

    Returns:
        str: The home page URL, ending in a slash
    """

    return f"http://127.0.0.1:{server_port}{serve.PREFIX}/"


@pytest.fixture(scope="session")
def fetch(server_port: int) -> Callable[[str], tuple]:
    """
    Gives a helper that requests a path without following redirects

    Args:
        server_port (int): The port the preview server listens on

    Returns:
        Callable[[str], tuple]: Takes a path under the prefix and returns status, headers, and body
    """

    def get(path: str) -> tuple:
        """
        Requests one path under the app's prefix

        Args:
            path (str): The path after the prefix, such as "/threat-matrix/", or "" for the bare prefix

        Returns:
            tuple: The status code, the headers as a dict, and the body as text
        """

        conn = http.client.HTTPConnection("127.0.0.1", server_port, timeout=10)
        try:
            conn.request("GET", f"{serve.PREFIX}{path}")
            response = conn.getresponse()
            body     = response.read().decode("utf-8", errors="replace")
            return response.status, dict(response.getheaders()), body
        finally:
            conn.close()

    return get