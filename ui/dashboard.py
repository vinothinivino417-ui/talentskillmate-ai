import streamlit as st

from ui.components import (
    asset_uri,
    html_block,
    top_bar,
    kpi_card,
    feature_card,
    recent_activity_row,
    footer,
)

from rag_engine import get_candidate_count


def show_dashboard():

    # ========================================================
    # TOP BAR
    # ========================================================

    top_bar()


    # ========================================================
    # LOAD ASSETS
    # ========================================================

    robot = asset_uri(
        "skyhigh_robot.png"
    )

    resume_icon = asset_uri(
        "resume_icon.png"
    )

    matching_icon = asset_uri(
        "matching_icon.png"
    )

    rag_icon = asset_uri(
        "rag_icon.png"
    )

    reports_icon = asset_uri(
        "reports_icon.png"
    )


    # ========================================================
    # ROBOT
    # ========================================================

    if robot:

        robot_html = f"""
        <div class="skyhigh-robot">
            <img
                src="{robot}"
                alt="SkyHigh AI"
            >
            <div class="robot-glow"></div>
        </div>
        """

    else:

        robot_html = """
        <div class="skyhigh-robot robot-fallback">
            🤖
        </div>
        """


    # ========================================================
    # ICONS
    # ========================================================

    resume_html = (
        f'<img src="{resume_icon}" '
        f'class="hero-action-icon" alt="">'
        if resume_icon
        else "📄"
    )

    matching_html = (
        f'<img src="{matching_icon}" '
        f'class="hero-action-icon" alt="">'
        if matching_icon
        else "🎯"
    )

    rag_html = (
        f'<img src="{rag_icon}" '
        f'class="hero-action-icon" alt="">'
        if rag_icon
        else "🧠"
    )

    reports_html = (
        f'<img src="{reports_icon}" '
        f'class="hero-action-icon" alt="">'
        if reports_icon
        else "📊"
    )


    # ========================================================
    # HERO
    # ========================================================

    html_block(
        f"""
        <section class="hero-section">

            <div class="hero-left">

                <div class="hero-badge">
                    <span class="hero-badge-dot"></span>
                    AI RECRUITMENT INTELLIGENCE
                </div>

                <h1 class="hero-title">
                    Hire Smarter.<br>
                    <span>Match Better.</span>
                </h1>

                <p class="hero-description">
                    TalentSkillMate AI transforms resumes into actionable
                    candidate intelligence using AI-powered screening,
                    matching and recruiter insights.
                </p>

                <div class="hero-buttons">

                    <a
                        href="?page=Resume%20Screening"
                        class="hero-primary-button"
                        style="
                            text-decoration:none;
                            display:inline-block;
                            cursor:pointer;
                        "
                    >
                        ✦ Start Resume Screening
                    </a>

                    <a
                        href="?page=Ask%20SkyHigh"
                        class="hero-secondary-button"
                        style="
                            text-decoration:none;
                            display:inline-block;
                            cursor:pointer;
                        "
                    >
                        Ask SkyHigh →
                    </a>

                </div>

                <div class="hero-trust">

                    <div class="trust-item">
                        <span>✓</span>
                        Evidence-based matching
                    </div>

                    <div class="trust-item">
                        <span>✓</span>
                        AI-powered insights
                    </div>

                    <div class="trust-item">
                        <span>✓</span>
                        Recruiter decision support
                    </div>

                </div>

            </div>


            <div class="hero-right">

                <div class="ai-scene">

                    <div class="orbit orbit-one"></div>
                    <div class="orbit orbit-two"></div>
                    <div class="orbit orbit-three"></div>


                    <div class="float-card float-one">

                        {resume_html}

                        <div class="float-card-text">

                            <span class="float-label">
                                Resume Screening
                            </span>

                            <span class="float-small">
                                AI Analysis
                            </span>

                        </div>

                    </div>


                    <div class="float-card float-two">

                        {matching_html}

                        <div class="float-card-text">

                            <span class="float-label">
                                Candidate Matching
                            </span>

                            <span class="float-small">
                                Smart Match
                            </span>

                        </div>

                    </div>


                    <div class="float-card float-three">

                        {rag_html}

                        <div class="float-card-text">

                            <span class="float-label">
                                RAG Intelligence
                            </span>

                            <span class="float-small">
                                Knowledge Search
                            </span>

                        </div>

                    </div>


                    <div class="float-card float-four">

                        {reports_html}

                        <div class="float-card-text">

                            <span class="float-label">
                                Recruiter Reports
                            </span>

                            <span class="float-small">
                                Hiring Insights
                            </span>

                        </div>

                    </div>


                    {robot_html}

                </div>

            </div>

        </section>
        """
    )


    # ========================================================
    # LIVE WORKSPACE
    # ========================================================

    rag_count = get_candidate_count()

    resumes_screened = st.session_state.get(
        "resume_count",
        0,
    )

    candidates_matched = st.session_state.get(
        "match_count",
        0,
    )

    reports_generated = st.session_state.get(
        "report_count",
        0,
    )

    candidate_profile = st.session_state.get(
        "candidate_analysis"
    )

    skills_discovered = 0

    if candidate_profile:

        skills_discovered = len(
            candidate_profile.get(
                "skills",
                [],
            )
        )


    html_block(
        """
        <div class="section-heading">

            <div>

                <div class="section-kicker">
                    LIVE WORKSPACE
                </div>

                <div class="section-title">
                    Recruitment Overview
                </div>

            </div>

            <div class="section-description">
                Your AI recruitment workspace at a glance
            </div>

        </div>
        """
    )


    # ========================================================
    # KPI
    # ========================================================

    kpi_columns = st.columns(4)

    with kpi_columns[0]:

        kpi_card(
            "◉",
            "Resumes Screened",
            resumes_screened,
        )

    with kpi_columns[1]:

        kpi_card(
            "✦",
            "Candidates Matched",
            candidates_matched,
        )

    with kpi_columns[2]:

        kpi_card(
            "⌁",
            "Skills Discovered",
            skills_discovered,
        )

    with kpi_columns[3]:

        kpi_card(
            "↗",
            "Reports Generated",
            reports_generated,
        )


    # ========================================================
    # CAPABILITIES
    # ========================================================

    html_block(
        """
        <div class="section-heading capabilities-heading">

            <div>

                <div class="section-kicker">
                    AI CAPABILITIES
                </div>

                <div class="section-title">
                    Everything recruiters need
                </div>

            </div>

            <div class="section-description">
                From resume parsing to candidate intelligence
            </div>

        </div>
        """
    )


    feature_columns = st.columns(5)

    with feature_columns[0]:

        feature_card(
            "◈",
            "Resume Screening",
            "Extract candidate information and analyze resumes automatically.",
        )

    with feature_columns[1]:

        feature_card(
            "⌁",
            "Skill Discovery",
            "Identify explicit and evidence-based skills from candidate profiles.",
        )

    with feature_columns[2]:

        feature_card(
            "◎",
            "Candidate Matching",
            "Compare candidates against job requirements with explainable scoring.",
        )

    with feature_columns[3]:

        feature_card(
            "◇",
            "Interview Studio",
            "Generate structured interview questions based on candidate evidence.",
        )

    with feature_columns[4]:

        feature_card(
            "▣",
            "Recruiter Reports",
            "Create recruiter-ready reports and candidate intelligence summaries.",
        )


    # ========================================================
    # ACTIVITY
    # ========================================================

    html_block(
        """
        <div class="section-heading activity-heading">

            <div>

                <div class="section-kicker">
                    ACTIVITY CENTER
                </div>

                <div class="section-title">
                    Recent Recruitment Activity
                </div>

            </div>

        </div>
        """
    )


    left_column, right_column = st.columns(
        [1.55, 1]
    )


    # ========================================================
    # RECENT ACTIVITY
    # ========================================================

    with left_column:

        html_block(
            """
            <div class="dashboard-panel">

                <div class="panel-header">

                    <div>

                        <div class="panel-title">
                            Recent Activity
                        </div>

                        <div class="panel-subtitle">
                            Latest actions in your recruitment workspace
                        </div>

                    </div>

                    <div class="panel-status">
                        LIVE
                    </div>

                </div>
            """
        )

        activities = st.session_state.get(
            "activity_log",
            [],
        )

        if activities:

            for activity in activities[:5]:

                recent_activity_row(
                    "📄",
                    activity.get(
                        "action",
                        "Activity",
                    ),
                    activity.get(
                        "description",
                        "",
                    ),
                    activity.get(
                        "time",
                        "Just now",
                    ),
                )

        else:

            recent_activity_row(
                "🤖",
                "SkyHigh AI",
                "Ready for your first resume screening workflow.",
                "Ready",
            )

        html_block(
            """
            </div>
            """
        )


    # ========================================================
    # MATCH OVERVIEW
    # ========================================================

    with right_column:

        match = st.session_state.get(
            "last_match"
        )

        if match:

            score = match.get(
                "overall_match_score",
                0,
            )

        else:

            score = 0


        html_block(
            f"""
            <div class="dashboard-panel match-panel">

                <div class="panel-header">

                    <div>

                        <div class="panel-title">
                            Match Overview
                        </div>

                        <div class="panel-subtitle">
                            Current candidate matching activity
                        </div>

                    </div>

                </div>

                <div class="match-score-circle">

                    <div class="match-score-number">
                        {score}%
                    </div>

                    <div class="match-score-label">
                        Current Match
                    </div>

                </div>

                <div class="match-stats">

                    <div class="match-stat">
                        <strong>{rag_count}</strong>
                        <span>Stored</span>
                    </div>

                    <div class="match-stat">
                        <strong>{candidates_matched}</strong>
                        <span>Matched</span>
                    </div>

                    <div class="match-stat">
                        <strong>{reports_generated}</strong>
                        <span>Reports</span>
                    </div>

                </div>

            </div>
            """
        )


    # ========================================================
    # FOOTER
    # ========================================================

    footer()