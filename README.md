Testimony generator

This repository generates a Markdown document from a Google Sheet CSV export.

Quick start

1. Set `CSV_URL` env var or pass `--url` to the script (public CSV export URL).

Run locally:

```bash
python generate.py --url "<CSV_EXPORT_URL>" --out output.md
```

CI

The repository includes a GitHub Actions workflow that runs daily and on manual dispatch. Put the CSV export URL into the repository secret `CSV_URL`.
