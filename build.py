#!/usr/bin/env python3
"""Compile the JSX sources into index.html without a Node toolchain.

Reads src/app.jsx and src/mount.jsx, transforms them with the vendored
Babel standalone inside headless Chrome, and inlines the result into
index.html. Sources stay the place to edit; index.html is generated.
"""
import base64
import html
import json
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SOURCES = ["src/app.jsx", "src/mount.jsx"]

HARNESS = """<!DOCTYPE html>
<html><body>
<script src="{babel}"></script>
<script>
const sources = {sources};
const out = sources.map(code => Babel.transform(code, {{presets: [['react', {{runtime: 'classic'}}]], comments: false}}).code);
const bytes = new TextEncoder().encode(JSON.stringify(out));
let bin = '';
for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
document.body.innerHTML = '<pre id="out">' + btoa(bin) + '</pre>';
</script>
</body></html>
"""


def compile_sources():
    sources = [(ROOT / p).read_text(encoding="utf-8") for p in SOURCES]
    harness = HARNESS.format(
        babel=(ROOT / "vendor/babel.min.js").as_uri(),
        sources=json.dumps(sources),
    )
    with tempfile.TemporaryDirectory() as tmp:
        page = pathlib.Path(tmp) / "build.html"
        page.write_text(harness, encoding="utf-8")
        result = subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--user-data-dir=" + str(pathlib.Path(tmp) / "profile"),
                "--virtual-time-budget=30000",
                "--dump-dom",
                page.as_uri(),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    match = re.search(r'id="out">([A-Za-z0-9+/=]+)</pre>', result.stdout)
    if not match:
        raise SystemExit(
            "Babel compile failed: no output in Chrome dump\n"
            + result.stdout[:500]
            + "\n"
            + result.stderr[:500]
            + "\n"
            + harness[:300]
        )
    encoded = base64.b64decode(match.group(1)).decode("utf-8")
    return json.loads(encoded)


def inline_into_html(compiled):
    path = ROOT / "index.html"
    page = path.read_text(encoding="utf-8")

    # First build: replace the two text/babel blocks with compiled, marked scripts.
    if '<script type="text/babel">' in page:
        for src, code in zip(SOURCES, compiled):
            page = page.replace(
                '<script type="text/babel">',
                f'<script data-src="{src}">',
                1,
            )
            marker = f'<script data-src="{src}">'
            start = page.index(marker) + len(marker)
            end = page.index("</script>", start)
            page = page[:start] + "\n" + code.replace("</script", "<\\/script") + "\n" + page[end:]
        page = re.sub(r'\n\s*<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>', "", page)
    else:
        for src, code in zip(SOURCES, compiled):
            pattern = re.compile(
                r'(<script data-src="' + re.escape(src) + r'">).*?(</script>)',
                re.S,
            )
            if not pattern.search(page):
                raise SystemExit(f"marker for {src} missing in index.html")
            safe = code.replace("</script", "<\\/script")
            page = pattern.sub(lambda m: m.group(1) + "\n" + safe + "\n" + m.group(2), page, count=1)

    path.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    inline_into_html(compile_sources())
    print("built index.html")
