#!/usr/bin/env python3
"""Build one offline Remark.js presentation from Markdown using the standard library.

Extracted from ct-slide-kit's HTML bundler; template assets now resolve relative
to the template instead of the output directory. Copyright 2026 Tianyou Yu.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import base64
import html
import mimetypes
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent


def asset_path(value, base, root):
    value = value.strip().strip("<>")
    url = urlsplit(value)
    if url.scheme or url.netloc or value.startswith(("/", "\\")):
        raise ValueError(f"Use a project-local asset, not a URL or absolute path: {value}")
    path = (base / unquote(url.path)).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Asset is outside the project: {value}")
    if not path.is_file():
        raise FileNotFoundError(f"Asset not found: {path}")
    return path


def data_uri(value, base, root):
    if value.startswith(("data:", "#")):
        return value
    path = asset_path(value, base, root)
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    fragment = urlsplit(value.strip().strip("<>")).fragment
    return f"data:{mime};base64,{encoded}" + (f"#{fragment}" if fragment else "")


def inline_markdown(markdown, base, root):
    lines = []
    fence = None
    for line in markdown.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            value = marker.group(1)
            if fence is None:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence):
                fence = None
            lines.append(line)
            continue
        if fence:
            lines.append(line)
            continue
        parts = re.split(r"(`+[^`\n]*`+)", line)
        for i in range(0, len(parts), 2):
            parts[i] = re.sub(r"(!\[[^\]]*\]\()([^\n)]+)(\))",
                              lambda m: m[1] + data_uri(m[2], base, root) + m[3], parts[i])
            parts[i] = re.sub(r'''(<img\b[^>]*\bsrc\s*=\s*)(["'])(.*?)\2''',
                              lambda m: m[1] + m[2] + data_uri(m[3], base, root) + m[2],
                              parts[i], flags=re.I)
        lines.append("".join(parts))
    return "".join(lines)


def build(markdown_path, output, title=None, logo=None, language="en", root=ROOT):
    root = root.resolve()
    markdown_path = markdown_path.resolve()
    if not markdown_path.is_relative_to(root):
        raise ValueError("Put the Markdown source inside the project before building.")
    markdown = markdown_path.read_text(encoding="utf-8")
    heading = re.search(r"^#\s+(.+)$", markdown, flags=re.M)
    title = title or (heading[1] if heading else "Technical slides")
    template_path = root / "theme/slides.html"
    template = template_path.read_text(encoding="utf-8")

    def stylesheet(match):
        path = asset_path(match[1], template_path.parent, root)
        css = path.read_text(encoding="utf-8")
        if re.search(r"@import\b", css):
            raise ValueError(f"Use a local stylesheet link instead of CSS @import: {path}")
        css = re.sub(r'''url\(\s*(["']?)(.*?)\1\s*\)''',
                     lambda m: 'url("' + data_uri(m[2], path.parent, root) + '")', css)
        return "<style>" + css + "</style>"

    def script(match):
        path = asset_path(match[1], template_path.parent, root)
        source = path.read_text(encoding="utf-8")
        return "<script>" + re.sub(r"</script", r"<\\/script", source, flags=re.I) + "</script>"

    template = re.sub(r'<link\s+rel="stylesheet"\s+href="([^"]+)"\s*/?>', stylesheet, template)
    template = re.sub(r'<script\s+src="([^"]+)"\s*></script>', script, template)
    branding = ""
    if logo:
        logo = logo.resolve()
        uri = data_uri(str(logo.relative_to(root)), root, root)
        branding = '<style>:root{--brand-logo:url("' + uri + '")}</style>'
    licenses = "\n\n".join((root / name).read_text(encoding="utf-8") for name in (
        "NOTICE", "LICENSE", "theme/vendor/remark-LICENSE", "theme/fonts/Inconsolata-OFL.txt"))
    replacements = {
        "TITLE": html.escape(title), "LANG": html.escape(language, quote=True),
        "BRANDING": branding,
        "MARKDOWN": html.escape(inline_markdown(markdown, markdown_path.parent, root), quote=False),
        "LICENSES": re.sub(r"</script", r"<\\/script", licenses, flags=re.I),
    }
    rendered = re.sub(r"@@(TITLE|LANG|BRANDING|MARKDOWN|LICENSES)@@",
                      lambda m: replacements[m[1]], template)
    output = output.resolve()
    if output == markdown_path or output.is_relative_to(root / "theme"):
        raise ValueError("Choose an output path outside the source Markdown and theme directory.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", nargs="?", type=Path, default=ROOT / "content/slides.md")
    parser.add_argument("--out", type=Path, default=ROOT / "dist/index.html", help="HTML file to create")
    parser.add_argument("--title", help="Browser title; defaults to the first Markdown heading")
    parser.add_argument("--logo", type=Path, help="Optional logo file inside this project")
    parser.add_argument("--lang", default="en", help="Document language, e.g. en or zh-CN")
    args = parser.parse_args()
    try:
        output = build(args.markdown, args.out, args.title, args.logo, args.lang)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Build failed: {error}\n")
    print(f"Created {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
