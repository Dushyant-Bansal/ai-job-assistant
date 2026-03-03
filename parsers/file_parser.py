"""Utilities for converting uploaded resume files into plain text."""

from __future__ import annotations

import io
from pathlib import Path

import docx
import fitz  # pymupdf


def parse_pdf(data: bytes) -> str:
    doc = fitz.open(stream=data, filetype="pdf")
    pages = [page.get_text() for page in doc]
    doc.close()
    return "\n\n".join(pages).strip()


def parse_docx(data: bytes) -> str:
    doc = docx.Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def parse_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="replace").strip()


def parse_resume(filename: str, data: bytes) -> str:
    """Dispatch to the correct parser based on file extension.

    Returns the extracted plain-text content.
    """
    ext = Path(filename).suffix.lower()
    parsers = {
        ".pdf": parse_pdf,
        ".docx": parse_docx,
        ".txt": parse_txt,
    }
    parser = parsers.get(ext)
    if parser is None:
        raise ValueError(
            f"Unsupported file type '{ext}'. Please upload a PDF, DOCX, or TXT file."
        )
    return parser(data)
