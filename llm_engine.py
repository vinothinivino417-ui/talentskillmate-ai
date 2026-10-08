import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

# ------------------------------------------------------------
# Provider configuration
# ------------------------------------------------------------
# Change these values in .env when you want to switch provider.
#
# Current:
#   Provider = Groq
#   Model    = openai/gpt-oss-20b
#
# Future provider/model changes should mainly happen here.
# ------------------------------------------------------------

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

LLM_API_KEY = os.getenv("LLM_API_KEY")

MODEL_NAME = os.getenv(
    "LLM_MODEL",
    "openai/gpt-oss-20b"
)

BASE_URL = os.getenv(
    "LLM_BASE_URL",
    "https://api.groq.com/openai/v1"
)

if not LLM_API_KEY:
    raise ValueError(
        "LLM_API_KEY is missing. "
        "Please add your LLM API key to the .env file."
    )


# ============================================================
# LLM CLIENT
# ============================================================

client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=BASE_URL
)


# ============================================================
# JSON EXTRACTION HELPER
# ============================================================

def _extract_json(text):
    """
    Extract JSON from an LLM response.

    Handles:
    - Normal JSON
    - ```json ... ```
    - Extra text before/after JSON
    """

    if not text:
        raise ValueError(
            "Empty response received from the model."
        )

    text = text.strip()

    # Remove markdown code fences
    text = re.sub(
        r"^```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"^```\s*",
        "",
        text
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    text = text.strip()

    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Find JSON object
    # --------------------------------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        candidate = text[start:end + 1]

        try:
            return json.loads(candidate)

        except json.JSONDecodeError:
            pass

    # --------------------------------------------------------
    # Find JSON array
    # --------------------------------------------------------

    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1 and end > start:

        candidate = text[start:end + 1]

        try:
            return json.loads(candidate)

        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Model did not return valid JSON.\n"
        f"Model response:\n{text}"
    )


# ============================================================
# BASIC LLM RESPONSE
# ============================================================

def generate_response(prompt, max_tokens=3500):
    """
    Send a prompt to the configured LLM provider.

    The rest of TalentSkillMate AI does not need to know
    which provider is being used.
    """

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            max_tokens=max_tokens
        )

        # ----------------------------------------------------
        # Check response choices
        # ----------------------------------------------------

        if not response.choices:
            raise RuntimeError(
                f"{LLM_PROVIDER} returned no response choices."
            )

        message = response.choices[0].message

        # ----------------------------------------------------
        # Get assistant content
        # ----------------------------------------------------

        content = getattr(
            message,
            "content",
            None
        )

        if content is not None and str(content).strip():

            return str(content).strip()

        raise RuntimeError(
            f"{LLM_PROVIDER} returned an empty response."
        )

    except Exception as e:

        error_text = str(e).lower()

        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        if (
            "401" in error_text
            or "unauthorized" in error_text
            or "invalid api key" in error_text
        ):

            raise RuntimeError(
                f"{LLM_PROVIDER} authentication failed. "
                "Check LLM_API_KEY in your .env file."
            ) from e

        # ----------------------------------------------------
        # Permission
        # ----------------------------------------------------

        if (
            "403" in error_text
            or "forbidden" in error_text
        ):

            raise RuntimeError(
                f"{LLM_PROVIDER} denied the request. "
                "Check your API key permissions."
            ) from e

        # ----------------------------------------------------
        # Rate limit
        # ----------------------------------------------------

        if (
            "429" in error_text
            or "rate limit" in error_text
            or "too many requests" in error_text
        ):

            raise RuntimeError(
                f"{LLM_PROVIDER} rate limit reached. "
                "Please wait and try again."
            ) from e

        # ----------------------------------------------------
        # Payment / credit
        # ----------------------------------------------------

        if (
            "402" in error_text
            or "payment" in error_text
            or "insufficient credits" in error_text
        ):

            raise RuntimeError(
                f"{LLM_PROVIDER} API credit/usage limit reached."
            ) from e

        # ----------------------------------------------------
        # Model unavailable
        # ----------------------------------------------------

        if (
            "404" in error_text
            or "not found" in error_text
            or "model_not_found" in error_text
        ):

            raise RuntimeError(
                f"LLM model '{MODEL_NAME}' is unavailable "
                f"on {LLM_PROVIDER}."
            ) from e

        # ----------------------------------------------------
        # Generic error
        # ----------------------------------------------------

        raise RuntimeError(
            f"{LLM_PROVIDER} LLM error: {e}"
        ) from e


# ============================================================
# RESUME ANALYSIS
# ============================================================

def analyze_resume(resume_text):
    """
    Analyze a resume and return a structured candidate profile.
    """

    if not resume_text or not resume_text.strip():

        raise ValueError(
            "Resume text is empty."
        )

    prompt = f"""
You are an expert HR resume screening assistant.

Analyze the following resume and extract the candidate information.

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. Do not use Markdown.
3. Do not add explanations outside the JSON.
4. Do not invent information.
5. If information is unavailable, use an empty string or empty array.
6. Extract skills exactly or clearly from the resume.
7. Keep work experience factual.
8. Keep education factual.
9. Keep projects factual.
10. The professional summary must be based only on the resume.

Return exactly this JSON structure:

{{
    "candidate_name": "",
    "email": "",
    "phone": "",
    "location": "",
    "professional_summary": "",
    "education": [
        {{
            "degree": "",
            "institution": "",
            "year": ""
        }}
    ],
    "skills": [],
    "work_experience": [
        {{
            "job_title": "",
            "company": "",
            "duration": "",
            "responsibilities": []
        }}
    ],
    "projects": [
        {{
            "project_name": "",
            "description": "",
            "technologies": []
        }}
    ],
    "certifications": [],
    "languages": []
}}

RESUME:

{resume_text}
"""

    response = generate_response(
        prompt,
        max_tokens=4500
    )

    try:

        profile = _extract_json(response)

    except ValueError as e:

        raise ValueError(
            "Resume analysis failed because the model "
            "did not return valid JSON.\n\n"
            f"{e}"
        ) from e

    # --------------------------------------------------------
    # Ensure expected fields exist
    # --------------------------------------------------------

    profile.setdefault(
        "candidate_name",
        ""
    )

    profile.setdefault(
        "email",
        ""
    )

    profile.setdefault(
        "phone",
        ""
    )

    profile.setdefault(
        "location",
        ""
    )

    profile.setdefault(
        "professional_summary",
        ""
    )

    profile.setdefault(
        "education",
        []
    )

    profile.setdefault(
        "skills",
        []
    )

    profile.setdefault(
        "work_experience",
        []
    )

    profile.setdefault(
        "projects",
        []
    )

    profile.setdefault(
        "certifications",
        []
    )

    profile.setdefault(
        "languages",
        []
    )

    return profile


# ============================================================
# RESUME SUMMARY
# ============================================================

def summarize_resume(candidate_profile):
    """
    Generate a concise professional summary.

    If professional_summary already exists, reuse it
    instead of making another API request.
    """

    existing_summary = candidate_profile.get(
        "professional_summary",
        ""
    )

    if existing_summary and existing_summary.strip():

        return existing_summary.strip()

    prompt = f"""
You are an HR recruitment assistant.

Create a concise professional summary for the candidate below.

Use ONLY the information provided.

Do not invent experience, skills, education, or achievements.

Candidate profile:

{json.dumps(candidate_profile, indent=2)}

Return ONLY valid JSON:

{{
    "summary": ""
}}
"""

    response = generate_response(
        prompt,
        max_tokens=1000
    )

    data = _extract_json(response)

    return data.get(
        "summary",
        ""
    ).strip()


# ============================================================
# RESUME TO JOB MATCHING
# ============================================================

def match_resume_to_job(
    candidate_profile,
    job_description
):
    """
    Compare a candidate profile against a job description.

    Returns scores and evidence-based matching information.
    """

    if not candidate_profile:

        raise ValueError(
            "Candidate profile is empty."
        )

    if not job_description or not job_description.strip():

        raise ValueError(
            "Job description is empty."
        )

    prompt = f"""
You are an expert HR recruitment screening assistant.

Compare the candidate profile with the job description.

IMPORTANT:

1. Return ONLY valid JSON.
2. Do not invent candidate experience.
3. Match skills based on evidence.
4. Identify missing skills.
5. Evaluate experience relevance.
6. Evaluate education relevance.
7. Provide a fair overall score from 0 to 100.
8. This is a recruiter recommendation, NOT a hiring decision.
9. Explain the score using evidence from the candidate profile.

CANDIDATE PROFILE:

{json.dumps(candidate_profile, indent=2)}

JOB DESCRIPTION:

{job_description}

Return exactly this JSON:

{{
    "overall_match_score": 0,
    "skill_match_score": 0,
    "experience_match_score": 0,
    "education_match_score": 0,
    "matching_skills": [],
    "missing_skills": [],
    "relevant_experience": [],
    "strengths": [],
    "concerns": [],
    "match_explanation": ""
}}
"""

    response = generate_response(
        prompt,
        max_tokens=3500
    )

    result = _extract_json(response)

    # --------------------------------------------------------
    # Defaults
    # --------------------------------------------------------

    result.setdefault(
        "overall_match_score",
        0
    )

    result.setdefault(
        "skill_match_score",
        0
    )

    result.setdefault(
        "experience_match_score",
        0
    )

    result.setdefault(
        "education_match_score",
        0
    )

    result.setdefault(
        "matching_skills",
        []
    )

    result.setdefault(
        "missing_skills",
        []
    )

    result.setdefault(
        "relevant_experience",
        []
    )

    result.setdefault(
        "strengths",
        []
    )

    result.setdefault(
        "concerns",
        []
    )

    result.setdefault(
        "match_explanation",
        ""
    )

    # --------------------------------------------------------
    # Fallback skill score
    # --------------------------------------------------------

    matching = result.get(
        "matching_skills",
        []
    )

    missing = result.get(
        "missing_skills",
        []
    )

    if (
        result.get(
            "skill_match_score",
            0
        ) == 0
        and (matching or missing)
    ):

        total_skills = (
            len(matching)
            + len(missing)
        )

        if total_skills > 0:

            result["skill_match_score"] = round(
                (
                    len(matching)
                    / total_skills
                ) * 100
            )

    # --------------------------------------------------------
    # Ensure scores are valid
    # --------------------------------------------------------

    score_fields = [
        "overall_match_score",
        "skill_match_score",
        "experience_match_score",
        "education_match_score"
    ]

    for field in score_fields:

        try:

            value = float(
                result.get(
                    field,
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            value = 0

        value = max(
            0,
            min(
                100,
                value
            )
        )

        result[field] = round(
            value,
            2
        )

    return result


# ============================================================
# SKYHIGH AI RECRUITMENT ASSISTANT
# ============================================================

def ask_skyhigh(
    question,
    candidate_profile=None,
    resume_text="",
    rag_context=""
):
    """
    Ask SkyHigh AI a recruiter-focused question.

    SkyHigh provides decision support and recommendations,
    but does not make the final hiring decision.
    """

    if not question or not question.strip():

        return "Please enter a question."

    candidate_information = ""

    if candidate_profile:

        candidate_information = json.dumps(
            candidate_profile,
            indent=2
        )

    prompt = f"""
You are SkyHigh AI, an intelligent recruitment assistant
inside TalentSkillMate AI.

Your role is to help recruiters understand resumes,
candidate skills, job matching, missing skills,
candidate comparisons, and interview preparation.

IMPORTANT RULES:

1. Provide evidence-based answers.
2. Use the supplied candidate information.
3. Use RAG context when available.
4. Never invent candidate information.
5. Do not make a final hiring decision.
6. Present recommendations as recruiter decision support.
7. Be concise but useful.
8. If the information is unavailable, clearly say so.
9. Do not claim something exists if it is not present.

CANDIDATE PROFILE:

{candidate_information}

RESUME TEXT:

{resume_text}

RAG CONTEXT:

{rag_context}

RECRUITER QUESTION:

{question}

Provide a clear recruiter-focused answer.
"""

    return generate_response(
        prompt,
        max_tokens=1800
    )


# ============================================================
# INTERVIEW QUESTION GENERATION
# ============================================================

def generate_interview_questions(
    candidate_profile,
    job_description="",
    interview_type="Technical Interview",
    number_of_questions=6
):
    """
    Generate candidate-specific interview questions.
    """

    if not candidate_profile:

        raise ValueError(
            "Candidate profile is empty."
        )

    try:

        number_of_questions = int(
            number_of_questions
        )

    except (
        TypeError,
        ValueError
    ):

        number_of_questions = 6

    number_of_questions = max(
        1,
        min(
            number_of_questions,
            20
        )
    )

    prompt = f"""
You are an expert technical recruiter.

Generate interview questions based on the candidate profile
and the job description.

Interview type:
{interview_type}

Number of questions:
{number_of_questions}

Candidate profile:

{json.dumps(candidate_profile, indent=2)}

Job description:

{job_description}

IMPORTANT:

1. Return ONLY valid JSON.
2. Do not invent candidate experience.
3. Questions should be relevant to the candidate.
4. Questions should help a recruiter evaluate the candidate.
5. Include a short reason for each question.

Return exactly:

{{
    "questions": [
        {{
            "question": "",
            "category": "",
            "reason": ""
        }}
    ]
}}
"""

    response = generate_response(
        prompt,
        max_tokens=3000
    )

    result = _extract_json(response)

    questions = result.get(
        "questions",
        []
    )

    if not isinstance(
        questions,
        list
    ):

        questions = []

    questions = questions[
        :number_of_questions
    ]

    return {
        "questions": questions
    }


# ============================================================
# SIMPLE CONNECTION TEST
# ============================================================

def test_connection():

    response = generate_response(
        "Reply with exactly: "
        "TALENTSKILLMATE LLM CONNECTION SUCCESS",
        max_tokens=200
    )

    return response


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "TalentSkillMate AI - LLM Connection Test"
    )

    print("=" * 60)

    try:

        result = test_connection()

        print("\nConnection test:")
        print(result)

        print("\nProvider:")
        print(LLM_PROVIDER)

        print("\nModel:")
        print(MODEL_NAME)

        print("\nBase URL:")
        print(BASE_URL)

        print("\nStatus:")
        print("SUCCESS")

    except Exception as e:

        print("\nStatus:")
        print("FAILED")

        print("\nError:")
        print(e)