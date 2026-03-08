"""Tests for parsers."""

from __future__ import annotations

import pytest

from parsers.file_parser import parse_pdf, parse_docx, parse_txt, parse_resume


class TestParseTxt:
    def test_parses_utf8(self):
        data = b"Python developer with 5 years experience."
        assert parse_txt(data) == "Python developer with 5 years experience."

    def test_strips_whitespace(self):
        data = b"  Hello World  \n\n"
        assert parse_txt(data) == "Hello World"

    def test_handles_replace_errors(self):
        data = b"Valid \xff invalid"
        result = parse_txt(data)
        assert "Valid" in result


class TestParseResume:
    def test_dispatches_txt(self):
        data = b"Resume content here"
        assert parse_resume("resume.txt", data) == "Resume content here"

    def test_dispatches_pdf(self):
        # Minimal single-page PDF (PyMuPDF requires valid structure)
        pdf_bytes = (
            b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n202\n%%EOF"
        )
        result = parse_resume("resume.pdf", pdf_bytes)
        assert isinstance(result, str)

    def test_raises_unsupported_extension(self):
        with pytest.raises(ValueError, match="Unsupported file type"):
            parse_resume("file.xyz", b"content")

    def test_case_insensitive_extension(self):
        data = b"Content"
        assert parse_resume("file.TXT", data) == "Content"
