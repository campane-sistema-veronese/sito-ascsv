import argparse
import csv
import pathlib
import re
import unicodedata

import fitz  # PyMuPDF


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


_ABBREVIATIONS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bgiov(?:\.|\s+)?em\b", re.IGNORECASE), "Giovanile Emergente"),
    (re.compile(r"\bgiov\b", re.IGNORECASE), "Giovanile"),
]


def title_from_filename(pdf_path: pathlib.Path) -> str:
    name = pdf_path.stem.replace("-", " ").replace("_", " ").strip().title()
    for pattern, replacement in _ABBREVIATIONS:
        name = pattern.sub(replacement, name)
    return name


def is_noise_line(line: str) -> bool:
    """Return True if the line consists only of spaces, slashes, and digits."""
    return bool(re.fullmatch(r"[ /\d]+", line))


def extract_page_lines(page, max_lines: int = 5) -> list[str]:
    lines: list[str] = []
    text = page.get_text("text", sort=True)
    for raw_line in text.splitlines():
        line = normalize_text(raw_line)
        if line and not is_noise_line(line):
            lines.append(line)
            if len(lines) >= max_lines:
                break
    return lines


def rule_based_classification(filename: str, lines: list[str]) -> str:
    haystack = normalize_text(" ".join([filename, *lines])).lower()
    haystack = haystack.replace("à", "a").replace("è", "e").replace("é", "e")
    haystack = haystack.replace("ì", "i").replace("ò", "o").replace("ù", "u")

    rules: list[tuple[str, list[str]]] = [
        ("itinerari", [r"\bitinerari\b", r"\bitinerario\b"]),
        (
            "censimento-campanario",
            [
                r"\bcensimento\b",
                r"\bcampanario\b",
                r"\bcampanili\b",
                r"\bstato del concerto\b",
            ],
        ),
        (
            "modulistica-gare",
            [
                r"\bmodulo\b",
                r"\bmodulistica\b",
                r"\bscheda iscrizione\b",
                r"\biscrizione\b",
                r"\bregolamento\b",
            ],
        ),
        (
            "gare-5-campane",
            [
                r"\b5\s+campane(?:\s+(?:maggiori|minori))?\b",
                r"\bcinque\s+campane\b",
                r"\b(?:a|con(?:\s+le)?|suonata\s+con(?:\s+le)?)\s+5\s+campane\b",
            ],
        ),
        (
            "gare-6-campane",
            [
                r"\b6\s+campane(?:\s+(?:maggiori|minori))?\b",
                r"\bsei\s+campane\b",
                r"\b(?:a|con(?:\s+le)?|suonata\s+con(?:\s+le)?)\s+6\s+campane\b",
            ],
        ),
        (
            "gare-9-campane",
            [
                r"\b9\s+campane(?:\s+(?:maggiori|minori))?\b",
                r"\bnove\s+campane\b",
                r"\b(?:a|con(?:\s+le)?|suonata\s+con(?:\s+le)?)\s+9\s+campane\b",
            ],
        ),
        (
            "suonate-classiche",
            [
                r"\bsuonate classiche\b",
                r"\bsuonata classica\b",
                r"\brepertorio\b",
                r"\bpartitura\b",
            ],
        ),
        (
            "storia-cultura",
            [
                r"\bstoria\b",
                r"\bcultura\b",
                r"\btradizione campanaria\b",
                r"\bmemorie\b",
            ],
        ),
    ]

    for slug, patterns in rules:
        if any(re.search(pattern, haystack) for pattern in patterns):
            return slug

    if re.search(r"\bgara\b|\bgare\b", haystack):
        return "altre-gare"

    return "storia-cultura"


def process_pdf(pdf_path: pathlib.Path) -> dict:
    title = title_from_filename(pdf_path)
    slug = slugify(title)

    with fitz.open(pdf_path) as doc:
        num_pages = len(doc)
        page1_lines = extract_page_lines(doc[0]) if num_pages >= 1 else []
        page2_lines = extract_page_lines(doc[1]) if num_pages >= 2 else []

    category = rule_based_classification(pdf_path.name, page1_lines)

    return {
        "filename": pdf_path.name,
        "slug": slug,
        "category": category,
        "title": title,
        "num_pages": num_pages,
        "page1_lines": " | ".join(page1_lines),
        "page2_lines": " | ".join(page2_lines),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Cartella contenente i PDF")
    parser.add_argument("--output", required=True, help="File CSV di output")
    parser.add_argument("--limit", default=None, type=int, help="Limite al numero di PDF da processare")

    args = parser.parse_args()

    input_dir = pathlib.Path(args.input)
    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["filename", "slug", "category", "title", "num_pages", "page1_lines", "page2_lines"]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i, pdf_path in enumerate(sorted(input_dir.glob("*.pdf"))):
            if args.limit is not None and i >= args.limit:
                break
            record = process_pdf(pdf_path)
            writer.writerow(record)
            print(f"{record['filename']} -> [{record['category']}]")


if __name__ == "__main__":
    main()
