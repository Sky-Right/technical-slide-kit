# Writing slides

The builder bundles assets; Remark.js renders the Markdown in the browser. The syntax below uses Remark's existing slide model.

## A slide and its notes

```markdown
name: overview
class: two-columns

# A request through the system

.left[
Explain what the user does.
]

.right[
![Request path](../assets/architecture.svg)
]

???

Explain the arrows, then switch to the live example.
```

Separate slides with `---` on its own line. Metadata belongs at the very top, followed by a blank line. `name` provides a stable URL fragment. Notes after `???` appear in presenter mode; they are also included in the shared HTML.

## Layouts

| Slide class | Use |
| --- | --- |
| `cover` | Centered title, optional `.cover-figure[]`, author/date |
| `closing` | A short, centered ending |
| `title inverse` | Occasional dark section divider |
| `two-columns` / `compare` | `.left[]` and `.right[]`, equal width |
| `command` | A narrower text/command column and a wider figure column |
| `lab` | A short hands-on exercise |
| `quiz` | A question and optional revealed `.answer[]` |
| `compact-code` | Slightly smaller code for a moderately long example |

Block helpers: `.figure[![Alt](path)]`, `.screen[![Alt](path)]`, `.note[text]`, `.caption[text]`, and `.output[code block]`. Use blank lines around Markdown inside multiline containers. Add `.clear[]` after floated columns if you need full-width content below them.

## Code and diagrams

Use fenced code blocks with a language such as `bash`, `python`, `css`, or `text`. Use `text` and `.output[]` for results rather than commands. Keep code short enough that the audience can read it without zooming.

Put images in `assets/`; refer to them relative to the Markdown file, e.g. `../assets/architecture.svg`. Plain Markdown images and quoted HTML `<img src="...">` tags are bundled. Use descriptive alt text. SVG files should be self-contained; their own nested resources are not recursively bundled.

The bundler rejects missing files, remote image URLs, assets outside the project, and CSS `@import`. Download and review an appropriately licensed asset into the project before referencing it. Ordinary hyperlinks remain clickable; they do not cause build-time downloads. Markdown images inside fenced or inline code are kept as literal examples.

Raw HTML is preserved by Remark. Build content you trust. The supported image form is `![Alt](../assets/file.svg)` without an optional quoted title or reference-style image definition.

## Reveals

```markdown
name: question
class: quiz

# Which state changes?

.question[What happens after this command?]

--

.answer[The next step appears when you advance.]
```

A `--` step appends to the current slide and keeps its page number. Use `---` when you want a new page. The print template hides earlier states, leaving the completed logical page once.

## Keep it readable

The canvas is a fixed 16:9 presentation scaled to the available screen. Use roughly one title, one main figure, and a few lines of text. It is designed for desktop presentation, not a scrolling mobile article. Split a crowded page rather than shrinking all the text.

The demo provides 12 logical pages and one reveal. Its browser checker is a fixture for that demo; if you change its structure, update the expected counts and reveal name in `tools/check-browser.cjs`.
