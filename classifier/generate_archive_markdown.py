import argparse
import datetime as dt
import json
import os
import pathlib
import re
import unicodedata
from typing import Any

import boto3
import fitz  # PyMuPDF


CATEGORY_SLUGS = [
    "censimento-campanario",
    "storia-cultura",
    "itinerari",
    "modulistica-gare",
    "suonate-classiche",
    "gare-5-campane",
    "gare-6-campane",
    "gare-9-campane",
    "altre-gare",
]


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def yaml_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def extract_first_lines(pdf_path: pathlib.Path, max_lines: int = 10) -> list[str]:
    lines: list[str] = []

    with fitz.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text("text", sort=True)
            for raw_line in text.splitlines():
                line = normalize_text(raw_line)
                if line:
                    lines.append(line)
                if len(lines) >= max_lines:
                    return lines

    return lines


def title_from_filename(pdf_path: pathlib.Path) -> str:
    return pdf_path.stem.replace("-", " ").replace("_", " ").strip().title()


def rule_based_classification(filename: str, lines: list[str]) -> dict[str, Any] | None:
    haystack = normalize_text(" ".join([filename, *lines])).lower()

    # Normalizzazioni utili
    haystack = haystack.replace("à", "a").replace("è", "e").replace("é", "e")
    haystack = haystack.replace("ì", "i").replace("ò", "o").replace("ù", "u")

    rules: list[tuple[str, list[str], float]] = [
        (
            "itinerari",
            [
                r"\bitinerari\b",
                r"\bitinerario\b",
            ],
            0.98,
        ),
        (
            "censimento-campanario",
            [
                r"\bcensimento\b",
                r"\bcampanario\b",
                r"\bcampanili\b",
                r"\bstato del concerto\b",
            ],
            0.95,
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
            0.92,
        ),
        (
            "gare-5-campane",
            [
                r"\b5\s+campane(?:\s+(?:maggiori|minori))?\b",
                r"\bcinque\s+campane\b",
                r"\b(?:a|con(?:\s+le)?|suonata\s+con(?:\s+le)?)\s+5\s+campane\b",
            ],
            0.95,
        ),
        (
            "gare-6-campane",
            [
                r"\b6\s+campane(?:\s+(?:maggiori|minori))?\b",
                r"\bsei\s+campane\b",
                r"\b(?:a|con(?:\s+le)?|suonata\s+con(?:\s+le)?)\s+6\s+campane\b",
            ],
            0.95,
        ),
        (
            "gare-9-campane",
            [
                r"\b9\s+campane(?:\s+(?:maggiori|minori))?\b",
                r"\bnove\s+campane\b",
                r"\b(?:a|con(?:\s+le)?|suonata\s+con(?:\s+le)?)\s+9\s+campane\b",
            ],
            0.95,
        ),
        (
            "suonate-classiche",
            [
                r"\bsuonate classiche\b",
                r"\bsuonata classica\b",
                r"\brepertorio\b",
                r"\bpartitura\b",
            ],
            0.85,
        ),
        (
            "storia-cultura",
            [
                r"\bstoria\b",
                r"\bcultura\b",
                r"\btradizione campanaria\b",
                r"\bmemorie\b",
            ],
            0.85,
        ),
    ]

    for slug, patterns, confidence in rules:
        if any(re.search(pattern, haystack) for pattern in patterns):
            return {
                "category": slug,
                "confidence": confidence,
                "reason": "Classificazione determinata da regole su nome file e prime righe.",
            }

    if re.search(r"\bgara\b|\bgare\b", haystack):
        return {
            "category": "altre-gare",
            "confidence": 0.80,
            "reason": "Documento relativo a gare, ma senza numero di campane riconosciuto.",
        }

    return None


def classify_with_bedrock(
    filename: str,
    lines: list[str],
    categories: list[dict[str, str]],
    model_id: str,
    region: str,
) -> dict[str, Any]:
    client = boto3.client("bedrock-runtime", region_name=region)

    schema = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Titolo leggibile del documento."
            },
            "category": {
                "type": "string",
                "enum": [c["slug"] for c in categories],
                "description": "Slug della categoria scelta."
            },
            "description": {
                "type": "string",
                "description": "Descrizione breve, adatta al frontmatter markdown."
            },
            "confidence": {
                "type": "number",
                "description": "Confidenza tra 0 e 1."
            },
            "reason": {
                "type": "string",
                "description": "Motivazione breve della scelta."
            },
        },
        "required": ["title", "category", "description", "confidence", "reason"],
        "additionalProperties": False,
    }

    prompt = {
        "filename": filename,
        "first_10_lines": lines,
        "allowed_categories": categories,
        "task": (
            "Classifica il documento in UNA sola categoria. "
            "Usa soprattutto nome file e prime righe. "
            "Se ci sono riferimenti espliciti a Itinerari, gare, numero di campane, "
            "modulistica, censimento o storia/cultura, privilegia questi segnali. "
            "Genera anche title e description per un file markdown."
        ),
    }

    response = client.converse(
        modelId=model_id,
        messages=[
            {
                "role": "user",
                "content": [{"text": json.dumps(prompt, ensure_ascii=False)}],
            }
        ],
        inferenceConfig={
            "maxTokens": 600,
            "temperature": 0,
        },
        outputConfig={
            "textFormat": {
                "type": "json_schema",
                "structure": {
                    "jsonSchema": {
                        "schema": json.dumps(schema),
                        "name": "document_archive_metadata",
                    }
                },
            }
        },
    )

    text = response["output"]["message"]["content"][0]["text"]
    result = json.loads(text)

    if result["category"] not in CATEGORY_SLUGS:
        raise ValueError(f"Categoria non valida: {result['category']}")

    return result


def make_markdown(
    title: str,
    slug: str,
    description: str,
    date: str,
    category: str,
    file_path: str,
) -> str:
    return "\n".join(
        [
            "---",
            f"title: {yaml_quote(title)}",
            f"slug: {yaml_quote(slug)}",
            f"description: {yaml_quote(description)}",
            f"date: {yaml_quote(date)}",
            f"category: {yaml_quote(category)}",
            f"file: {yaml_quote(file_path)}",
            "---",
            "",
            title,
            "",
        ]
    )


def unique_output_path(output_dir: pathlib.Path, slug: str) -> pathlib.Path:
    candidate = output_dir / f"{slug}.md"
    return candidate


def process_pdf(
    pdf_path: pathlib.Path,
    output_dir: pathlib.Path,
    categories: list[dict[str, str]],
    date: str,
    docs_prefix: str,
    use_bedrock: bool,
    model_id: str,
    region: str,
) -> dict[str, Any]:
    lines = extract_first_lines(pdf_path)
    title = title_from_filename(pdf_path)
    result = rule_based_classification(pdf_path.name, lines)

    if result is None and use_bedrock:
        result = classify_with_bedrock(
            filename=pdf_path.name,
            lines=lines,
            categories=categories,
            model_id=model_id,
            region=region,
        )

    if result is None:
        result = {
            "title": title,
            "category": "storia-cultura",
            "description": "Documento di archivio relativo alla tradizione campanaria.",
            "confidence": 0.0,
            "reason": "Nessuna regola applicabile e Bedrock disabilitato.",
        }

    final_title = result.get("title") or title
    category = result["category"]

    category_description = next((c["description"] for c in categories if c["slug"] == category), "")

    description = result.get("description") or category_description
    slug = slugify(final_title)
    file_path = f"{docs_prefix.rstrip('/')}/{pdf_path.name}"

    markdown = make_markdown(
        title=final_title,
        slug=slug,
        description=description,
        date=date,
        category=category,
        file_path=file_path,
    )

    now = dt.datetime.now()
    markdown_filename = f"{now.strftime('%Y-%m-%d')}--{slug}.md"
    output_path = unique_output_path(output_dir, markdown_filename)
    output_path.write_text(markdown, encoding="utf-8")

    return {
        "pdf": pdf_path.name,
        "markdown": output_path.name,
        "title": final_title,
        "slug": slug,
        "category": category,
        "confidence": result.get("confidence"),
        "reason": result.get("reason"),
        "first_10_lines": lines,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Cartella contenente i PDF")
    parser.add_argument("--output", required=True, help="Cartella output markdown")
    parser.add_argument("--categories", required=True, help="File categories.json")
    parser.add_argument("--date", default=dt.date.today().isoformat())
    parser.add_argument("--docs-prefix", default="/docs")
    parser.add_argument("--use-bedrock", action="store_true")
    parser.add_argument("--region", default=os.getenv("AWS_REGION", "eu-west-1"))
    parser.add_argument(
        "--model-id",
        default=os.getenv(
            "BEDROCK_MODEL_ID",
            "eu.anthropic.claude-haiku-4-5-20251001-v1:0",
        ),
    )
    parser.add_argument(
        "--limit",
        default=None,
        type=int,
        help="Limite al numero di PDF da processare"
    )

    args = parser.parse_args()

    input_dir = pathlib.Path(args.input)
    output_dir = pathlib.Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    categories = json.loads(pathlib.Path(args.categories).read_text(encoding="utf-8"))

    report = []
    for i, pdf_path in enumerate(sorted(input_dir.glob("*.pdf"))):
        if args.limit is not None and i >= args.limit:
            break
        record = process_pdf(
            pdf_path=pdf_path,
            output_dir=output_dir,
            categories=categories,
            date=args.date,
            docs_prefix=args.docs_prefix,
            use_bedrock=args.use_bedrock,
            model_id=args.model_id,
            region=args.region,
        )
        report.append(record)
        print(f"{record['pdf']} -> {record['markdown']} [{record['category']}]")

    report_path = output_dir / "_classification_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
