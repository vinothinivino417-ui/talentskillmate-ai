from llm_engine import (
    analyze_resume,
    summarize_resume,
    match_resume_to_job,
    ask_skyhigh,
    generate_interview_questions,
)

from rag_engine import (
    add_candidate,
    search_candidates,
)


# ============================================================
# SKYHIGH AGENT
# ============================================================

class SkyHighAgent:

    def __init__(self):

        self.name = "SkyHigh"

        self.product = "TalentSkillMate AI"


    # ========================================================
    # ANALYZE CANDIDATE
    # ========================================================

    def analyze_candidate(
        self,
        resume_text,
    ):

        profile = analyze_resume(
            resume_text
        )

        summary = summarize_resume(
            profile
        )

        profile["professional_summary"] = (
            summary
        )

        return profile


    # ========================================================
    # STORE CANDIDATE
    # ========================================================

    def store_candidate(
        self,
        candidate_profile,
        resume_hash=None,
    ):

        return add_candidate(
            candidate_profile=candidate_profile,
            resume_hash=resume_hash,
        )


    # ========================================================
    # MATCH CANDIDATE
    # ========================================================

    def match_candidate(
        self,
        candidate_profile,
        job_description,
    ):

        return match_resume_to_job(
            candidate_profile,
            job_description,
        )


    # ========================================================
    # FIND CANDIDATES
    # ========================================================

    def find_candidates(
        self,
        query,
        n_results=5,
    ):

        return search_candidates(
            query,
            n_results=n_results,
        )


    # ========================================================
    # ASK SKYHIGH
    # ========================================================

    def ask(
        self,
        question,
        candidate_profile=None,
        resume_text="",
    ):

        rag_context = ""

        try:

            results = self.find_candidates(
                question,
                n_results=3,
            )

            documents = results.get(
                "documents",
                [],
            )

            if documents:

                if isinstance(
                    documents[0],
                    list,
                ):

                    documents = documents[0]

                rag_context = "\n\n".join(
                    str(document)
                    for document in documents
                )

        except Exception:

            rag_context = ""

        return ask_skyhigh(
            question=question,
            candidate_profile=candidate_profile,
            resume_text=resume_text,
            rag_context=rag_context,
        )


    # ========================================================
    # INTERVIEW QUESTIONS
    # ========================================================

    def generate_questions(
        self,
        candidate_profile,
        job_description="",
        interview_type="Technical Interview",
        number_of_questions=6,
    ):

        return generate_interview_questions(
            candidate_profile=candidate_profile,
            job_description=job_description,
            interview_type=interview_type,
            number_of_questions=number_of_questions,
        )


    # ========================================================
    # COMPLETE RECRUITMENT WORKFLOW
    # ========================================================

    def run_recruitment_workflow(
        self,
        resume_text,
        job_description=None,
        store_candidate=True,
        resume_hash=None,
    ):

        result = {
            "agent": self.name,
            "status": "started",
            "candidate_profile": None,
            "match_report": None,
            "candidate_id": None,
            "storage_result": None,
            "steps_completed": [],
        }


        # ----------------------------------------------------
        # STEP 1 — ANALYZE RESUME
        # ----------------------------------------------------

        profile = self.analyze_candidate(
            resume_text
        )

        result["candidate_profile"] = profile

        result["steps_completed"].append(
            "Resume analyzed"
        )


        # ----------------------------------------------------
        # STEP 2 — STORE / REPLACE IN RAG
        # ----------------------------------------------------

        if store_candidate:

            storage_result = (
                self.store_candidate(
                    candidate_profile=profile,
                    resume_hash=resume_hash,
                )
            )

            result["storage_result"] = (
                storage_result
            )

            result["candidate_id"] = (
                storage_result.get(
                    "candidate_id",
                    "",
                )
            )

            if storage_result.get(
                "replaced",
                False,
            ):

                result["steps_completed"].append(
                    "Existing candidate replaced with latest resume"
                )

            else:

                result["steps_completed"].append(
                    "Candidate stored in RAG database"
                )


        # ----------------------------------------------------
        # STEP 3 — MATCH JOB
        # ----------------------------------------------------

        if (
            job_description
            and job_description.strip()
        ):

            match_report = (
                self.match_candidate(
                    profile,
                    job_description,
                )
            )

            result["match_report"] = (
                match_report
            )

            result["steps_completed"].append(
                "Candidate matched with job description"
            )


        # ----------------------------------------------------
        # COMPLETE
        # ----------------------------------------------------

        result["status"] = "completed"

        return result


# ============================================================
# PUBLIC WORKFLOW FUNCTION
# ============================================================

def run_skyhigh(
    resume_text,
    job_description=None,
    store_candidate=True,
    resume_hash=None,
):

    agent = SkyHighAgent()

    return agent.run_recruitment_workflow(
        resume_text=resume_text,
        job_description=job_description,
        store_candidate=store_candidate,
        resume_hash=resume_hash,
    )


# ============================================================
# PUBLIC ASK FUNCTION
# ============================================================

def ask_skyhigh_agent(
    question,
    candidate_profile=None,
    resume_text="",
):

    agent = SkyHighAgent()

    return agent.ask(
        question=question,
        candidate_profile=candidate_profile,
        resume_text=resume_text,
    )


# ============================================================
# PUBLIC INTERVIEW FUNCTION
# ============================================================

def generate_skyhigh_interview(
    candidate_profile,
    job_description="",
    interview_type="Technical Interview",
    number_of_questions=6,
):

    agent = SkyHighAgent()

    return agent.generate_questions(
        candidate_profile=candidate_profile,
        job_description=job_description,
        interview_type=interview_type,
        number_of_questions=number_of_questions,
    )