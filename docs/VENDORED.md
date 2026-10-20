# Vendored Files

The app ships one third-party library, copied into `public/js/vendor/` rather than installed, so `pip-audit` cannot see it. This file is its record.

## html2canvas

- Version: 1.4.1, from 2022, the latest release as of 2026-10-16
- Source: [html2canvas.hertzen.com](https://html2canvas.hertzen.com)
- License: MIT, copyright 2022 Niklas von Hertzen, kept in the notice at the top of the file
- SHA-256: `e87e550794322e574a1fda0c1549a3c70dae5a93d9113417a429016838eab8cb`
- Used by: `downloadPoster()` in `public/js/poster.js`, which draws the open poster as a PNG for the poster's download button

While it copies the poster, html2canvas adds one fixed `<style>` block to the copy, which hides the original `::before` and `::after` content. The Content Security Policy in `deploy/nginx/headers.conf` allows that one block by its hash in `style-src` (`'sha256-UP0QZg7irvSMvOBz9mH2PIIE28+57UiavRfeVea0l3g='`), so a download logs no violation. `tests/test_csp.py` rebuilds the block from the library and checks the policy names its hash, so a new version that changes the block fails the suite.

`tests/test_dependencies.py` hashes `public/js/vendor/html2canvas.min.js` and compares the result with the SHA-256 above, so a changed copy fails the suite. To update the library, replace the file, record its new version and hash here, update the style hash in the policy if `tests/test_csp.py` fails, and check a poster download in a browser.

This record sits in `docs/`, outside `public/`, so nginx never serves it.