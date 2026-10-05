import pymupdf
from docx import Document
from pathlib import Path
import io


def extract_text_from_pdf(file_bytes):
    """Extract text from a PDF resume."""
    try:
        text = ""

        with pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        ) as pdf:
            for page in pdf:
                text += page.get_text() + "\n"

        if not text.strip():
            return "No readable text found in this PDF."

        return text.strip()

    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def extract_text_from_docx(file_bytes):
    """Extract text from a DOCX resume."""
    try:
        document = Document(io.BytesIO(file_bytes))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    except Exception as e:
        return f"Error reading DOCX: {str(e)}"


def extract_resume_text(uploaded_file):
    """Extract text from an uploaded PDF or DOCX resume."""
    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)

    elif file_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)

    else:
        raise ValueError(
            "Unsupported file format. Please upload a PDF or DOCX file."
        )