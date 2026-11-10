# mldoyle.github.io

Matthew Doyle's personal site: quantitative research, coding projects, writing, and résumé.

The site is intentionally static and dependency-free so it can be served directly by GitHub Pages. The rendered research notebook lives in `notebooks/`, alongside its downloadable `.ipynb` source.

The published notebook is the local `laplace-demon/src/notebooks/backtest.ipynb` snapshot saved November 10, 2026, with backtest results through October 23, 2026. Its SHA-256 is `51abf57fe23e4af097ff0f82e6b0808a819a2bfa758d4677cda76313a5742a2e`.

To publish a newer local snapshot, copy it to `notebooks/order-flow-backtest.ipynb`, update the summary in `scripts/build_notebook.py` to match its results, and run `python scripts/build_notebook.py` with `nbconvert==7.17.1` installed. Rendering preserves saved outputs without executing the research notebook.

The **Refresh backtest notebook** workflow runs manually and requires an explicitly selected, reviewed source commit SHA. Scheduled syncing is disabled because local snapshots can be newer than the committed source notebook.
