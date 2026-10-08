import re
import uuid
import hashlib
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
# NORMALIZE TEXT
# ============================================================

def _normalize_text(value):
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value or "").lower(),
    ).strip()


# ============================================================
# NORMALIZE EMAIL
# ============================================================

def _normalize_email(value):
    return str(value or "").strip().lower()


# ============================================================
# NORMALIZE PHONE
# ============================================================

def _normalize_phone(value):
    digits = re.sub(
        r"\D",
        "",
        str(value or ""),
    )

    if len(digits) > 10:
        digits = digits[-10:]

    return digits


# ============================================================
# CANDIDATE ID
# ============================================================

def create_candidate_id(candidate_profile):

    email = _normalize_email(
        candidate_profile.get("email", "")
    )

    phone = _normalize_phone(
        candidate_profile.get("phone", "")
    )

    name = str(
        candidate_profile.get(
            "candidate_name",
            "",
        )
    ).strip()

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    if email:

        email_hash = hashlib.sha256(
            email.encode("utf-8")
        ).hexdigest()[:16]

        return f"candidate_email_{email_hash}"

    # --------------------------------------------------------
    # PHONE
    # --------------------------------------------------------

    if phone:

        phone_hash = hashlib.sha256(
            phone.encode("utf-8")
        ).hexdigest()[:16]

        return f"candidate_phone_{phone_hash}"

    # --------------------------------------------------------
    # NO RELIABLE IDENTITY
    #
    # IMPORTANT:
    # Name alone is NOT used for duplicate detection.
    # --------------------------------------------------------

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
# RESUME HASH
# ============================================================

def create_resume_hash(candidate_profile):

    """
    Fallback hash based on the structured profile.

    The preferred hash is the raw uploaded-file hash,
    which is passed from app.py.
    """

    profile_text = str(candidate_profile)

    return hashlib.sha256(
        profile_text.encode("utf-8")
    ).hexdigest()


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

    phone = candidate_profile.get(
        "phone",
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

        if not isinstance(education, dict):
            continue

        education_parts.append(
            " | ".join(
                str(value)
                for value in [
                    education.get("degree", ""),
                    education.get("institution", ""),
                    education.get("year", ""),
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

        if not isinstance(experience, dict):
            continue

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

        if not isinstance(project, dict):
            continue

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

Phone:
{phone}

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
# FIND EXISTING CANDIDATE
# ============================================================

def _find_existing_candidate(
    candidate_profile,
    resume_hash=None,
):
    """
    Find existing candidate records.

    Duplicate rules:

    1. Same email → duplicate
    2. Same phone when email is unavailable → duplicate
    3. Same exact uploaded resume hash → duplicate
    4. Same name alone → NOT duplicate

    Multiple matching old records are returned so they
    can all be cleaned up during replacement.
    """

    if collection.count() == 0:
        return []

    stored = collection.get(
        include=["metadatas"]
    )

    all_ids = stored.get("ids", [])
    all_metadatas = stored.get("metadatas", [])

    candidate_email = _normalize_email(
        candidate_profile.get("email", "")
    )

    candidate_phone = _normalize_phone(
        candidate_profile.get("phone", "")
    )

    candidate_hash = str(
        resume_hash or ""
    ).strip()

    # Fallback only when raw hash was not supplied.
    if not candidate_hash:
        candidate_hash = create_resume_hash(
            candidate_profile
        )

    matches = []

    for index, metadata in enumerate(
        all_metadatas
    ):

        metadata = metadata or {}

        stored_email = _normalize_email(
            metadata.get("email", "")
        )

        stored_phone = _normalize_phone(
            metadata.get("phone", "")
        )

        stored_hash = str(
            metadata.get(
                "resume_hash",
                "",
            )
        ).strip()

        candidate_id = (
            all_ids[index]
            if index < len(all_ids)
            else ""
        )

        # ----------------------------------------------------
        # SAME EMAIL
        #
        # Email is the strongest identity.
        # ----------------------------------------------------

        if (
            candidate_email
            and stored_email
            and candidate_email == stored_email
        ):

            matches.append(
                {
                    "id": candidate_id,
                    "reason": "same_email",
                }
            )

            continue

        # ----------------------------------------------------
        # SAME PHONE
        #
        # Only use phone when the new resume has no email.
        # ----------------------------------------------------

        if (
            not candidate_email
            and candidate_phone
            and stored_phone
            and candidate_phone == stored_phone
        ):

            matches.append(
                {
                    "id": candidate_id,
                    "reason": "same_phone",
                }
            )

            continue

        # ----------------------------------------------------
        # SAME EXACT RESUME
        # ----------------------------------------------------

        if (
            candidate_hash
            and stored_hash
            and candidate_hash == stored_hash
        ):

            matches.append(
                {
                    "id": candidate_id,
                    "reason": "same_resume",
                }
            )

    return matches


# ============================================================
# STORE / REPLACE CANDIDATE
# ============================================================

def add_candidate(
    candidate_profile,
    candidate_id=None,
    resume_hash=None,
):

    if not candidate_profile:
        raise ValueError(
            "Candidate profile is empty."
        )

    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    document = candidate_to_text(
        candidate_profile
    )

    # --------------------------------------------------------
    # RAW RESUME HASH
    # --------------------------------------------------------

    final_resume_hash = str(
        resume_hash or ""
    ).strip()

    if not final_resume_hash:

        final_resume_hash = create_resume_hash(
            candidate_profile
        )

    # --------------------------------------------------------
    # FIND EXISTING
    # --------------------------------------------------------

    existing_candidates = (
        _find_existing_candidate(
            candidate_profile,
            resume_hash=final_resume_hash,
        )
    )

    # --------------------------------------------------------
    # DETERMINE ID
    # --------------------------------------------------------

    if existing_candidates:

        # IMPORTANT:
        # Always reuse the existing ID.
        #
        # Do NOT use the newly generated candidate_id
        # when replacing an existing candidate.

        new_candidate_id = existing_candidates[0][
            "id"
        ]

        if not new_candidate_id:

            new_candidate_id = (
                candidate_id
                or create_candidate_id(
                    candidate_profile
                )
            )

    else:

        new_candidate_id = (
            candidate_id
            or create_candidate_id(
                candidate_profile
            )
        )

    # ========================================================
    # DELETE OLD MATCHING RECORDS
    # ========================================================

    replaced = bool(
        existing_candidates
    )

    replacement_reason = ""

    if existing_candidates:

        replacement_reason = (
            existing_candidates[0].get(
                "reason",
                "existing_candidate",
            )
        )

        # Delete every matching record except
        # the ID that we are going to upsert.

        old_ids = [
            item["id"]
            for item in existing_candidates
            if item.get("id")
            and item.get("id") != new_candidate_id
        ]

        if old_ids:

            collection.delete(
                ids=old_ids
            )

    # ========================================================
    # STORE LATEST VERSION
    # ========================================================

    collection.upsert(
        ids=[new_candidate_id],

        documents=[document],

        metadatas=[
            {
                "candidate_name": str(
                    candidate_profile.get(
                        "candidate_name",
                        "Candidate",
                    )
                ),

                "email": _normalize_email(
                    candidate_profile.get(
                        "email",
                        "",
                    )
                ),

                "phone": _normalize_phone(
                    candidate_profile.get(
                        "phone",
                        "",
                    )
                ),

                "location": str(
                    candidate_profile.get(
                        "location",
                        "",
                    )
                ),

                "resume_hash": final_resume_hash,

                "storage_status": (
                    "replaced"
                    if replaced
                    else "new"
                ),
            }
        ],
    )

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "candidate_id": new_candidate_id,

        "candidate_name": candidate_profile.get(
            "candidate_name",
            "Candidate",
        ),

        "stored": True,

        "replaced": replaced,

        "replacement_reason": (
            replacement_reason
            if replaced
            else ""
        ),

        "message": (
            "Existing candidate resume replaced "
            "with the latest resume."
            if replaced
            else
            "New candidate resume stored successfully."
        ),
    }


# ============================================================
# SEARCH CANDIDATES
# ============================================================

def search_candidates(
    query,
    n_results=5,
):

    if not query or not query.strip():
        return _empty_result()

    total = collection.count()

    if total == 0:
        return _empty_result()

    query = query.strip()

    n_results = min(
        max(1, n_results),
        total,
    )

    # --------------------------------------------------------
    # GET ALL CANDIDATES
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

    normalized_query = _normalize_text(
        query
    )

    # ========================================================
    # NAME SEARCH
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

            if normalized_query in normalized_name:

                name_matches.append(index)

                continue

            if (
                query_words
                and query_words.issubset(name_words)
            ):

                name_matches.append(index)

    if name_matches:

        selected = name_matches[:n_results]

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
    # KEYWORD SEARCH
    # ========================================================

    stop_words = {
        "who", "has", "have", "had", "with",
        "experience", "experienced", "in", "on",
        "for", "and", "or", "the", "a", "an",
        "is", "are", "was", "were", "candidate",
        "candidates", "person", "people", "show",
        "find", "me", "looking", "look", "search",
        "please", "can", "you", "do", "does",
        "developer", "developers", "engineer",
        "engineers", "skill", "skills", "knowledge",
        "good", "strong", "relevant", "expert",
        "experts", "proficient", "proficiency",
        "using", "use", "used",
    }

    query_words = [
        word
        for word in normalized_query.split()
        if word not in stop_words
        and len(word) > 1
    ]

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

                matched_words.append(word)

        if matched_words:

            keyword_matches.append(
                {
                    "index": index,
                    "matched_count": len(
                        matched_words
                    ),
                    "matched_words": matched_words,
                }
            )

    keyword_matches.sort(
        key=lambda item: item["matched_count"],
        reverse=True,
    )

    if keyword_matches:

        selected = keyword_matches[:n_results]

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
    # SEMANTIC SEARCH
    # ========================================================

    try:

        semantic_results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )

        return semantic_results

    except Exception:

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
                    str(document or "").lower(),
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

        selected = scored[:n_results]

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
# CLEAR ALL
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