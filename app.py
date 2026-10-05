import streamlit as st
from datetime import datetime
import io
import json
import pandas as pd
import hashlib
import re
import base64
from pathlib import Path

from ui.styles import load_styles
from ui.components import (
    brand,
    sidebar_activity,
    log_activity,
)

from ui.dashboard import show_dashboard

from resume_parser import extract_resume_text

from skyhigh_agent import (
    run_skyhigh,
    ask_skyhigh_agent,
    generate_skyhigh_interview,
)

from rag_engine import (
    search_candidates,
    get_candidate_count,
    clear_all_candidates,
)

from report_generator import (
    create_report_pdf,
    create_report_text,
    create_report_json,
)


# ============================================================
# INITIAL SESSION STATE
# ============================================================

if "activity_log" not in st.session_state:
    st.session_state.activity_log = []


# ============================================================
# CONSTANTS
# ============================================================

MAX_BULK_RESUMES = 100

CHROMA_DIR = Path(__file__).resolve().parent / "chroma_db"

RAG_COLLECTION_NAME = "candidate_profiles"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _normalize_email(value):
    if not value:
        return ""

    return str(value).strip().lower()


def _normalize_phone(value):
    if not value:
        return ""

    digits = re.sub(r"\D", "", str(value))

    if len(digits) > 10:
        digits = digits[-10:]

    return digits


def _resume_hash(resume_bytes):
    return hashlib.sha256(resume_bytes).hexdigest()


def _extract_contact_from_resume(text):
    email_match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text or "",
    )

    email = _normalize_email(
        email_match.group(0)
        if email_match
        else ""
    )

    phone_matches = re.findall(
        r"(?:\+?\d[\d\s().-]{8,}\d)",
        text or "",
    )

    phone = ""

    for candidate in phone_matches:

        normalized = _normalize_phone(candidate)

        if len(normalized) >= 10:
            phone = normalized
            break

    return email, phone


def _get_rag_collection():

    try:

        import chromadb

        client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        return client.get_or_create_collection(
            name=RAG_COLLECTION_NAME
        )

    except Exception:

        return None


def _find_existing_candidate(
    email="",
    phone="",
    resume_hash="",
):

    collection = _get_rag_collection()

    if collection is None:
        return None

    try:

        stored = collection.get(
            include=["metadatas"]
        )

    except Exception:

        return None

    metadatas = stored.get("metadatas") or []
    ids = stored.get("ids") or []

    email = _normalize_email(email)
    phone = _normalize_phone(phone)

    for index, metadata in enumerate(metadatas):

        metadata = metadata or {}

        existing_email = _normalize_email(
            metadata.get("email", "")
        )

        existing_phone = _normalize_phone(
            metadata.get("phone", "")
        )

        existing_hash = str(
            metadata.get("resume_hash", "")
        ).strip()

        if (
            email
            and existing_email
            and email == existing_email
        ):

            return {
                "candidate_id": (
                    ids[index]
                    if index < len(ids)
                    else ""
                ),
                "reason": "same email",
                "metadata": metadata,
            }

        if (
            phone
            and existing_phone
            and phone == existing_phone
        ):

            return {
                "candidate_id": (
                    ids[index]
                    if index < len(ids)
                    else ""
                ),
                "reason": "same phone",
                "metadata": metadata,
            }

        if (
            resume_hash
            and existing_hash
            and resume_hash == existing_hash
        ):

            return {
                "candidate_id": (
                    ids[index]
                    if index < len(ids)
                    else ""
                ),
                "reason": "same resume",
                "metadata": metadata,
            }

    return None


def _save_identity_metadata(
    candidate_id,
    profile,
    resume_hash,
):

    if not candidate_id:
        return

    collection = _get_rag_collection()

    if collection is None:
        return

    try:

        current = collection.get(
            ids=[candidate_id],
            include=["metadatas"],
        )

        metadatas = current.get("metadatas") or []

        metadata = (
            dict(metadatas[0])
            if metadatas
            else {}
        )

        metadata["resume_hash"] = str(
            resume_hash
        )

        metadata["email"] = _normalize_email(
            profile.get("email", "")
        )

        metadata["phone"] = _normalize_phone(
            profile.get("phone", "")
        )

        collection.update(
            ids=[candidate_id],
            metadatas=[metadata],
        )

    except Exception:

        # Deduplication should never break screening.
        pass


def _get_robot_base64():

    robot_path = (
        Path(__file__).resolve().parent
        / "assets"
        / "skyhigh_robot.png"
    )

    if not robot_path.exists():
        return None

    try:

        image_bytes = robot_path.read_bytes()

        return base64.b64encode(
            image_bytes
        ).decode("utf-8")

    except Exception:

        return None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TalentSkillMate AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD STYLES
# ============================================================

load_styles()


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "resume_text": "",
    "candidate_analysis": None,
    "candidate_name": "No candidate",
    "candidate_id": None,
    "job_description": "",
    "last_match": None,
    "interview_questions": [],
    "chat_messages": [],
    "activity_log": [],
    "resume_count": 0,
    "match_count": 0,
    "report_count": 0,
    "workflow_complete": False,
    "bulk_results": [],
    "skyhigh_greeting_shown": False,
    "skyhigh_pending_question": None,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# QUERY PARAMETER NAVIGATION
# ============================================================

if "navigation" not in st.session_state:
    st.session_state.navigation = "Overview"


page_from_url = st.query_params.get(
    "page",
    "",
)


valid_pages = [
    "Overview",
    "Resume Screening",
    "RAG Intelligence",
    "Ask SkyHigh",
    "Skill Discovery",
    "Candidate Matching",
    "Interview Studio",
    "Recruiter Reports",
    "Settings",
]


if page_from_url in valid_pages:

    st.session_state.navigation = page_from_url

    st.query_params.clear()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    brand()

    st.markdown(
        '<div class="workspace-title">Workspace</div>',
        unsafe_allow_html=True,
    )

    menu = st.radio(
        "Navigation",
        valid_pages,
        key="navigation",
        label_visibility="collapsed",
    )

    sidebar_activity()


# ============================================================
# OVERVIEW
# ============================================================

if menu == "Overview":

    show_dashboard()


# ============================================================
# RESUME SCREENING
# ============================================================

elif menu == "Resume Screening":

    st.title("Resume Screening")

    st.write(
        "Upload one or multiple resumes and let "
        "TalentSkillMate AI analyze, compare, and rank "
        "candidates against the same job description."
    )

    st.markdown("---")


    # ========================================================
    # STEP 1 — JOB DESCRIPTION
    # ========================================================

    st.markdown(
        "### Step 1 — Job Description"
    )

    job_description = st.text_area(
        "Paste Job Description",
        value=st.session_state.get(
            "job_description",
            "",
        ),
        height=220,
        placeholder=(
            "Paste the complete job description here..."
        ),
        key="screening_job_description",
    )

    st.session_state.job_description = (
        job_description
    )


    # ========================================================
    # STEP 2 — UPLOAD RESUMES
    # ========================================================

    st.markdown(
        "### Step 2 — Upload Resume(s)"
    )

    st.caption(
        "Upload one or multiple PDF/DOCX resumes"
    )

    uploaded_resumes = st.file_uploader(
        "Upload Resume(s)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        key="resume_uploader",
        label_visibility="collapsed",
    )

    resume_limit_exceeded = bool(
        uploaded_resumes
        and len(uploaded_resumes)
        > MAX_BULK_RESUMES
    )


    if uploaded_resumes:

        if resume_limit_exceeded:

            st.error(
                f"Maximum {MAX_BULK_RESUMES} resumes "
                f"per screening. "
                f"You selected {len(uploaded_resumes)}."
            )

        else:

            st.success(
                f"✓ {len(uploaded_resumes)} resume(s) "
                "uploaded successfully. "
                "They will be compared and ranked automatically."
            )


    # ========================================================
    # ORIGINAL RESUME DOWNLOADS
    # ========================================================

    if (
        uploaded_resumes
        and not resume_limit_exceeded
    ):

        st.markdown(
            "### 📥 Download Uploaded Resumes"
        )

        st.caption(
            "Download the original resume files at any time."
        )

        for resume_index, resume_file in enumerate(
            uploaded_resumes,
            start=1,
        ):

            resume_name = resume_file.name

            resume_bytes = resume_file.getvalue()

            if resume_name.lower().endswith(".pdf"):

                resume_mime = "application/pdf"

            else:

                resume_mime = (
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                )

            download_left, download_right = (
                st.columns([4, 1])
            )

            with download_left:

                st.write(
                    f"📄 **{resume_index}. {resume_name}**"
                )

            with download_right:

                st.download_button(
                    "⬇ Download",
                    data=resume_bytes,
                    file_name=resume_name,
                    mime=resume_mime,
                    width="stretch",
                    key=(
                        f"download_original_resume_"
                        f"{resume_index}"
                    ),
                )


    # ========================================================
    # START SCREENING
    # ========================================================

    st.markdown("---")

    start_screening = st.button(
        "✦ START AI SCREENING WORKFLOW",
        type="primary",
        width="stretch",
        disabled=(
            not uploaded_resumes
            or resume_limit_exceeded
            or not job_description.strip()
        ),
        key="start_resume_screening",
    )


    if start_screening:

        results = []

        total_candidates = len(
            uploaded_resumes
        )

        progress_bar = st.progress(0)

        status_text = st.empty()

        batch_seen = {}


        # ====================================================
        # PROCESS EACH RESUME
        # ====================================================

        for index, uploaded_resume in enumerate(
            uploaded_resumes,
            start=1,
        ):

            status_text.info(
                f"Analyzing candidate "
                f"{index} of {total_candidates}: "
                f"{uploaded_resume.name}"
            )

            try:

                # --------------------------------------------
                # STEP 1 — EXTRACT RESUME
                # --------------------------------------------

                resume_text = extract_resume_text(
                    uploaded_resume
                )

                if not resume_text.strip():

                    raise ValueError(
                        "No readable text was found "
                        "in this resume."
                    )


                # --------------------------------------------
                # STEP 2 — DEDUPLICATION
                # --------------------------------------------

                resume_hash = _resume_hash(
                    uploaded_resume.getvalue()
                )

                resume_email, resume_phone = (
                    _extract_contact_from_resume(
                        resume_text
                    )
                )


                identity_keys = []

                if resume_email:

                    identity_keys.append(
                        (
                            "email",
                            resume_email,
                        )
                    )

                if resume_phone:

                    identity_keys.append(
                        (
                            "phone",
                            resume_phone,
                        )
                    )

                identity_keys.append(
                    (
                        "resume",
                        resume_hash,
                    )
                )


                duplicate = None


                # Check duplicates within this batch.

                for identity_key in identity_keys:

                    if identity_key in batch_seen:

                        duplicate = {
                            "candidate_id": (
                                batch_seen[
                                    identity_key
                                ]
                            ),
                            "reason": (
                                f"duplicate "
                                f"{identity_key[0]} "
                                "in this batch"
                            ),
                        }

                        break


                # Check existing RAG candidates.

                if duplicate is None:

                    duplicate = (
                        _find_existing_candidate(
                            email=resume_email,
                            phone=resume_phone,
                            resume_hash=resume_hash,
                        )
                    )


                if duplicate:

                    results.append(
                        {
                            "candidate_name": (
                                uploaded_resume.name
                            ),
                            "score": 0.0,
                            "status": (
                                "Duplicate — Skipped"
                            ),
                            "matching_skills": [],
                            "missing_skills": [],
                            "explanation": (
                                "Existing candidate "
                                "was not analyzed again: "
                                f"{duplicate.get('reason', 'duplicate identity')}"
                            ),
                            "candidate_id": (
                                duplicate.get(
                                    "candidate_id",
                                    "",
                                )
                            ),
                            "profile": {},
                            "match_report": {},
                            "resume_name": (
                                uploaded_resume.name
                            ),
                            "resume_bytes": (
                                uploaded_resume.getvalue()
                            ),
                        }
                    )

                    progress_bar.progress(
                        index / total_candidates
                    )

                    continue


                # --------------------------------------------
                # STEP 3 — SKYHIGH WORKFLOW
                # --------------------------------------------

                workflow = run_skyhigh(
                    resume_text=resume_text,
                    job_description=job_description,
                    store_candidate=True,
                )


                profile = (
                    workflow.get(
                        "candidate_profile",
                        {},
                    )
                    or {}
                )

                match_report = (
                    workflow.get(
                        "match_report",
                        {},
                    )
                    or {}
                )

                candidate_id = workflow.get(
                    "candidate_id",
                    "",
                )


                # --------------------------------------------
                # SAVE IDENTITY
                # --------------------------------------------

                _save_identity_metadata(
                    candidate_id,
                    profile,
                    resume_hash,
                )


                # --------------------------------------------
                # MARK BATCH SEEN
                # --------------------------------------------

                if resume_email:

                    batch_seen[
                        ("email", resume_email)
                    ] = candidate_id

                if resume_phone:

                    batch_seen[
                        ("phone", resume_phone)
                    ] = candidate_id

                batch_seen[
                    ("resume", resume_hash)
                ] = candidate_id


                # --------------------------------------------
                # CANDIDATE NAME
                # --------------------------------------------

                candidate_name = profile.get(
                    "candidate_name",
                    "Candidate",
                ) or uploaded_resume.name


                # --------------------------------------------
                # MATCH SCORE
                # --------------------------------------------

                try:

                    score = float(
                        match_report.get(
                            "overall_match_score",
                            0,
                        )
                    )

                except Exception:

                    score = 0.0


                # --------------------------------------------
                # MATCHING SKILLS
                # --------------------------------------------

                matching_skills = (
                    match_report.get(
                        "matching_skills",
                        [],
                    )
                )

                missing_skills = (
                    match_report.get(
                        "missing_skills",
                        [],
                    )
                )


                if not isinstance(
                    matching_skills,
                    list,
                ):

                    matching_skills = [
                        str(matching_skills)
                    ]


                if not isinstance(
                    missing_skills,
                    list,
                ):

                    missing_skills = [
                        str(missing_skills)
                    ]


                explanation = (
                    match_report.get(
                        "match_explanation",
                        "No explanation available.",
                    )
                )


                # --------------------------------------------
                # STORE RESULT
                # --------------------------------------------

                results.append(
                    {
                        "candidate_name": str(
                            candidate_name
                        ),
                        "score": score,
                        "status": "Analyzed",
                        "matching_skills": (
                            matching_skills
                        ),
                        "missing_skills": (
                            missing_skills
                        ),
                        "explanation": str(
                            explanation
                        ),
                        "candidate_id": (
                            candidate_id
                        ),
                        "profile": profile,
                        "match_report": (
                            match_report
                        ),
                        "resume_name": (
                            uploaded_resume.name
                        ),
                        "resume_bytes": (
                            uploaded_resume.getvalue()
                        ),
                        "resume_text": resume_text,
                    }
                )


            except Exception as error:

                results.append(
                    {
                        "candidate_name": (
                            uploaded_resume.name
                        ),
                        "score": 0.0,
                        "status": "Failed",
                        "matching_skills": [],
                        "missing_skills": [],
                        "explanation": str(error),
                        "profile": {},
                        "match_report": {},
                        "candidate_id": "",
                        "resume_name": (
                            uploaded_resume.name
                        ),
                        "resume_bytes": (
                            uploaded_resume.getvalue()
                        ),
                    }
                )


            progress_bar.progress(
                index / total_candidates
            )


        # ====================================================
        # RANK CANDIDATES
        # ====================================================

        results.sort(
            key=lambda item: item.get(
                "score",
                0,
            ),
            reverse=True,
        )


        rank = 1

        for result in results:

            if result.get("status") == "Analyzed":

                result["rank"] = rank

                rank += 1

            else:

                result["rank"] = None


        # ====================================================
        # SAVE RESULTS
        # ====================================================

        st.session_state.bulk_results = results

        st.session_state.job_description = (
            job_description
        )


        analyzed_results = [
            item
            for item in results
            if item.get("status") == "Analyzed"
        ]


        # ====================================================
        # TOP CANDIDATE CONTEXT
        # ====================================================

        if analyzed_results:

            top_result = analyzed_results[0]

            top_profile = (
                top_result.get(
                    "profile",
                    {},
                )
                or {}
            )


            st.session_state.resume_text = (
                top_result.get(
                    "resume_text",
                    "",
                )
            )

            st.session_state.candidate_analysis = (
                top_profile
            )

            st.session_state.candidate_name = (
                top_profile.get(
                    "candidate_name",
                    top_result.get(
                        "candidate_name",
                        "Candidate",
                    ),
                )
            )

            st.session_state.candidate_id = (
                top_result.get(
                    "candidate_id"
                )
            )

            st.session_state.last_match = (
                top_result.get(
                    "match_report",
                    {},
                )
            )

            st.session_state.workflow_complete = (
                True
            )


            st.session_state.resume_count += (
                len(analyzed_results)
            )

            st.session_state.match_count += sum(
                1
                for item in analyzed_results
                if item.get("match_report")
            )


        # ====================================================
        # ACTIVITY LOG
        # ====================================================

        log_activity(
            "Resume Screening",
            (
                f"{len(analyzed_results)} analyzed; "
                f"{sum(1 for item in results if item.get('status') == 'Duplicate — Skipped')} duplicates; "
                f"{sum(1 for item in results if item.get('status') == 'Failed')} failed"
            ),
            "📄",
        )


        status_text.success(
            "AI resume screening completed successfully."
        )


        st.success(
            f"{len(analyzed_results)} candidate(s) "
            "analyzed and ranked. "
            f"{sum(1 for item in results if item.get('status') == 'Duplicate — Skipped')} "
            "duplicate(s) skipped."
        )


    # ========================================================
    # SCREENING RESULTS
    # ========================================================

    if st.session_state.get("bulk_results"):

        results = st.session_state.bulk_results

        st.markdown("---")

        st.subheader(
            "Recruiter Candidate Ranking"
        )

        st.write(
            "Candidates are ranked according to "
            "their AI-generated job-match score."
        )


        ranking_rows = []


        for result in results:

            ranking_rows.append(
                {
                    "Rank": result.get(
                        "rank"
                    ),
                    "Candidate": result.get(
                        "candidate_name",
                        "Candidate",
                    ),
                    "Match Score": (
                        f"{float(result.get('score', 0)):.1f}%"
                    ),
                    "Status": result.get(
                        "status",
                        "Unknown",
                    ),
                }
            )


        st.dataframe(
            ranking_rows,
            width="stretch",
            hide_index=True,
        )


        # ====================================================
        # METRICS
        # ====================================================

        analyzed_scores = [
            float(item.get("score", 0))
            for item in results
            if item.get("status") == "Analyzed"
        ]


        average_score = (
            sum(analyzed_scores)
            / len(analyzed_scores)
            if analyzed_scores
            else 0
        )


        highest_score = (
            max(analyzed_scores)
            if analyzed_scores
            else 0
        )


        metric1, metric2, metric3 = (
            st.columns(3)
        )


        with metric1:

            st.metric(
                "Candidates",
                len(results),
            )


        with metric2:

            st.metric(
                "Average Match",
                f"{average_score:.1f}%",
            )


        with metric3:

            st.metric(
                "Highest Match",
                f"{highest_score:.1f}%",
            )


        # ====================================================
        # CANDIDATE DETAILS
        # ====================================================

        st.markdown("---")

        st.subheader(
            "Candidate Details"
        )


        for result_index, result in enumerate(
            results
        ):

            rank_value = result.get(
                "rank"
            )

            display_rank = (
                rank_value
                if rank_value is not None
                else "—"
            )

            candidate_name = result.get(
                "candidate_name",
                "Candidate",
            )

            score = float(
                result.get(
                    "score",
                    0,
                )
            )

            status = result.get(
                "status",
                "Unknown",
            )


            with st.expander(
                f"#{display_rank}  "
                f"{candidate_name}  —  "
                f"{score:.1f}% Match"
            ):

                st.caption(
                    f"Status: {status}"
                )


                # ----------------------------------------
                # ORIGINAL RESUME DOWNLOAD
                # ----------------------------------------

                if result.get("resume_name"):

                    st.download_button(
                        "⬇ Download Original Resume",
                        data=result.get(
                            "resume_bytes",
                            b"",
                        ),
                        file_name=result.get(
                            "resume_name"
                        ),
                        mime=(
                            "application/pdf"
                            if str(
                                result.get(
                                    "resume_name",
                                    "",
                                )
                            ).lower().endswith(".pdf")
                            else
                            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        ),
                        width="content",
                        key=(
                            f"download_result_resume_"
                            f"{result_index}"
                        ),
                    )


                detail_left, detail_right = (
                    st.columns(2)
                )


                # ----------------------------------------
                # MATCHING SKILLS
                # ----------------------------------------

                with detail_left:

                    st.markdown(
                        "#### Matching Skills"
                    )

                    matching_skills = (
                        result.get(
                            "matching_skills",
                            [],
                        )
                    )


                    if matching_skills:

                        for skill in matching_skills:

                            st.success(
                                f"✓ {skill}"
                            )

                    else:

                        st.info(
                            "No matching skills identified."
                        )


                # ----------------------------------------
                # MISSING SKILLS
                # ----------------------------------------

                with detail_right:

                    st.markdown(
                        "#### Missing Skills"
                    )

                    missing_skills = (
                        result.get(
                            "missing_skills",
                            [],
                        )
                    )


                    if missing_skills:

                        for skill in missing_skills:

                            st.warning(
                                f"• {skill}"
                            )

                    else:

                        st.success(
                            "No missing skills identified."
                        )


                # ----------------------------------------
                # EXPLANATION
                # ----------------------------------------

                st.markdown(
                    "#### Match Explanation"
                )

                st.info(
                    result.get(
                        "explanation",
                        "No explanation available.",
                    )
                )


                # ----------------------------------------
                # PROFILE
                # ----------------------------------------

                profile = (
                    result.get(
                        "profile"
                    )
                    or {}
                )


                if profile:

                    st.markdown(
                        "#### Candidate Overview"
                    )


                    overview_left, overview_right = (
                        st.columns(2)
                    )


                    with overview_left:

                        st.write(
                            f"**Name:** "
                            f"{profile.get('candidate_name', '—')}"
                        )

                        st.write(
                            f"**Email:** "
                            f"{profile.get('email', '—')}"
                        )

                        st.write(
                            f"**Phone:** "
                            f"{profile.get('phone', '—')}"
                        )


                    with overview_right:

                        st.write(
                            f"**Location:** "
                            f"{profile.get('location', '—')}"
                        )


                        languages = profile.get(
                            "languages",
                            [],
                        )


                        if isinstance(
                            languages,
                            list,
                        ):

                            languages = ", ".join(
                                str(x)
                                for x in languages
                            )


                        st.write(
                            f"**Languages:** "
                            f"{languages or '—'}"
                        )


                    # ------------------------------------
                    # SUMMARY
                    # ------------------------------------

                    if profile.get(
                        "professional_summary"
                    ):

                        st.markdown(
                            "#### Professional Summary"
                        )

                        st.info(
                            profile.get(
                                "professional_summary"
                            )
                        )


                    # ------------------------------------
                    # SKILLS
                    # ------------------------------------

                    skills = profile.get(
                        "skills",
                        [],
                    )


                    st.markdown(
                        "#### Detected Skills"
                    )


                    if skills:

                        skill_columns = st.columns(
                            min(
                                4,
                                len(skills),
                            )
                        )


                        for skill_index, skill in enumerate(
                            skills
                        ):

                            with skill_columns[
                                skill_index
                                % len(skill_columns)
                            ]:

                                st.success(
                                    str(skill)
                                )

                    else:

                        st.info(
                            "No explicit skills found."
                        )


                    # ------------------------------------
                    # EXPERIENCE
                    # ------------------------------------

                    experiences = profile.get(
                        "work_experience",
                        [],
                    )


                    st.markdown(
                        "#### Work Experience"
                    )


                    if experiences:

                        for experience in experiences:

                            with st.expander(
                                experience.get(
                                    "job_title",
                                    "Experience",
                                )
                            ):

                                st.write(
                                    f"**Company:** "
                                    f"{experience.get('company', '—')}"
                                )

                                st.write(
                                    f"**Duration:** "
                                    f"{experience.get('duration', '—')}"
                                )


                                responsibilities = (
                                    experience.get(
                                        "responsibilities",
                                        [],
                                    )
                                )


                                if responsibilities:

                                    for responsibility in (
                                        responsibilities
                                    ):

                                        st.write(
                                            f"• {responsibility}"
                                        )

                    else:

                        st.info(
                            "No work experience "
                            "explicitly found."
                        )


                    # ------------------------------------
                    # EDUCATION
                    # ------------------------------------

                    education_list = profile.get(
                        "education",
                        [],
                    )


                    st.markdown(
                        "#### Education"
                    )


                    if education_list:

                        for education in education_list:

                            st.write(
                                f"**{education.get('degree', '')}**"
                            )

                            st.write(
                                f"{education.get('institution', '')} "
                                f"{education.get('year', '')}"
                            )

                    else:

                        st.info(
                            "No education information found."
                        )


                    # ------------------------------------
                    # PROJECTS
                    # ------------------------------------

                    projects = profile.get(
                        "projects",
                        [],
                    )


                    st.markdown(
                        "#### Projects"
                    )


                    if projects:

                        for project in projects:

                            with st.expander(
                                project.get(
                                    "project_name",
                                    "Project",
                                )
                            ):

                                st.write(
                                    project.get(
                                        "description",
                                        "",
                                    )
                                )


                                technologies = (
                                    project.get(
                                        "technologies",
                                        [],
                                    )
                                )


                                if technologies:

                                    st.write(
                                        "**Technologies:** "
                                        + ", ".join(
                                            str(item)
                                            for item in technologies
                                        )
                                    )

                    else:

                        st.info(
                            "No projects explicitly found."
                        )


        # ====================================================
        # RECRUITER EXPORT
        # ====================================================

        st.markdown("---")

        st.subheader(
            "Recruiter Ranking Export"
        )

        st.caption(
            "Download the analyzed candidate ranking "
            "in your preferred format."
        )


        export_rows = []


        for result in results:

            matching_skills = result.get(
                "matching_skills",
                [],
            )

            missing_skills = result.get(
                "missing_skills",
                [],
            )


            matching_skills_text = (
                ", ".join(
                    str(skill)
                    for skill in matching_skills
                )
                if isinstance(
                    matching_skills,
                    list,
                )
                else str(
                    matching_skills
                )
            )


            missing_skills_text = (
                ", ".join(
                    str(skill)
                    for skill in missing_skills
                )
                if isinstance(
                    missing_skills,
                    list,
                )
                else str(
                    missing_skills
                )
            )


            export_rows.append(
                {
                    "Rank": result.get(
                        "rank"
                    ),
                    "Candidate": result.get(
                        "candidate_name",
                        "Candidate",
                    ),
                    "Match Score": round(
                        float(
                            result.get(
                                "score",
                                0,
                            )
                        ),
                        1,
                    ),
                    "Status": result.get(
                        "status",
                        "Unknown",
                    ),
                    "Matching Skills": (
                        matching_skills_text
                    ),
                    "Missing Skills": (
                        missing_skills_text
                    ),
                    "Match Explanation": (
                        result.get(
                            "explanation",
                            "",
                        )
                    ),
                }
            )


        export_df = pd.DataFrame(
            export_rows
        )


        col_csv, col_excel, col_json, col_pdf = (
            st.columns(4)
        )


        # ====================================================
        # CSV
        # ====================================================

        with col_csv:

            csv_data = export_df.to_csv(
                index=False
            )

            st.download_button(
                label="⬇ CSV",
                data=csv_data,
                file_name=(
                    "TalentSkillMate_Bulk_Ranking.csv"
                ),
                mime="text/csv",
                width="stretch",
            )


        # ====================================================
        # EXCEL
        # ====================================================

        with col_excel:

            excel_buffer = io.BytesIO()


            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl",
            ) as writer:

                export_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Candidate Ranking",
                )


            excel_buffer.seek(0)


            st.download_button(
                label="⬇ Excel",
                data=excel_buffer.getvalue(),
                file_name=(
                    "TalentSkillMate_Bulk_Ranking.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                width="stretch",
            )


        # ====================================================
        # JSON
        # ====================================================

        with col_json:

            json_data = json.dumps(
                export_rows,
                indent=4,
                ensure_ascii=False,
            )


            st.download_button(
                label="⬇ JSON",
                data=json_data,
                file_name=(
                    "TalentSkillMate_Bulk_Ranking.json"
                ),
                mime="application/json",
                width="stretch",
            )


        # ====================================================
        # PDF
        # ====================================================

        with col_pdf:

            try:

                from reportlab.lib import colors

                from reportlab.lib.enums import (
                    TA_CENTER,
                )

                from reportlab.lib.pagesizes import A4

                from reportlab.lib.styles import (
                    getSampleStyleSheet,
                    ParagraphStyle,
                )

                from reportlab.lib.units import mm

                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Paragraph,
                    Spacer,
                    Table,
                    TableStyle,
                )


                pdf_buffer = io.BytesIO()


                doc = SimpleDocTemplate(
                    pdf_buffer,
                    pagesize=A4,
                    rightMargin=15 * mm,
                    leftMargin=15 * mm,
                    topMargin=15 * mm,
                    bottomMargin=15 * mm,
                )


                styles = getSampleStyleSheet()


                title_style = ParagraphStyle(
                    "TalentSkillMateTitle",
                    parent=styles["Title"],
                    alignment=TA_CENTER,
                    fontSize=18,
                    leading=22,
                    spaceAfter=8,
                )


                subtitle_style = ParagraphStyle(
                    "TalentSkillMateSubtitle",
                    parent=styles["Normal"],
                    alignment=TA_CENTER,
                    fontSize=9,
                    leading=12,
                    spaceAfter=15,
                )


                small_style = ParagraphStyle(
                    "TalentSkillMateSmall",
                    parent=styles["Normal"],
                    fontSize=8,
                    leading=10,
                )


                story = [
                    Paragraph(
                        "TalentSkillMate AI — Candidate Ranking",
                        title_style,
                    ),
                    Paragraph(
                        "AI-generated recommendation "
                        "for recruiter review",
                        subtitle_style,
                    ),
                ]


                table_data = [
                    [
                        Paragraph(
                            "Rank",
                            small_style,
                        ),
                        Paragraph(
                            "Candidate",
                            small_style,
                        ),
                        Paragraph(
                            "Score",
                            small_style,
                        ),
                        Paragraph(
                            "Status",
                            small_style,
                        ),
                    ]
                ]


                for row in export_rows:

                    rank_text = (
                        str(row["Rank"])
                        if row["Rank"] is not None
                        else "—"
                    )


                    table_data.append(
                        [
                            Paragraph(
                                rank_text,
                                small_style,
                            ),
                            Paragraph(
                                str(
                                    row["Candidate"]
                                ),
                                small_style,
                            ),
                            Paragraph(
                                f"{row['Match Score']:.1f}%",
                                small_style,
                            ),
                            Paragraph(
                                str(
                                    row["Status"]
                                ),
                                small_style,
                            ),
                        ]
                    )


                table = Table(
                    table_data,
                    colWidths=[
                        25 * mm,
                        75 * mm,
                        30 * mm,
                        45 * mm,
                    ],
                    repeatRows=1,
                )


                table.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, 0),
                                colors.HexColor(
                                    "#EAF1FF"
                                ),
                            ),
                            (
                                "TEXTCOLOR",
                                (0, 0),
                                (-1, 0),
                                colors.HexColor(
                                    "#16315C"
                                ),
                            ),
                            (
                                "GRID",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                colors.HexColor(
                                    "#D5DCE8"
                                ),
                            ),
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP",
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                6,
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                6,
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                6,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                6,
                            ),
                        ]
                    )
                )


                story.append(table)

                story.append(
                    Spacer(
                        1,
                        10,
                    )
                )


                for row in export_rows:

                    explanation = (
                        row.get(
                            "Match Explanation",
                            "",
                        )
                        or "Not available"
                    )


                    story.append(
                        Paragraph(
                            (
                                f"<b>{row['Candidate']}</b> — "
                                f"{row['Match Score']:.1f}%<br/>"
                                f"<b>Match Explanation:</b> "
                                f"{explanation}"
                            ),
                            small_style,
                        )
                    )


                    story.append(
                        Spacer(
                            1,
                            8,
                        )
                    )


                story.append(
                    Paragraph(
                        (
                            "<b>Disclaimer:</b> "
                            "AI-generated candidate ranking "
                            "is intended to support recruiter "
                            "review. It is not a hiring decision "
                            "and should not be used as the sole "
                            "basis for employment decisions."
                        ),
                        small_style,
                    )
                )


                doc.build(story)

                pdf_buffer.seek(0)


                st.download_button(
                    label="⬇ PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=(
                        "TalentSkillMate_Bulk_Ranking.pdf"
                    ),
                    mime="application/pdf",
                    width="stretch",
                )


            except ImportError:

                st.warning(
                    "PDF export requires the reportlab package."
                )

                st.caption(
                    "Run: pip install reportlab"
                )


        # ====================================================
        # DISCLAIMER
        # ====================================================

        st.info(
            "AI-generated candidate ranking is intended "
            "to support recruiter review. It is not a "
            "hiring decision and should not be used as "
            "the sole basis for employment decisions."
        )


# ============================================================
# RAG INTELLIGENCE
# ============================================================

elif menu == "RAG Intelligence":

    st.title(
        "RAG Intelligence"
    )

    st.write(
        "Search the candidate knowledge base "
        "using recruiter questions."
    )


    count = get_candidate_count()


    st.metric(
        "Candidates Stored",
        count,
    )


    query = st.text_input(
        "Search candidate intelligence",
        placeholder=(
            "Example: Python developers "
            "with automation experience"
        ),
    )


    if st.button(
        "🔎 Search Candidate Knowledge",
        type="primary",
    ):

        if not query.strip():

            st.warning(
                "Enter a search query."
            )

        else:

            with st.spinner(
                "Searching candidate intelligence..."
            ):

                results = search_candidates(
                    query,
                    n_results=5,
                )


            documents = results.get(
                "documents",
                [],
            )

            metadatas = results.get(
                "metadatas",
                [],
            )


            if documents:

                if isinstance(
                    documents[0],
                    list,
                ):

                    documents = documents[0]


                if (
                    metadatas
                    and isinstance(
                        metadatas[0],
                        list,
                    )
                ):

                    metadatas = metadatas[0]


                for index, document in enumerate(
                    documents
                ):

                    metadata = (
                        metadatas[index]
                        if index < len(metadatas)
                        else {}
                    )


                    name = metadata.get(
                        "candidate_name",
                        "Candidate",
                    )


                    with st.expander(
                        f"👤 {name}"
                    ):

                        st.write(
                            document
                        )


            else:

                st.info(
                    "No candidates found."
                )


# ============================================================
# ASK SKYHIGH
# ============================================================

elif menu == "Ask SkyHigh":

    st.title(
        "Ask SkyHigh"
    )


    # ========================================================
    # INITIALIZE SKYHIGH STATE
    # ========================================================

    if (
        "skyhigh_greeting_shown"
        not in st.session_state
    ):

        st.session_state.skyhigh_greeting_shown = (
            False
        )


    if (
        "skyhigh_pending_question"
        not in st.session_state
    ):

        st.session_state.skyhigh_pending_question = (
            None
        )


    # ========================================================
    # FIRST ENTRY WELCOME
    # ========================================================

    if not st.session_state.skyhigh_greeting_shown:

        robot_b64 = _get_robot_base64()


        # ====================================================
        # SKYHIGH WELCOME CSS
        # ====================================================

        st.markdown(
            """
            <style>

            .skyhigh-welcome {
                width: 100%;
                text-align: center;
                padding: 20px 15px 10px 15px;
                box-sizing: border-box;
                overflow: hidden;
            }


            /* ----------------------------------------------
               ROBOT CONTAINER
               ---------------------------------------------- */

            .skyhigh-robot-container {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                min-height: 210px;
                margin: 0 auto 8px auto;
            }


            /* ----------------------------------------------
               ROBOT IMAGE
               ---------------------------------------------- */

            .skyhigh-robot {
                width: 180px;
                height: 180px;
                object-fit: contain;
                display: block;
                animation:
                    skyhighFloat 3s ease-in-out infinite,
                    skyhighAppear 0.9s ease-out both;
                transform-origin: center center;
                will-change: transform, opacity;
            }


            /* ----------------------------------------------
               FLOATING ANIMATION
               ---------------------------------------------- */

            @keyframes skyhighFloat {

                0% {
                    transform:
                        translateY(0px)
                        rotate(-1deg);
                }

                25% {
                    transform:
                        translateY(-7px)
                        rotate(0deg);
                }

                50% {
                    transform:
                        translateY(-16px)
                        rotate(1deg);
                }

                75% {
                    transform:
                        translateY(-7px)
                        rotate(0deg);
                }

                100% {
                    transform:
                        translateY(0px)
                        rotate(-1deg);
                }

            }


            /* ----------------------------------------------
               APPEAR ANIMATION
               ---------------------------------------------- */

            @keyframes skyhighAppear {

                0% {
                    opacity: 0;
                    transform:
                        scale(0.65)
                        translateY(25px);
                }

                60% {
                    opacity: 1;
                    transform:
                        scale(1.06)
                        translateY(-4px);
                }

                100% {
                    opacity: 1;
                    transform:
                        scale(1)
                        translateY(0px);
                }

            }


            /* ----------------------------------------------
               TITLE
               ---------------------------------------------- */

            .skyhigh-title {
                text-align: center;
                font-size: clamp(
                    26px,
                    3vw,
                    36px
                );
                line-height: 1.2;
                font-weight: 800;
                margin: 8px auto 0 auto;
            }


            /* ----------------------------------------------
               DESCRIPTION
               ---------------------------------------------- */

            .skyhigh-description {
                width: 100%;
                max-width: 720px;
                margin: 10px auto 0 auto;
                text-align: center;
                font-size: clamp(
                    14px,
                    1.4vw,
                    16px
                );
                line-height: 1.6;
                opacity: 0.78;
                padding: 0 10px;
                box-sizing: border-box;
            }


            /* ----------------------------------------------
               BUBBLE
               ---------------------------------------------- */

            .skyhigh-bubble {
                display: block;
                width: fit-content;
                max-width: calc(100% - 30px);
                margin: 16px auto 4px auto;
                padding: 10px 20px;
                border-radius: 24px;
                text-align: center;
                font-weight: 600;
                box-sizing: border-box;
            }


            /* ----------------------------------------------
               MOBILE
               ---------------------------------------------- */

            @media (max-width: 600px) {

                .skyhigh-welcome {
                    padding:
                        12px 8px 8px 8px;
                }


                .skyhigh-robot-container {
                    min-height: 180px;
                }


                .skyhigh-robot {
                    width: 150px;
                    height: 150px;
                }


                .skyhigh-title {
                    font-size: 25px;
                }


                .skyhigh-description {
                    font-size: 14px;
                    line-height: 1.5;
                    padding: 0 5px;
                }


                .skyhigh-bubble {
                    font-size: 14px;
                    padding: 9px 15px;
                    margin-top: 12px;
                }

            }


            @media (max-width: 380px) {

                .skyhigh-robot {
                    width: 135px;
                    height: 135px;
                }


                .skyhigh-title {
                    font-size: 22px;
                }


                .skyhigh-description {
                    font-size: 13px;
                }

            }

            </style>
            """,
            unsafe_allow_html=True,
        )


        # ====================================================
        # WELCOME CONTAINER
        # ====================================================

        st.markdown(
            '<div class="skyhigh-welcome">',
            unsafe_allow_html=True,
        )


        # ====================================================
        # ROBOT
        # ====================================================

        if robot_b64:

            st.markdown(
                f"""
                <div class="skyhigh-robot-container">
                    <img
                        class="skyhigh-robot"
                        src="data:image/png;base64,{robot_b64}"
                        alt="SkyHigh AI"
                    >
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="skyhigh-robot-container">
                    <div
                        class="skyhigh-robot"
                        style="
                            font-size:100px;
                            text-align:center;
                            line-height:1;
                        "
                    >
                        🤖
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


        # ====================================================
        # GREETING TITLE
        # ====================================================

        st.markdown(
            """
            <div class="skyhigh-title">
                Hi! I'm SkyHigh AI 👋
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ====================================================
        # DESCRIPTION
        # ====================================================

        st.markdown(
            """
            <div class="skyhigh-description">
                Your intelligent recruitment assistant.<br>
                I can help you analyze candidates,
                discover hidden skills,
                compare resumes,
                understand matching results,
                and prepare interview questions.
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ====================================================
        # WELCOME BUBBLE
        # ====================================================

        st.markdown(
            """
            <div class="skyhigh-bubble">
                ✨ What would you like to know?
            </div>
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


        # ====================================================
        # SUGGESTED QUESTIONS
        # ====================================================

        st.markdown(
            "### 💡 Try asking SkyHigh"
        )


        q1, q2 = st.columns(2)


        with q1:

            if st.button(
                "🏆 Who is the best-matched candidate?",
                width="stretch",
                key="skyhigh_suggest_1",
            ):

                st.session_state.skyhigh_pending_question = (
                    "Who is the best-matched candidate?"
                )

                st.session_state.skyhigh_greeting_shown = (
                    True
                )

                st.rerun()


        with q2:

            if st.button(
                "🔍 What skills are missing?",
                width="stretch",
                key="skyhigh_suggest_2",
            ):

                st.session_state.skyhigh_pending_question = (
                    "What skills are missing?"
                )

                st.session_state.skyhigh_greeting_shown = (
                    True
                )

                st.rerun()


        q3, q4 = st.columns(2)


        with q3:

            if st.button(
                "👥 Compare the top candidates",
                width="stretch",
                key="skyhigh_suggest_3",
            ):

                st.session_state.skyhigh_pending_question = (
                    "Compare the top candidates."
                )

                st.session_state.skyhigh_greeting_shown = (
                    True
                )

                st.rerun()


        with q4:

            if st.button(
                "🎯 Generate interview questions",
                width="stretch",
                key="skyhigh_suggest_4",
            ):

                st.session_state.skyhigh_pending_question = (
                    "Generate interview questions."
                )

                st.session_state.skyhigh_greeting_shown = (
                    True
                )

                st.rerun()


        # ====================================================
        # START CHAT
        # ====================================================

        if st.button(
            "💬 Start Chatting with SkyHigh",
            type="primary",
            width="stretch",
            key="skyhigh_start_chat",
        ):

            st.session_state.skyhigh_greeting_shown = (
                True
            )

            st.rerun()


    # ========================================================
    # CURRENT CANDIDATE CONTEXT
    # ========================================================

    if st.session_state.candidate_analysis:

        st.info(
            "Current candidate: "
            f"**{st.session_state.candidate_name}**"
        )


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    for message in (
        st.session_state.chat_messages
    ):

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    question = (
        st.session_state.skyhigh_pending_question
    )


    if question:

        st.session_state.skyhigh_pending_question = (
            None
        )

    else:

        question = st.chat_input(
            "Ask SkyHigh about candidates..."
        )


    # ========================================================
    # PROCESS QUESTION
    # ========================================================

    if question:

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": question,
            }
        )


        with st.chat_message("user"):

            st.markdown(
                question
            )


        with st.chat_message("assistant"):

            with st.spinner(
                "SkyHigh is thinking..."
            ):

                try:

                    answer = ask_skyhigh_agent(
                        question=question,
                        candidate_profile=(
                            st.session_state.candidate_analysis
                        ),
                        resume_text=(
                            st.session_state.resume_text
                        ),
                    )


                    st.markdown(
                        answer
                    )


                    st.session_state.chat_messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )


                except Exception as error:

                    st.error(
                        f"SkyHigh error: {error}"
                    )


    # ========================================================
    # CLEAR CHAT
    # ========================================================

    if st.session_state.chat_messages:

        st.markdown("---")


        if st.button(
            "🗑️ Clear Chat",
            width="content",
            key="clear_skyhigh_chat",
        ):

            st.session_state.chat_messages = []

            st.session_state.skyhigh_greeting_shown = (
                False
            )

            st.session_state.skyhigh_pending_question = (
                None
            )

            st.rerun()


# ============================================================
# SKILL DISCOVERY
# ============================================================

elif menu == "Skill Discovery":

    st.title(
        "Skill Discovery"
    )


    if not st.session_state.candidate_analysis:

        st.info(
            "Analyze a resume first."
        )

    else:

        profile = (
            st.session_state.candidate_analysis
        )


        st.subheader(
            "Explicit Skills"
        )


        for skill in profile.get(
            "skills",
            [],
        ):

            st.success(
                f"✓ {skill}"
            )


        st.subheader(
            "Projects and Evidence"
        )


        for project in profile.get(
            "projects",
            [],
        ):

            st.write(
                f"**{project.get('project_name', 'Project')}**"
            )


            st.write(
                project.get(
                    "description",
                    "",
                )
            )


# ============================================================
# CANDIDATE MATCHING
# ============================================================

elif menu == "Candidate Matching":

    st.title(
        "Candidate Matching"
    )


    if not st.session_state.candidate_analysis:

        st.info(
            "Please analyze a resume first."
        )

    else:

        job_description = st.text_area(
            "Job Description",
            value=st.session_state.get(
                "job_description",
                "",
            ),
            height=240,
        )


        if st.button(
            "🎯 Run Candidate Matching",
            type="primary",
            width="stretch",
        ):

            if not job_description.strip():

                st.warning(
                    "Please enter a job description."
                )

            else:

                from llm_engine import (
                    match_resume_to_job,
                )


                with st.spinner(
                    "Calculating candidate-job alignment..."
                ):

                    try:

                        match = match_resume_to_job(
                            st.session_state.candidate_analysis,
                            job_description,
                        )


                        st.session_state.last_match = (
                            match
                        )


                        st.session_state.job_description = (
                            job_description
                        )


                        st.session_state.match_count += (
                            1
                        )


                    except Exception as error:

                        st.error(
                            f"Matching failed: {error}"
                        )


        if st.session_state.last_match:

            match = (
                st.session_state.last_match
            )


            st.markdown("---")


            c1, c2, c3, c4 = st.columns(4)


            with c1:

                st.metric(
                    "Overall",
                    f"{match.get('overall_match_score', 0)}%",
                )


            with c2:

                st.metric(
                    "Skills",
                    f"{match.get('skill_match_score', 0)}%",
                )


            with c3:

                st.metric(
                    "Experience",
                    f"{match.get('experience_match_score', 0)}%",
                )


            with c4:

                st.metric(
                    "Education",
                    f"{match.get('education_match_score', 0)}%",
                )


            st.subheader(
                "Matching Skills"
            )


            for skill in match.get(
                "matching_skills",
                [],
            ):

                st.success(
                    f"✓ {skill}"
                )


            st.subheader(
                "Missing Skills"
            )


            for skill in match.get(
                "missing_skills",
                [],
            ):

                st.warning(
                    f"• {skill}"
                )


            st.subheader(
                "Explanation"
            )


            st.info(
                match.get(
                    "match_explanation",
                    "",
                )
            )


# ============================================================
# INTERVIEW STUDIO
# ============================================================

elif menu == "Interview Studio":

    st.title(
        "Interview Studio"
    )


    if not st.session_state.candidate_analysis:

        st.info(
            "Analyze a resume first."
        )

    else:

        interview_type = st.selectbox(
            "Interview Type",
            [
                "Technical Interview",
                "Behavioral Interview",
                "HR Interview",
                "Project Interview",
                "Mixed Interview",
            ],
        )


        number_of_questions = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=15,
            value=6,
        )


        job_description = st.text_area(
            "Job Description",
            value=st.session_state.get(
                "job_description",
                "",
            ),
            height=180,
        )


        if st.button(
            "🎤 Generate Interview Questions",
            type="primary",
            width="stretch",
        ):

            with st.spinner(
                "SkyHigh is preparing interview questions..."
            ):

                try:

                    questions = (
                        generate_skyhigh_interview(
                            candidate_profile=(
                                st.session_state.candidate_analysis
                            ),
                            job_description=(
                                job_description
                            ),
                            interview_type=(
                                interview_type
                            ),
                            number_of_questions=(
                                number_of_questions
                            ),
                        )
                    )


                    st.session_state.interview_questions = (
                        questions
                    )


                except Exception as error:

                    st.error(
                        f"Interview generation failed: {error}"
                    )


        if st.session_state.interview_questions:

            st.markdown("---")


            st.subheader(
                "Generated Interview Questions"
            )


            for index, item in enumerate(
                st.session_state.interview_questions,
                start=1,
            ):

                question = item.get(
                    "question",
                    "",
                )


                category = item.get(
                    "category",
                    "General",
                )


                reason = item.get(
                    "reason",
                    "",
                )


                with st.expander(
                    f"Question {index} — {category}"
                ):

                    st.write(
                        question
                    )


                    if reason:

                        st.caption(
                            f"Why this question: {reason}"
                        )


# ============================================================
# RECRUITER REPORTS
# ============================================================

elif menu == "Recruiter Reports":

    st.title(
        "Recruiter Reports"
    )


    if not st.session_state.candidate_analysis:

        st.info(
            "Analyze a resume first."
        )

    else:

        profile = (
            st.session_state.candidate_analysis
        )


        match = (
            st.session_state.last_match
        )


        st.subheader(
            "Report Preview"
        )


        st.write(
            f"**Candidate:** "
            f"{profile.get('candidate_name', 'Candidate')}"
        )


        st.write(
            profile.get(
                "professional_summary",
                "",
            )
        )


        if match:

            st.metric(
                "Overall Match",
                f"{match.get('overall_match_score', 0)}%",
            )


        st.markdown("---")


        pdf_data = create_report_pdf(
            profile,
            match,
        )


        text_data = create_report_text(
            profile,
            match,
        )


        json_data = create_report_json(
            profile,
            match,
        )


        candidate_name = (
            profile.get(
                "candidate_name",
                "candidate",
            )
            .replace(
                " ",
                "_",
            )
            .replace(
                "/",
                "_",
            )
        )


        st.download_button(
            "⬇ Download Professional PDF Report",
            data=pdf_data,
            file_name=(
                f"{candidate_name}_"
                "TalentSkillMate_Report.pdf"
            ),
            mime="application/pdf",
            type="primary",
            width="stretch",
        )


        st.download_button(
            "⬇ Download Text Report",
            data=text_data,
            file_name=(
                f"{candidate_name}_"
                "TalentSkillMate_Report.txt"
            ),
            mime="text/plain",
            width="stretch",
        )


        st.download_button(
            "⬇ Download JSON Data",
            data=json_data,
            file_name=(
                f"{candidate_name}_"
                "TalentSkillMate_Data.json"
            ),
            mime="application/json",
            width="stretch",
        )


# ============================================================
# SETTINGS
# ============================================================

elif menu == "Settings":

    st.title(
        "Settings"
    )


    st.checkbox(
        "Enable SkyHigh AI",
        value=True,
    )


    st.checkbox(
        "Enable RAG Intelligence",
        value=True,
    )


    st.checkbox(
        "Enable recruiter insights",
        value=True,
    )


    st.markdown("---")


    st.subheader(
        "Database"
    )


    count = get_candidate_count()


    st.write(
        f"Candidates currently stored: **{count}**"
    )


    if st.button(
        "Clear RAG Candidate Database"
    ):

        deleted = clear_all_candidates()


        st.success(
            f"{deleted} candidate records removed."
        )


        st.rerun()