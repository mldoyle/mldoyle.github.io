#!/usr/bin/env python3
"""Render the project backtest notebook inside the portfolio's page chrome."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re

import nbformat
from nbconvert import HTMLExporter


PAGE_TITLE = "Institutional Order Flow Imblanace — Matthew Doyle"
PAGE_DESCRIPTION = (
    "A long-short equity strategy covering testing: 13.9% ANR, 1.61 Sharpe and "
    "6.1% maximum drawdown. (signal research, risk modeling, portfolio optimization)"
)

PAGE_HEADER = """<header class="notebook-nav">
  <a class="brand" href="../index.html">MD<span>.</span></a>
  <span class="note-label">Research notebook / 2026</span>
  <a href="../index.html#work">← Back to work</a>
</header>
<section class="notebook-hero">
  <div class="notebook-hero-inner">
    <p class="notebook-kicker">Quantitative research / Equity markets</p>
    <h1>Institutional Order Flow Imblanace</h1>
    <p class="notebook-summary">A long-short equity strategy covering testing: 13.9% ANR, 1.61 Sharpe and 6.1% maximum drawdown. (signal research, risk modeling, portfolio optimization)</p>
    <div class="notebook-controls">
      <button aria-controls="notebook-content" aria-expanded="false" aria-pressed="false" id="code-toggle" type="button">Show code</button>
    </div>
  </div>
</section>"""

PAGE_FOOTER = """<p class="notebook-disclaimer">This is a research notebook, not investment advice. Backtested results are hypothetical, depend on stated assumptions and data, and do not guarantee future performance.</p>
<footer class="notebook-footer">
  <span>© 2026 Matthew Doyle</span>
  <a href="mailto:matthew.doyle@icloud.com">matthew.doyle@icloud.com</a>
</footer>
<script>
  const codeToggle = document.getElementById('code-toggle');
  codeToggle.addEventListener('click', () => {
    const codeIsHidden = document.body.classList.toggle('hide-code');
    codeToggle.textContent = codeIsHidden ? 'Show code' : 'Hide code';
    codeToggle.setAttribute('aria-pressed', String(!codeIsHidden));
    codeToggle.setAttribute('aria-expanded', String(!codeIsHidden));
  });
</script>"""


def render(source: Path) -> str:
    notebook = nbformat.read(source, as_version=4)
    exporter = HTMLExporter(template_name="lab")
    document, _ = exporter.from_notebook_node(
        notebook,
        resources={"metadata": {"name": source.stem}},
    )

    metadata = "\n".join(
        (
            f"<title>{escape(PAGE_TITLE)}</title>",
            f'<meta name="description" content="{escape(PAGE_DESCRIPTION, quote=True)}">',
            '<meta property="og:type" content="article">',
            f'<meta property="og:title" content="{escape(PAGE_TITLE, quote=True)}">',
            f'<meta property="og:description" content="{escape(PAGE_DESCRIPTION, quote=True)}">',
            '<meta property="og:url" content="https://mldoyle.github.io/notebooks/order-flow-backtest.html">',
            '<link rel="canonical" href="https://mldoyle.github.io/notebooks/order-flow-backtest.html">',
        )
    )
    document, title_count = re.subn(
        r"<title>.*?</title>",
        metadata,
        document,
        count=1,
        flags=re.DOTALL,
    )
    if title_count != 1:
        raise RuntimeError("Could not replace the generated document title.")

    stylesheet = '<link rel="stylesheet" href="order-flow-backtest.css">\n'
    if "</head>" not in document:
        raise RuntimeError("Generated notebook has no closing head element.")
    document = document.replace("</head>", stylesheet + "</head>", 1)

    body_pattern = re.compile(
        r'<body class="jp-Notebook"(?P<attributes>[^>]*)>\s*<main>'
    )
    body_replacement = (
        r'<body class="jp-Notebook hide-code"\g<attributes>>\n'
        + PAGE_HEADER
        + '\n<main id="notebook-content">'
    )
    document, body_count = body_pattern.subn(body_replacement, document, count=1)
    if body_count != 1:
        raise RuntimeError("Could not add the portfolio header to the generated notebook.")

    document, footer_count = re.subn(
        r"</main>\s*</body>",
        "</main>\n" + PAGE_FOOTER + "\n</body>",
        document,
        count=1,
    )
    if footer_count != 1:
        raise RuntimeError("Could not add the portfolio footer to the generated notebook.")

    return document


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=Path("notebooks/order-flow-backtest.ipynb"),
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=Path("notebooks/order-flow-backtest.html"),
    )
    args = parser.parse_args()

    rendered = render(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Rendered {args.source} to {args.output}.")


if __name__ == "__main__":
    main()
