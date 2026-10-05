import json
from pathlib import Path

from resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
)

from llm_engine import analyze_resume, summarize_resume


RESUME_PATH = Path("sample_resume.pdf")


def main():
    print("\n" + "=" * 50)
    print("  TalentSkillMate AI - Resume Extraction")
    print("=" * 50)

    if not RESUME_PATH.exists():
        print(f"\nResume file not found: {RESUME_PATH}")
        return

    print("\nStep 1: Reading resume...")

    file_bytes = RESUME_PATH.read_bytes()

    print("File name:", RESUME_PATH.name)
    print("File size:", len(file_bytes), "bytes")
    print("PDF header:", file_bytes[:10])

    if RESUME_PATH.suffix.lower() == ".pdf":
        resume_text = extract_text_from_pdf(file_bytes)

    elif RESUME_PATH.suffix.lower() == ".docx":
        resume_text = extract_text_from_docx(file_bytes)

    else:
        print("Unsupported file format.")
        return

    if not resume_text or resume_text.startswith("Error reading"):
        print("\nResume text extraction failed.")
        print(resume_text)
        return

    if resume_text == "No readable text found in this PDF.":
        print("\nNo readable text found in the PDF.")
        return

    print("\nResume text extracted successfully!")

    print("\nStep 2: Analyzing resume with Hugging Face AI...")

    candidate_profile = analyze_resume(resume_text)

    print("\nStep 3: Generating professional summary...")

    summary = summarize_resume(candidate_profile)

    candidate_profile["professional_summary"] = summary

    print("\n" + "=" * 50)
    print("  EXTRACTED CANDIDATE PROFILE")
    print("=" * 50)

    print(json.dumps(
        candidate_profile,
        indent=4,
        ensure_ascii=False,
    ))

    output_path = Path("candidate_profile.json")

    output_path.write_text(
        json.dumps(
            candidate_profile,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nProfile saved successfully:", output_path)


if __name__ == "__main__":
    main()