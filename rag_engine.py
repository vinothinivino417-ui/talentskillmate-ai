import re
import uuid
from pathlib import Path

import chromadb


# ============================================================
# CHROMA DATABASE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

CHROMA_PATH = PROJECT_ROOT / "chroma_db"

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = chroma_client.get_or_create_collection(
    name="candidate_profiles"
)


# ============================================================
# EMPTY RESULT
# ============================================================

def _empty_result():

    return {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
    }


# ============================================================
# CANDIDATE ID
# ============================================================

def create_candidate_id(candidate_profile):

    name = candidate_profile.get(
        "candidate_name",
        "",
    ).strip()

    if not name:
        name = "candidate"

    safe_name = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        name,
    ).strip("_").lower()

    if not safe_name:
        safe_name = "candidate"

    return (
        f"{safe_name}_"
        f"{uuid.uuid4().hex[:8]}"
    )


# ============================================================
# PROFILE → RAG DOCUMENT
# ============================================================

def candidate_to_text(candidate_profile):

    name = candidate_profile.get(
        "candidate_name",
        "",
    )

    email = candidate_profile.get(
        "email",
        "",
    )

    location = candidate_profile.get(
        "location",
        "",
    )

    summary = candidate_profile.get(
        "professional_summary",
        "",
    )

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    skills = ", ".join(
        str(skill)
        for skill in candidate_profile.get(
            "skills",
            [],
        )
    )

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    education_parts = []

    for education in candidate_profile.get(
        "education",
        [],
    ):

        education_parts.append(
            " | ".join(
                str(value)
                for value in [
                    education.get(
                        "degree",
                        "",
                    ),
                    education.get(
                        "institution",
                        "",
                    ),
                    education.get(
                        "year",
                        "",
                    ),
                ]
                if value
            )
        )

    # --------------------------------------------------------
    # WORK EXPERIENCE
    # --------------------------------------------------------

    experience_parts = []

    for experience in candidate_profile.get(
        "work_experience",
        [],
    ):

        responsibilities = ", ".join(
            str(item)
            for item in experience.get(
                "responsibilities",
                [],
            )
        )

        experience_parts.append(
            f"""
Job Title:
{experience.get("job_title", "")}

Company:
{experience.get("company", "")}

Duration:
{experience.get("duration", "")}

Responsibilities:
{responsibilities}
""".strip()
        )

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    project_parts = []

    for project in candidate_profile.get(
        "projects",
        [],
    ):

        technologies = ", ".join(
            str(item)
            for item in project.get(
                "technologies",
                [],
            )
        )

        project_parts.append(
            f"""
Project:
{project.get("project_name", "")}

Description:
{project.get("description", "")}

Technologies:
{technologies}
""".strip()
        )

    # --------------------------------------------------------
    # FINAL DOCUMENT
    # --------------------------------------------------------

    return f"""
Candidate Name:
{name}

Email:
{email}

Location:
{location}

Professional Summary:
{summary}

Skills:
{skills}

Education:
{" | ".join(education_parts)}

Work Experience:
{" | ".join(experience_parts)}

Projects:
{" | ".join(project_parts)}
""".strip()


# ============================================================
# STORE CANDIDATE
# ============================================================

def add_candidate(
    candidate_profile,
    candidate_id=None,
):

    if not candidate_profile:

        raise ValueError(
            "Candidate profile is empty."
        )

    if not candidate_id:

        candidate_id = create_candidate_id(
            candidate_profile
        )

    document = candidate_to_text(
        candidate_profile
    )

    collection.upsert(
        ids=[candidate_id],
        documents=[document],
        metadatas=[
            {
                "candidate_name": str(
                    candidate_profile.get(
                        "candidate_name",
                        "Candidate",
                    )
                ),
                "email": str(
                    candidate_profile.get(
                        "email",
                        "",
                    )
                ),
                "location": str(
                    candidate_profile.get(
                        "location",
                        "",
                    )
                ),
            }
        ],
    )

    return {
        "candidate_id": candidate_id,
        "candidate_name": candidate_profile.get(
            "candidate_name",
            "Candidate",
        ),
        "stored": True,
    }


# ============================================================
# NORMALIZE TEXT
# ============================================================

def _normalize_text(value):

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value or "").lower(),
    ).strip()


# ============================================================
# SEARCH CANDIDATES
# ============================================================

def search_candidates(
    query,
    n_results=5,
):

    # --------------------------------------------------------
    # EMPTY QUERY
    # --------------------------------------------------------

    if not query or not query.strip():

        return _empty_result()

    # --------------------------------------------------------
    # CHECK DATABASE
    # --------------------------------------------------------

    total = collection.count()

    if total == 0:

        return _empty_result()

    query = query.strip()

    n_results = min(
        max(1, n_results),
        total,
    )

    # --------------------------------------------------------
    # GET ALL STORED CANDIDATES
    # --------------------------------------------------------

    all_data = collection.get(
        include=[
            "documents",
            "metadatas",
        ]
    )

    all_ids = all_data.get(
        "ids",
        [],
    )

    all_documents = all_data.get(
        "documents",
        [],
    )

    all_metadatas = all_data.get(
        "metadatas",
        [],
    )

    # --------------------------------------------------------
    # NORMALIZED QUERY
    # --------------------------------------------------------

    normalized_query = _normalize_text(
        query
    )

    # ========================================================
    # 1. CANDIDATE NAME SEARCH
    # ========================================================

    name_matches = []

    if normalized_query:

        query_words = set(
            normalized_query.split()
        )

        for index, metadata in enumerate(
            all_metadatas
        ):

            metadata = metadata or {}

            candidate_name = str(
                metadata.get(
                    "candidate_name",
                    "",
                )
            ).strip()

            if not candidate_name:
                continue

            normalized_name = _normalize_text(
                candidate_name
            )

            if not normalized_name:
                continue

            name_words = set(
                normalized_name.split()
            )

            # Exact / partial name match
            if (
                normalized_query
                in normalized_name
            ):

                name_matches.append(index)

                continue

            # Multi-word name match
            if (
                query_words
                and query_words.issubset(
                    name_words
                )
            ):

                name_matches.append(index)

    # --------------------------------------------------------
    # RETURN NAME MATCHES
    # --------------------------------------------------------

    if name_matches:

        selected = name_matches[
            :n_results
        ]

        return {
            "ids": [[
                all_ids[index]
                for index in selected
            ]],
            "documents": [[
                all_documents[index]
                for index in selected
            ]],
            "metadatas": [[
                all_metadatas[index]
                for index in selected
            ]],
        }

    # ========================================================
    # 2. KEYWORD / SKILL SEARCH
    # ========================================================
    #
    # We remove common recruiter words so that:
    #
    # "Who has experience with AutoCAD and Revit?"
    #
    # becomes:
    #
    # AutoCAD
    # Revit
    #
    # ========================================================

    stop_words = {
        "who",
        "has",
        "have",
        "had",
        "with",
        "experience",
        "experienced",
        "in",
        "on",
        "for",
        "and",
        "or",
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "candidate",
        "candidates",
        "person",
        "people",
        "show",
        "find",
        "me",
        "looking",
        "look",
        "search",
        "please",
        "can",
        "you",
        "do",
        "does",
        "developer",
        "developers",
        "engineer",
        "engineers",
        "skill",
        "skills",
        "knowledge",
        "good",
        "strong",
        "relevant",
        "expert",
        "experts",
        "proficient",
        "proficiency",
        "using",
        "use",
        "used",
    }

    query_words = [
        word
        for word in normalized_query.split()
        if word not in stop_words
        and len(word) > 1
    ]

    # --------------------------------------------------------
    # SCORE EACH CANDIDATE
    # --------------------------------------------------------

    keyword_matches = []

    for index, document in enumerate(
        all_documents
    ):

        document_text = str(
            document or ""
        ).lower()

        matched_words = []

        for word in query_words:

            if word in document_text:

                matched_words.append(
                    word
                )

        if matched_words:

            keyword_matches.append(
                {
                    "index": index,
                    "matched_count": len(
                        matched_words
                    ),
                    "matched_words": (
                        matched_words
                    ),
                }
            )

    # --------------------------------------------------------
    # SORT BY RELEVANCE
    # --------------------------------------------------------

    keyword_matches.sort(
        key=lambda item: (
            item["matched_count"],
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # RETURN RELEVANT CANDIDATES
    # --------------------------------------------------------

    if keyword_matches:

        selected = keyword_matches[
            :n_results
        ]

        selected_indexes = [
            item["index"]
            for item in selected
        ]

        return {
            "ids": [[
                all_ids[index]
                for index in selected_indexes
            ]],
            "documents": [[
                all_documents[index]
                for index in selected_indexes
            ]],
            "metadatas": [[
                all_metadatas[index]
                for index in selected_indexes
            ]],
        }

    # ========================================================
    # 3. SEMANTIC RAG SEARCH
    # ========================================================
    #
    # If no direct keyword was found,
    # use Chroma's semantic search.
    #
    # ========================================================

    try:

        semantic_results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )

        return semantic_results

    except Exception:

        # ====================================================
        # 4. FINAL KEYWORD FALLBACK
        # ====================================================

        query_word_set = set(
            query_words
        )

        scored = []

        for index, document in enumerate(
            all_documents
        ):

            document_words = set(
                re.findall(
                    r"\w+",
                    str(
                        document or ""
                    ).lower(),
                )
            )

            score = len(
                query_word_set.intersection(
                    document_words
                )
            )

            if score > 0:

                scored.append(
                    (
                        score,
                        index,
                    )
                )

        scored.sort(
            reverse=True
        )

        selected = scored[
            :n_results
        ]

        return {
            "ids": [[
                all_ids[index]
                for _, index in selected
            ]],
            "documents": [[
                all_documents[index]
                for _, index in selected
            ]],
            "metadatas": [[
                all_metadatas[index]
                for _, index in selected
            ]],
        }


# ============================================================
# COUNT
# ============================================================

def get_candidate_count():

    return collection.count()


# ============================================================
# ALL CANDIDATES
# ============================================================

def get_all_candidates():

    return collection.get(
        include=[
            "documents",
            "metadatas",
        ]
    )


# ============================================================
# CLEAR ALL CANDIDATES
# ============================================================

def clear_all_candidates():

    data = collection.get()

    candidate_ids = data.get(
        "ids",
        [],
    )

    if candidate_ids:

        collection.delete(
            ids=candidate_ids
        )

    return len(candidate_ids)