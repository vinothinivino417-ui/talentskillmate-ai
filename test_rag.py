import json
from pathlib import Path

from rag_engine import (
    add_candidate,
    search_candidates,
    get_candidate_count,
)


PROFILE_PATH = Path("candidate_profile.json")


def main():

    print("\n" + "=" * 60)
    print("  TalentSkillMate AI - RAG + ChromaDB Test")
    print("=" * 60)

    # Check candidate profile
    if not PROFILE_PATH.exists():
        print("\nCandidate profile not found.")
        print("Please run: python test_resume.py")
        return

    # Load candidate profile
    candidate_profile = json.loads(
        PROFILE_PATH.read_text(
            encoding="utf-8"
        )
    )

    candidate_name = candidate_profile.get(
        "candidate_name",
        "Unknown"
    )

    print("\nCandidate:", candidate_name)

    # Store candidate
    print("\nStep 1: Storing candidate in ChromaDB...")

    add_candidate(
        candidate_profile,
        candidate_id="candidate_001"
    )

    print("Candidate stored successfully.")

    # Show count
    count = get_candidate_count()

    print("\nCandidates in ChromaDB:", count)

    # Search
    print("\nStep 2: Testing semantic search...")

    query = "Python AI automation chatbot experience"

    print("\nSearch query:")
    print(query)

    results = search_candidates(
        query,
        n_results=3
    )

    print("\n" + "=" * 60)
    print("  SEARCH RESULTS")
    print("=" * 60)

    documents = results.get("documents", [[]])[0]

    if not documents:
        print("\nNo candidates found.")
        return

    for index, document in enumerate(documents, start=1):

        print(f"\nCandidate Result {index}")
        print("-" * 40)
        print(document)

    print("\n" + "=" * 60)
    print("RAG test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()