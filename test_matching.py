import json
from pathlib import Path

from llm_engine import match_resume_to_job


PROFILE_PATH = Path("candidate_profile.json")


JOB_DESCRIPTION = """
We are looking for an AI/Automation Developer.

Requirements:
- Strong Python knowledge
- Experience with Streamlit
- Knowledge of AI tools and automation
- Experience with chatbot development
- Understanding of prompt engineering
- Good problem-solving skills
- Experience with CrewAI is preferred
"""


def main():
    print("\n" + "=" * 60)
    print("  TalentSkillMate AI - Job Description Matching")
    print("=" * 60)

    if not PROFILE_PATH.exists():
        print("\nCandidate profile not found.")
        print("Please run: python test_resume.py")
        return

    print("\nStep 1: Loading candidate profile...")

    candidate_profile = json.loads(
        PROFILE_PATH.read_text(encoding="utf-8")
    )

    print("Candidate:", candidate_profile.get("candidate_name", "Unknown"))

    print("\nStep 2: Matching candidate with job description...")
    
    match_report = match_resume_to_job(
        candidate_profile,
        JOB_DESCRIPTION
    )

    print("\n" + "=" * 60)
    print("  MATCHING REPORT")
    print("=" * 60)

    print("\nMatch Score:")
    print(match_report.get("match_score", 0), "%")

    print("\nMatching Skills:")
    for skill in match_report.get("matching_skills", []):
        print("  ✓", skill)

    print("\nMissing Skills:")
    for skill in match_report.get("missing_skills", []):
        print("  •", skill)

    print("\nRelevant Experience:")
    for experience in match_report.get("relevant_experience", []):
        print("  ✓", experience)

    print("\nMatch Explanation:")
    print(match_report.get("match_explanation", ""))

    output_path = Path("match_report.json")

    output_path.write_text(
        json.dumps(
            match_report,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("Match report saved successfully:", output_path)
    print("=" * 60)


if __name__ == "__main__":
    main()