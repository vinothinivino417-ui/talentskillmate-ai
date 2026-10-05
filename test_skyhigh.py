from pathlib import Path

from resume_parser import extract_text_from_pdf
from skyhigh_agent import run_skyhigh


RESUME_PATH = Path("sample_resume.pdf")


JOB_DESCRIPTION = """
We are looking for an AI / Automation Developer.

Requirements:
- Python
- Streamlit
- AI tools and automation
- Prompt engineering
- Chatbot development
- Good communication
- Problem solving
"""


def main():

    print("\n" + "=" * 60)
    print("              SKYHIGH AI AGENT")
    print("=" * 60)

    if not RESUME_PATH.exists():
        print("Resume file not found.")
        return

    print("\n[1/5] Reading resume...")

    file_bytes = RESUME_PATH.read_bytes()

    resume_text = extract_text_from_pdf(
        file_bytes
    )

    print("[2/5] Starting SkyHigh workflow...")

    result = run_skyhigh(
        resume_text=resume_text,
        job_description=JOB_DESCRIPTION,
    )

    print("\n[3/5] Workflow completed.")

    print("\n" + "=" * 60)
    print("SKYHIGH RESULT")
    print("=" * 60)

    profile = result["candidate_profile"]

    print(
        "\nCandidate:",
        profile.get("candidate_name"),
    )

    print(
        "Skills:",
        ", ".join(profile.get("skills", [])),
    )

    print(
        "\nCandidate ID:",
        result.get("candidate_id"),
    )

    if result.get("match_report"):

        report = result["match_report"]

        print(
            "\nMatch Score:",
            report.get("match_score"),
        )

        print(
            "\nMatching Skills:",
            ", ".join(
                report.get(
                    "matching_skills",
                    [],
                )
            ),
        )

        print(
            "\nMissing Skills:",
            ", ".join(
                report.get(
                    "missing_skills",
                    [],
                )
            ),
        )

        print(
            "\nExplanation:",
            report.get(
                "match_explanation",
                "",
            ),
        )

    print("\nCompleted Steps:")

    for step in result["steps_completed"]:
        print("✓", step)

    print("\nSkyHigh status:", result["status"])


if __name__ == "__main__":
    main()