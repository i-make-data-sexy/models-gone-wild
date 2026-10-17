# Vendored Files

The app ships one third-party library, copied into `js/` rather than installed, so `pip-audit` cannot see it. This file is its record.

## html2canvas

- Version: 1.4.1, from 2022, the latest release as of 2026-10-16
- Source: [html2canvas.hertzen.com](https://html2canvas.hertzen.com)
- License: MIT, copyright 2022 Niklas von Hertzen, kept in the notice at the top of the file
- SHA-256: `e87e550794322e574a1fda0c1549a3c70dae5a93d9113417a429016838eab8cb`
- Used by: `downloadPoster()` in `index.html`, which draws the open poster as a PNG for the poster's download button

`tests/test_dependencies.py` hashes `js/html2canvas.min.js` and compares the result with the SHA-256 above, so a changed copy fails the suite. To update the library, replace the file, record its new version and hash here, and check a poster download in a browser.

Nginx's denylist covers `.md`, so this file is never served.