from pathlib import Path
import base64
import html
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"

def asset_uri(filename):
    """
    Convert an asset file into a browser-safe data URI.
    Returns None when the image does not exist.
    """

    path = ASSETS_DIR / filename

    if not path.exists():
        print(f"ASSET NOT FOUND: {path}")
        return None

    print(f"ASSET FOUND: {path}")

    suffix = path.suffix.lower()

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }

    mime_type = mime_types.get(
        suffix,
        "application/octet-stream",
    )

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def html_block(content):
    st.html(content)


def brand():
    logo = asset_uri("logo.png")

    if logo:
        logo_html = f"""
        <img
            src="{logo}"
            class="brand-image"
            alt="TalentSkillMate AI"
        >
        """
    else:
        logo_html = """
        <div class="brand-logo">A</div>
        """

    html_block(
        f"""
        <div class="brand-row">

            {logo_html}

            <div>
                <div class="brand-name">
                    TalentSkillMate AI
                </div>

                <div class="brand-subtitle">
                    AI Recruitment Intelligence
                </div>
            </div>

        </div>
        """
    )


def log_activity(action, details="", icon="●"):
    from datetime import datetime

    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []

    activity = {
        "action": action,
        "details": details,
        "icon": icon,
        "time": datetime.now(),
    }

    st.session_state.activity_log.insert(0, activity)

    st.session_state.activity_log = (
        st.session_state.activity_log[:8]
    )


def _activity_time_text(timestamp):
    from datetime import datetime

    if not timestamp:
        return ""

    seconds = int(
        (datetime.now() - timestamp).total_seconds()
    )

    if seconds < 60:
        return "just now"

    minutes = seconds // 60

    if minutes < 60:
        return f"{minutes}m ago"

    hours = minutes // 60

    if hours < 24:
        return f"{hours}h ago"

    days = hours // 24

    if days == 1:
        return "1d ago"

    return f"{days}d ago"


def sidebar_activity():
    activities = st.session_state.get(
        "activity_log",
        [],
    )

    html_items = []

    if not activities:
        html_items.append(
            """
            <div class="activity-item">
                <span class="activity-dot"></span>
                No activity yet
            </div>
            """
        )
    else:
        for item in activities[:5]:

            action = html.escape(
                str(item.get("action", "Activity"))
            )

            details = html.escape(
                str(item.get("details", ""))
            )

            timestamp = item.get("time")

            time_text = _activity_time_text(
                timestamp
            )

            if details:
                text = f"{action} — {details}"
            else:
                text = f"{action} — {time_text}"

            html_items.append(
                f"""
                <div class="activity-item">
                    <span class="activity-dot"></span>
                    {html.escape(text)}
                </div>
                """
            )

    html_block(
        f"""
        <div class="activity-sidebar-title">
            Recent Activity
        </div>

        {''.join(html_items)}
        """
    )

    st.markdown(
    "<div style='height:6px'></div>",
    unsafe_allow_html=True,
)

def top_bar():
    left, right = st.columns([6, 1])

    with left:
        html_block(
            """
            <div class="top-search">
                <span class="top-search-icon">⌕</span>
                Search candidates, skills or roles...
            </div>
            """
        )

    with right:
        html_block(
            """
            <div class="online-box">
                <span class="online-dot"></span>
                SkyHigh AI Online
            </div>
            """
        )

    st.markdown(
        "<div style='height:6px'></div>",
        unsafe_allow_html=True,
    )

def kpi_card(icon, label, value):
    html_block(
        f"""
        <div class="kpi-card">

            <div class="kpi-icon">
                {icon}
            </div>

            <div>
                <div class="kpi-label">
                    {html.escape(label)}
                </div>

                <div class="kpi-value">
                    {html.escape(str(value))}
                </div>
            </div>

        </div>
        """
    )


def image_or_fallback(
    filename,
    fallback,
    class_name,
):
    uri = asset_uri(filename)

    if uri:
        return f"""
        <img
            src="{uri}"
            class="{class_name}"
            alt=""
        >
        """

    return f"""
    <div class="{class_name} robot-fallback">
        {fallback}
    </div>
    """


def feature_card(icon, title, description):
    html_block(
        f"""
        <div class="feature-card">

            <div class="feature-icon">
                {icon}
            </div>

            <div class="feature-title">
                {html.escape(title)}
            </div>

            <div class="feature-text">
                {html.escape(description)}
            </div>

        </div>
        """
    )


def recent_activity_row(
    icon,
    name,
    description,
    time,
):
    html_block(
        f"""
        <div class="recent-row">

            <div class="recent-icon">
                {icon}
            </div>

            <div>
                <div class="recent-name">
                    {html.escape(name)}
                </div>

                <div class="recent-description">
                    {html.escape(description)}
                </div>
            </div>

            <div class="recent-time">
                {html.escape(str(time))}
            </div>

        </div>
        """
    )


def footer():
    html_block(
        """
        <div class="footer">
            TalentSkillMate AI · Powered by SkyHigh AI ·
            Recruiter Decision Support Platform
        </div>
        """
    )