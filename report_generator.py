from io import BytesIO
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def _safe(value, default=""):
    if value is None:
        return default
    return str(value)


def _list_text(items):
    if not items:
        return "None"
    return ", ".join(str(item) for item in items)


def create_report_pdf(
    candidate_profile,
    match_report=None,
    job_description="",
):
    """
    Create a recruiter report PDF in memory.

    Returns:
        bytes
    """

    candidate_profile = candidate_profile or {}
    match_report = match_report or {}

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=12,
        spaceAfter=7,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5,
    )

    story = []

    story.append(
        Paragraph(
            "TalentSkillMate AI",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Recruiter Candidate Intelligence Report",
            subtitle_style,
        )
    )

    candidate_name = _safe(
        candidate_profile.get(
            "candidate_name",
            "Candidate",
        ),
        "Candidate",
    )

    story.append(
        Paragraph(
            f"<b>Candidate:</b> {candidate_name}",
            body_style,
        )
    )

    email = candidate_profile.get("email", "")
    phone = candidate_profile.get("phone", "")
    location = candidate_profile.get("location", "")

    if email:
        story.append(
            Paragraph(
                f"<b>Email:</b> {_safe(email)}",
                body_style,
            )
        )

    if phone:
        story.append(
            Paragraph(
                f"<b>Phone:</b> {_safe(phone)}",
                body_style,
            )
        )

    if location:
        story.append(
            Paragraph(
                f"<b>Location:</b> {_safe(location)}",
                body_style,
            )
        )

    # ---------------------------------------------------------
    # Professional Summary
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Professional Summary",
            heading_style,
        )
    )

    summary = candidate_profile.get(
        "professional_summary",
        "",
    )

    story.append(
        Paragraph(
            _safe(summary, "No professional summary available."),
            body_style,
        )
    )

    # ---------------------------------------------------------
    # Match Analysis
    # ---------------------------------------------------------

    if match_report:
        story.append(
            Paragraph(
                "Candidate–Job Match Analysis",
                heading_style,
            )
        )

        overall = match_report.get(
            "overall_match_score",
            0,
        )

        skill = match_report.get(
            "skill_match_score",
            0,
        )

        experience = match_report.get(
            "experience_match_score",
            0,
        )

        education = match_report.get(
            "education_match_score",
            0,
        )

        score_data = [
            ["Metric", "Score"],
            ["Overall Match", f"{overall}%"],
            ["Skill Match", f"{skill}%"],
            ["Experience Match", f"{experience}%"],
            ["Education Match", f"{education}%"],
        ]

        score_table = Table(
            score_data,
            colWidths=[100 * mm, 55 * mm],
        )

        score_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#3157D5"),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.whitesmoke,
                    ),
                    (
                        "FONTNAME",
                        (0, 1),
                        (-1, -1),
                        "Helvetica",
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (1, -1),
                        "CENTER",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(score_table)
        story.append(Spacer(1, 8))

        matching_skills = match_report.get(
            "matching_skills",
            [],
        )

        missing_skills = match_report.get(
            "missing_skills",
            [],
        )

        story.append(
            Paragraph(
                "<b>Matching Skills:</b> "
                + _list_text(matching_skills),
                body_style,
            )
        )

        story.append(
            Paragraph(
                "<b>Missing Skills:</b> "
                + _list_text(missing_skills),
                body_style,
            )
        )

        relevant_experience = match_report.get(
            "relevant_experience",
            [],
        )

        if relevant_experience:
            story.append(
                Paragraph(
                    "<b>Relevant Experience:</b> "
                    + _list_text(relevant_experience),
                    body_style,
                )
            )

        strengths = match_report.get(
            "strengths",
            [],
        )

        if strengths:
            story.append(
                Paragraph(
                    "<b>Strengths:</b> "
                    + _list_text(strengths),
                    body_style,
                )
            )

        concerns = match_report.get(
            "concerns",
            [],
        )

        if concerns:
            story.append(
                Paragraph(
                    "<b>Considerations:</b> "
                    + _list_text(concerns),
                    body_style,
                )
            )

        explanation = match_report.get(
            "match_explanation",
            "",
        )

        if explanation:
            story.append(
                Paragraph(
                    "<b>Match Explanation:</b> "
                    + _safe(explanation),
                    body_style,
                )
            )

    # ---------------------------------------------------------
    # Skills
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Candidate Skills",
            heading_style,
        )
    )

    skills = candidate_profile.get(
        "skills",
        [],
    )

    story.append(
        Paragraph(
            _list_text(skills),
            body_style,
        )
    )

    # ---------------------------------------------------------
    # Education
    # ---------------------------------------------------------

    education = candidate_profile.get(
        "education",
        [],
    )

    if education:
        story.append(
            Paragraph(
                "Education",
                heading_style,
            )
        )

        for item in education:
            degree = _safe(item.get("degree", ""))
            institution = _safe(
                item.get("institution", "")
            )
            year = _safe(item.get("year", ""))

            education_text = " — ".join(
                part
                for part in [
                    degree,
                    institution,
                    year,
                ]
                if part
            )

            story.append(
                Paragraph(
                    f"• {education_text}",
                    body_style,
                )
            )

    # ---------------------------------------------------------
    # Work Experience
    # ---------------------------------------------------------

    experience = candidate_profile.get(
        "work_experience",
        [],
    )

    if experience:
        story.append(
            Paragraph(
                "Work Experience",
                heading_style,
            )
        )

        for item in experience:
            job_title = _safe(
                item.get("job_title", "")
            )
            company = _safe(
                item.get("company", "")
            )
            duration = _safe(
                item.get("duration", "")
            )

            title_line = " — ".join(
                part
                for part in [
                    job_title,
                    company,
                    duration,
                ]
                if part
            )

            if title_line:
                story.append(
                    Paragraph(
                        f"<b>{title_line}</b>",
                        body_style,
                    )
                )

            responsibilities = item.get(
                "responsibilities",
                [],
            )

            for responsibility in responsibilities:
                story.append(
                    Paragraph(
                        f"• {_safe(responsibility)}",
                        body_style,
                    )
                )

    # ---------------------------------------------------------
    # Projects
    # ---------------------------------------------------------

    projects = candidate_profile.get(
        "projects",
        [],
    )

    if projects:
        story.append(
            Paragraph(
                "Projects",
                heading_style,
            )
        )

        for project in projects:
            project_name = _safe(
                project.get(
                    "project_name",
                    "Project",
                )
            )

            description = _safe(
                project.get(
                    "description",
                    "",
                )
            )

            technologies = project.get(
                "technologies",
                [],
            )

            story.append(
                Paragraph(
                    f"<b>{project_name}</b>",
                    body_style,
                )
            )

            if description:
                story.append(
                    Paragraph(
                        description,
                        body_style,
                    )
                )

            if technologies:
                story.append(
                    Paragraph(
                        "<b>Technologies:</b> "
                        + _list_text(technologies),
                        body_style,
                    )
                )

    # ---------------------------------------------------------
    # Job Description
    # ---------------------------------------------------------

    if job_description:
        story.append(
            Paragraph(
                "Job Description Used for Matching",
                heading_style,
            )
        )

        story.append(
            Paragraph(
                _safe(job_description),
                body_style,
            )
        )

    # ---------------------------------------------------------
    # Disclaimer
    # ---------------------------------------------------------

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            "<b>Recruiter Decision-Support Notice:</b> "
            "This report provides AI-generated candidate analysis "
            "to support recruiter review. It is not a hiring decision "
            "and should not be used as the sole basis for employment decisions.",
            body_style,
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


def create_report_text(
    candidate_profile,
    match_report=None,
    job_description="",
):
    """
    Create a plain-text recruiter report.
    """

    candidate_profile = candidate_profile or {}
    match_report = match_report or {}

    lines = []

    lines.append("TALENTSKILLMATE AI")
    lines.append("Recruiter Candidate Intelligence Report")
    lines.append("=" * 60)

    lines.append(
        f"Candidate: "
        f"{candidate_profile.get('candidate_name', 'Candidate')}"
    )

    if candidate_profile.get("email"):
        lines.append(
            f"Email: {candidate_profile['email']}"
        )

    if candidate_profile.get("phone"):
        lines.append(
            f"Phone: {candidate_profile['phone']}"
        )

    if candidate_profile.get("location"):
        lines.append(
            f"Location: {candidate_profile['location']}"
        )

    lines.append("")
    lines.append("PROFESSIONAL SUMMARY")
    lines.append("-" * 60)

    lines.append(
        candidate_profile.get(
            "professional_summary",
            "No professional summary available.",
        )
    )

    if match_report:
        lines.append("")
        lines.append("MATCH ANALYSIS")
        lines.append("-" * 60)

        lines.append(
            f"Overall Match: "
            f"{match_report.get('overall_match_score', 0)}%"
        )

        lines.append(
            f"Skill Match: "
            f"{match_report.get('skill_match_score', 0)}%"
        )

        lines.append(
            f"Experience Match: "
            f"{match_report.get('experience_match_score', 0)}%"
        )

        lines.append(
            f"Education Match: "
            f"{match_report.get('education_match_score', 0)}%"
        )

        lines.append("")
        lines.append(
            "Matching Skills: "
            + _list_text(
                match_report.get(
                    "matching_skills",
                    [],
                )
            )
        )

        lines.append(
            "Missing Skills: "
            + _list_text(
                match_report.get(
                    "missing_skills",
                    [],
                )
            )
        )

        lines.append("")
        lines.append("Match Explanation:")
        lines.append(
            match_report.get(
                "match_explanation",
                "",
            )
        )

    lines.append("")
    lines.append("SKILLS")
    lines.append("-" * 60)

    lines.append(
        _list_text(
            candidate_profile.get(
                "skills",
                [],
            )
        )
    )

    lines.append("")
    lines.append("RECRUITER DECISION-SUPPORT NOTICE")
    lines.append("-" * 60)

    lines.append(
        "This report is AI-generated recruiter decision support. "
        "It is not a hiring decision."
    )

    return "\n".join(lines)


def create_report_json(
    candidate_profile,
    match_report=None,
    job_description="",
):
    """
    Create recruiter report JSON bytes.
    """

    data = {
        "platform": "TalentSkillMate AI",
        "report_type": "Recruiter Candidate Intelligence Report",
        "candidate_profile": candidate_profile or {},
        "match_report": match_report or {},
        "job_description": job_description or "",
        "decision_support_notice": (
            "This report is AI-generated recruiter decision support "
            "and is not a hiring decision."
        ),
    }

    return json.dumps(
        data,
        indent=4,
        ensure_ascii=False,
    ).encode("utf-8")