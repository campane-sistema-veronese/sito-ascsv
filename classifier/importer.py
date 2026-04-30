"""
tsv_to_ndjson.py — Convert cleaned TSV report to Sanity-importable NDJSON.

Usage:
    python importer.py --tsv output/report.tsv --input input/ --output output/import.ndjson

Then import with the Sanity CLI (from studio-sito-ascsv/):
    npx sanity datasets import ../classifier/output/import.ndjson staging --replace
    npx sanity datasets import ../classifier/output/import.ndjson production --replace
"""

import argparse
import csv
import datetime
import json
import pathlib
import sys


def make_document(row: dict, pdf_path: pathlib.Path, unique_id: str) -> dict:
    slug = row["slug"]
    return {
        "_id": unique_id,
        "_type": "allegato",
        "title": row["title"],
        "slug": {
            "_type": "slug",
            "current": slug,
        },
        "date": datetime.datetime.now(tz=datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        ),
        "category": row["category"],
        "file": {
            "_type": "file",
            "_sanityAsset": f"file@file://{pdf_path.resolve()}",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert cleaned TSV to Sanity NDJSON import file."
    )
    parser.add_argument("--tsv", required=True, help="Path to the cleaned TSV file")
    parser.add_argument("--input", required=True, help="Folder containing PDF files")
    parser.add_argument("--output", required=True, help="Path for the output NDJSON file")
    parser.add_argument(
        "--limit", default=None, type=int, help="Process only the first N rows"
    )
    args = parser.parse_args()

    tsv_path = pathlib.Path(args.tsv)
    input_dir = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    skipped = 0
    written = 0
    seen_ids: dict[str, int] = {}

    with (
        tsv_path.open(encoding="utf-8", newline="") as tsv_file,
        output_path.open("w", encoding="utf-8") as out_file,
    ):
        reader = csv.DictReader(tsv_file, delimiter="\t")

        for i, row in enumerate(reader):
            if args.limit is not None and i >= args.limit:
                break

            filename = row["filename"].strip()
            pdf_path = input_dir / filename

            if not pdf_path.exists():
                print(f"SKIP (not found): {filename}", file=sys.stderr)
                skipped += 1
                continue

            base_id = f"allegato-{row['slug']}"
            count = seen_ids.get(base_id, 0)
            seen_ids[base_id] = count + 1
            unique_id = base_id if count == 0 else f"{base_id}-{count + 1}"
            if count > 0:
                print(f"DUPLICATE slug '{row['slug']}' → assigned id '{unique_id}' for {filename}", file=sys.stderr)

            doc = make_document(row, pdf_path, unique_id)
            out_file.write(json.dumps(doc, ensure_ascii=False) + "\n")
            written += 1
            print(f"OK: {filename} [{row['category']}]")

    print(f"\n{written} documents written to {output_path}")
    if skipped:
        print(f"{skipped} files skipped (PDF not found in {input_dir})", file=sys.stderr)


if __name__ == "__main__":
    main()
