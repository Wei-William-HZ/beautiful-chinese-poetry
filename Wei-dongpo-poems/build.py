#!/usr/bin/env python3
"""Build self-contained index.html with all poems embedded (no fetch() needed)."""
import os
import json

POEMS_DIR = "poems"
INPUT_HTML = "index.html"
OUTPUT_HTML = "index.html"

def escape_js_template(s):
    """Escape a string for embedding in a JavaScript backtick template literal."""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

def main():
    # Read all .md files
    poems = {}
    for fname in sorted(os.listdir(POEMS_DIR)):
        if fname.endswith(".md"):
            fpath = f"{POEMS_DIR}/{fname}"
            with open(fpath, encoding="utf-8") as f:
                poems[fpath] = f.read()

    # Sort by file path
    sorted_keys = sorted(poems.keys())

    # Build the embedded data JS
    lines = ["<script>", "const EMBEDDED_POEMS = {"]
    for key in sorted_keys:
        escaped = escape_js_template(poems[key])
        lines.append(f'  "{key}": `{escaped}`,')
    lines.append("};")
    lines.append("</script>")
    embedded_script = "\n".join(lines)

    # Read index.html
    with open(INPUT_HTML, encoding="utf-8") as f:
        html = f.read()

    # Find the main <script> tag and insert embedded data before it
    marker = '<script>\n(function() {'
    if marker not in html:
        print("ERROR: Could not find main script marker in index.html")
        return

    # Insert embedded data before the main script
    html = html.replace(
        marker,
        embedded_script + "\n" + marker
    )

    # Replace fetch() call with embedded data lookup
    old_fetch = """      const resp = await fetch(filePath);
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      const rawMd = await resp.text();"""

    new_fetch = """      await new Promise(r => setTimeout(r, 10)); // yield for loading spinner
      const rawMd = EMBEDDED_POEMS[filePath];
      if (!rawMd) throw new Error('Poem not found: ' + filePath);"""

    if old_fetch not in html:
        print("ERROR: Could not find fetch() call in index.html")
        return

    html = html.replace(old_fetch, new_fetch)

    # Write output
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    total_size = len(html)
    poem_data_size = sum(len(v) for v in poems.values())
    print(f"Done! Embedded {len(poems)} poems ({poem_data_size:,} bytes markdown)")
    print(f"Output: {OUTPUT_HTML} ({total_size:,} bytes total)")

if __name__ == "__main__":
    main()
