# Customizing the theme

Edit `theme/custom.css` for small changes. Keep the base theme intact when you want new talks to share the same typography and layout.

```css
:root {
  --accent: #087f8c;
  --ink: #182230;
  --paper: #ffffff;
  --muted: #566479;
}
```

Run `python3 build.py` after changing content, CSS, or images. The finished HTML contains a snapshot of those assets; it does not load later CSS changes dynamically.

## Logo

The theme reserves the original bottom-right position: 22 px from the right edge, 18 px from the bottom, at 50 px high. A Logo is optional.

```bash
python3 build.py --logo assets/example-logo.svg
```

Replace the example with a Logo you may redistribute. The aspect ratio is preserved. You can also set `--brand-logo: url('../assets/your-logo.svg');` in `theme/custom.css`; CSS asset paths are relative to that stylesheet. A CLI Logo takes precedence over that variable.

## Fonts

Droid Serif (400/700) and Inconsolata (400/700) are local, unmodified font files. Their licenses and source information are included. No font CDN is required.

Chinese characters fall back to available system fonts, such as Songti SC or Noto Serif CJK SC. If you need identical Chinese typography on different computers, add a suitably licensed local font, declare it with `@font-face`, and include its license when distributing. The Python builder embeds fonts referenced by CSS `url(...)`.

## HTML template and output

Edit `theme/slides.html` to change Remark settings. Preserve `window.slideshow` if you use the included browser checker. The template keeps the existing keyboard controls, notes, and print behavior.

```bash
python3 build.py content/starter.md --out dist/talk.html --title "Service architecture" --lang en
```

Stylesheets and scripts in this template use project-local paths. CSS references are resolved relative to the CSS file; images relative to Markdown. The output path does not influence asset resolution.

The extracted kit keeps the active HTML workflow. It does not carry over the older course repository's simplified PPTX renderer or its course-specific Git diagram generator. For editable diagrams, edit the SVG sources. For a fixed handout, print the HTML to PDF.
