Testimony generator

This repository generates a Markdown document from a Google Sheet CSV export.

Quick start

1. Set `CSV_URL` env var or pass `--url` to the script (public CSV export URL).

Run locally:

```bash
python generate.py --url "<CSV_EXPORT_URL>" --out small_plates.md
```

CI

The repository includes a GitHub Actions workflow that runs on schedule and on manual dispatch. Put the CSV export URL into the repository secret `CSV_URL`.

See runs: `gh run list --workflow=generate.yml`
View a run log: `gh run view <run-id> --log`

STATUS

done with Journal/Study
next is Journal/Church
