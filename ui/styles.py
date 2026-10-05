import streamlit as st


def load_styles():

    st.markdown(
        """
        <style>

        /* =====================================================
           GLOBAL
        ===================================================== */

        .stApp {
            background:
                radial-gradient(
                    circle at 85% 5%,
                    rgba(67, 170, 255, 0.22),
                    transparent 30%
                ),
                radial-gradient(
                    circle at 15% 35%,
                    rgba(91, 112, 255, 0.14),
                    transparent 32%
                ),
                linear-gradient(
                    135deg,
                    #e5f4ff 0%,
                    #edf5ff 45%,
                    #f0edff 100%
                );

            color: #12213f;
        }


        .block-container {
    padding-top: 0.25rem !important;
    padding-bottom: 2rem;
    max-width: 1500px;
}

/* =====================================================
   REMOVE TOP EMPTY SPACE
   ===================================================== */

header[data-testid="stHeader"] {
    height: 0 !important;
    min-height: 0 !important;
    background: transparent !important;
}

header[data-testid="stHeader"] > div {
    height: 0 !important;
}

div[data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
}

div[data-testid="stAppViewContainer"] > section {
    padding-top: 0 !important;
}

.main .block-container {
    padding-top: 0.25rem !important;
}

        /* =====================================================
           SIDEBAR
        ===================================================== */

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(
                    180deg,
                    #071a3d 0%,
                    #0b2450 45%,
                    #101d48 100%
                );

            border-right: 1px solid rgba(255,255,255,0.08);
        }


        section[data-testid="stSidebar"] > div {
            padding-top: 1.4rem;
        }


        section[data-testid="stSidebar"] * {
            color: #edf6ff;
        }


        .workspace-title {
            margin-top: 30px;
            margin-bottom: 12px;

            font-size: 11px;
            font-weight: 700;

            letter-spacing: 1.8px;
            text-transform: uppercase;

            color: #7fa9d8 !important;
        }


        /* =====================================================
           BRAND
        ===================================================== */

        .brand-row {
            display: flex;
            align-items: center;
            gap: 12px;
        }


        .brand-image {
            width: 42px;
            height: 42px;
            object-fit: contain;
            border-radius: 12px;
        }


        .brand-logo {
            width: 42px;
            height: 42px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 12px;

            background:
                linear-gradient(
                    135deg,
                    #4e9cff,
                    #7668ff
                );

            color: white;
            font-size: 21px;
            font-weight: 800;

            box-shadow:
                0 8px 25px rgba(74,120,255,0.3);
        }


        .brand-name {
            color: #ffffff;
            font-size: 15px;
            font-weight: 800;
            line-height: 1.2;
        }


        .brand-subtitle {
            color: #8da9ca;
            font-size: 10px;
            margin-top: 3px;
        }


        /* =====================================================
           SIDEBAR NAVIGATION
        ===================================================== */

        section[data-testid="stSidebar"]
        div[role="radiogroup"] {
            gap: 7px;
        }


        section[data-testid="stSidebar"]
        div[role="radiogroup"] label {
            border-radius: 12px;
            padding: 9px 12px;
            transition: 0.2s ease;
        }


        section[data-testid="stSidebar"]
        div[role="radiogroup"] label:hover {
            background: rgba(95,150,255,0.12);
        }


        section[data-testid="stSidebar"]
        div[role="radiogroup"] label[data-checked="true"] {
            background:
                linear-gradient(
                    90deg,
                    rgba(75,143,255,0.22),
                    rgba(113,102,255,0.15)
                );

            border: 1px solid rgba(104,159,255,0.18);
        }


        /* =====================================================
           SIDEBAR ACTIVITY
        ===================================================== */

        .activity-sidebar-title {
            margin-top: 32px;
            margin-bottom: 14px;

            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.5px;

            color: #7897bd;
            text-transform: uppercase;
        }


        .activity-item {
            padding: 8px 0;

            font-size: 11px;
            color: #9eb5d1;

            display: flex;
            align-items: center;
            gap: 8px;
        }


        .activity-dot {
            width: 6px;
            height: 6px;

            border-radius: 50%;

            background: #63b7ff;

            box-shadow:
                0 0 10px rgba(99,183,255,0.8);
        }


        /* =====================================================
           TOP SEARCH
        ===================================================== */

        .top-search {
            width: 100%;
            height: 46px;

            display: flex;
            align-items: center;

            padding: 0 18px;

            border-radius: 14px;

            background: rgba(255,255,255,0.76);

            border: 1px solid rgba(88,128,190,0.13);

            box-shadow:
                0 10px 30px rgba(49,82,135,0.07);

            color: #7890b0;
            font-size: 13px;
        }


        .top-search-icon {
            font-size: 21px;
            margin-right: 10px;
            color: #5478b5;
        }


        .online-box {
            height: 46px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 14px;

            background: rgba(255,255,255,0.78);

            border: 1px solid rgba(88,128,190,0.13);

            color: #31547d;

            font-size: 12px;
            font-weight: 700;

            box-shadow:
                0 10px 30px rgba(49,82,135,0.07);
        }


        .online-dot {
            width: 8px;
            height: 8px;

            border-radius: 50%;

            background: #31c77a;

            margin-right: 8px;

            box-shadow:
                0 0 10px rgba(49,199,122,0.7);
        }


        /* =====================================================
           HERO
        ===================================================== */

        .hero-section {
            position: relative;

            min-height: 510px;

            display: grid;
            grid-template-columns: 1fr 0.9fr;

            gap: 20px;

            padding: 42px 45px;

            border-radius: 32px;

            overflow: hidden;

            background:
                radial-gradient(
                    circle at 78% 50%,
                    rgba(120,181,255,0.24),
                    transparent 33%
                ),
                linear-gradient(
                    135deg,
                    #116bcf 0%,
                    #245bd3 45%,
                    #4c55d9 100%
                );

            box-shadow:
                0 25px 65px rgba(34,82,160,0.20);
        }


        .hero-section::before {
            content: "";

            position: absolute;

            width: 420px;
            height: 420px;

            right: -150px;
            top: -180px;

            border-radius: 50%;

            border: 1px solid rgba(255,255,255,0.13);
        }


        .hero-section::after {
            content: "";

            position: absolute;

            width: 580px;
            height: 580px;

            right: -250px;
            bottom: -330px;

            border-radius: 50%;

            border: 1px solid rgba(255,255,255,0.08);
        }


        .hero-left {
            position: relative;
            z-index: 5;

            display: flex;
            flex-direction: column;
            justify-content: center;
        }


        .hero-badge {
            width: fit-content;

            padding: 7px 13px;

            border-radius: 100px;

            background: rgba(255,255,255,0.12);

            border: 1px solid rgba(255,255,255,0.15);

            color: #d8eeff;

            font-size: 10px;
            font-weight: 800;

            letter-spacing: 1.4px;
        }


        .hero-badge-dot {
            display: inline-block;

            width: 7px;
            height: 7px;

            border-radius: 50%;

            background: #78d4ff;

            margin-right: 7px;
        }


        .hero-title {
            margin: 22px 0 14px;

            color: white;

            font-size: 53px;
            line-height: 1.04;

            font-weight: 850;

            letter-spacing: -2px;
        }


        .hero-title span {
            color: #b8e3ff;
        }


        .hero-description {
            max-width: 590px;

            color: rgba(239,248,255,0.82);

            font-size: 14px;
            line-height: 1.75;

            margin-bottom: 24px;
        }


        .hero-buttons {
            display: flex;
            gap: 12px;
            align-items: center;
        }


        .hero-primary-button,
        .hero-secondary-button {
            padding: 12px 18px;

            border-radius: 12px;

            font-size: 12px;
            font-weight: 800;
        }


        .hero-primary-button {
            background: white;
            color: #245bcf;

            box-shadow:
                0 10px 25px rgba(0,0,0,0.12);
        }


        .hero-secondary-button {
            color: white;

            background: rgba(255,255,255,0.09);

            border:
                1px solid rgba(255,255,255,0.17);
        }


        .hero-trust {
            display: flex;
            flex-wrap: wrap;

            gap: 18px;

            margin-top: 27px;
        }


        .trust-item {
            color: rgba(239,248,255,0.72);

            font-size: 10px;
        }


        .trust-item span {
            color: #91e1ff;
            font-weight: 900;
            margin-right: 4px;
        }


        /* =====================================================
           AI SCENE
        ===================================================== */

        .hero-right {
            position: relative;
            z-index: 3;

            min-height: 420px;

            display: flex;
            align-items: center;
            justify-content: center;
        }


        .ai-scene {
            position: relative;

            width: 100%;
            height: 430px;

            display: flex;
            align-items: center;
            justify-content: center;

            overflow: visible;
        }


        /* =====================================================
           ROBOT
        ===================================================== */

        .skyhigh-robot {
            position: absolute;

            left: 50%;
            top: 50%;

            transform: translate(-50%, -50%);

            width: 330px;
            height: 330px;

            display: flex;
            align-items: center;
            justify-content: center;

            z-index: 4;
        }


        .skyhigh-robot img {
            width: 100%;
            height: 100%;

            object-fit: contain;

            display: block;

            filter:
                drop-shadow(
                    0 20px 30px rgba(0,0,0,0.20)
                );
        }


        .robot-glow {
            position: absolute;

            width: 210px;
            height: 90px;

            left: 50%;
            bottom: 20px;

            transform: translateX(-50%);

            border-radius: 50%;

            background:
                radial-gradient(
                    ellipse,
                    rgba(107,218,255,0.34),
                    transparent 70%
                );

            filter: blur(10px);

            z-index: -1;
        }


        .robot-fallback {
            font-size: 120px;
        }


        /* =====================================================
           ORBITS
        ===================================================== */

        .orbit {
            position: absolute;

            left: 50%;
            top: 50%;

            transform: translate(-50%, -50%);

            border-radius: 50%;

            border: 1px solid rgba(190,229,255,0.22);

            pointer-events: none;
        }


        .orbit-one {
            width: 360px;
            height: 220px;

            transform:
                translate(-50%, -50%)
                rotate(-12deg);
        }


        .orbit-two {
            width: 410px;
            height: 270px;

            transform:
                translate(-50%, -50%)
                rotate(42deg);
        }


        .orbit-three {
            width: 450px;
            height: 320px;

            transform:
                translate(-50%, -50%)
                rotate(-38deg);
        }


        /* =====================================================
           FLOATING CARDS
        ===================================================== */

        .float-card {
            position: absolute;

            z-index: 7;

            min-width: 170px;

            padding: 11px 14px;

            display: flex;
            align-items: center;

            gap: 10px;

            border-radius: 15px;

            background:
                rgba(255,255,255,0.94);

            border:
                1px solid rgba(255,255,255,0.75);

            box-shadow:
                0 18px 35px rgba(15,48,108,0.20);

            backdrop-filter: blur(12px);
        }


        .float-one {
            left: 0;
            top: 68px;
        }


        .float-two {
            right: 0;
            top: 78px;
        }


        .float-three {
            left: 8px;
            bottom: 55px;
        }


        .float-four {
            right: 2px;
            bottom: 45px;
        }


        .hero-action-icon {
            width: 34px;
            height: 34px;

            object-fit: contain;

            display: block;
        }


        .float-card-text {
            display: flex;
            flex-direction: column;
        }


        .float-label {
            color: #18345d;

            font-size: 10px;
            font-weight: 800;

            white-space: nowrap;
        }


        .float-small {
            margin-top: 3px;

            color: #7a91b1;

            font-size: 8px;
        }


        /* =====================================================
           SECTION HEADINGS
        ===================================================== */

        .section-heading {
            display: flex;
            justify-content: space-between;
            align-items: end;

            margin-top: 34px;
            margin-bottom: 16px;
        }


        .section-kicker {
            color: #6685ad;

            font-size: 9px;
            font-weight: 800;

            letter-spacing: 1.6px;

            margin-bottom: 4px;
        }


        .section-title {
            color: #122d54;

            font-size: 21px;
            font-weight: 850;
        }


        .section-description {
            color: #7890ad;

            font-size: 11px;
        }


        /* =====================================================
           KPI CARDS
        ===================================================== */

        .kpi-card {
            min-height: 105px;

            display: flex;
            align-items: center;

            gap: 14px;

            padding: 18px;

            border-radius: 18px;

            background:
                rgba(255,255,255,0.78);

            border:
                1px solid rgba(91,128,180,0.10);

            box-shadow:
                0 15px 35px rgba(45,75,125,0.07);

            backdrop-filter: blur(10px);
        }


        .kpi-icon {
            width: 44px;
            height: 44px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 13px;

            background:
                linear-gradient(
                    135deg,
                    #dceeff,
                    #e8e5ff
                );

            color: #416fcb;

            font-size: 20px;
            font-weight: 800;
        }


        .kpi-label {
            color: #7b91ad;

            font-size: 10px;
            font-weight: 600;
        }


        .kpi-value {
            margin-top: 4px;

            color: #17345f;

            font-size: 25px;
            font-weight: 850;
        }


        /* =====================================================
           FEATURE CARDS
        ===================================================== */

        .feature-card {
            min-height: 150px;

            padding: 20px;

            border-radius: 18px;

            background:
                rgba(255,255,255,0.70);

            border:
                1px solid rgba(91,128,180,0.10);

            box-shadow:
                0 14px 30px rgba(45,75,125,0.055);
        }


        .feature-icon {
            width: 40px;
            height: 40px;

            display: flex;
            align-items: center;
            justify-content: center;

            margin-bottom: 14px;

            border-radius: 12px;

            background:
                linear-gradient(
                    135deg,
                    #e0f2ff,
                    #eae6ff
                );

            color: #426fd0;

            font-size: 18px;
            font-weight: 800;
        }


        .feature-title {
            color: #17345d;

            font-size: 12px;
            font-weight: 850;

            margin-bottom: 7px;
        }


        .feature-text {
            color: #7b8fa9;

            font-size: 10px;
            line-height: 1.55;
        }


        /* =====================================================
           DASHBOARD PANELS
        ===================================================== */

        .dashboard-panel {
            padding: 22px;

            border-radius: 20px;

            background:
                rgba(255,255,255,0.76);

            border:
                1px solid rgba(91,128,180,0.10);

            box-shadow:
                0 15px 35px rgba(45,75,125,0.06);
        }


        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: start;

            margin-bottom: 20px;
        }


        .panel-title {
            color: #18345d;

            font-size: 14px;
            font-weight: 850;
        }


        .panel-subtitle {
            margin-top: 4px;

            color: #8498b1;

            font-size: 9px;
        }


        .panel-status {
            padding: 5px 9px;

            border-radius: 20px;

            background: #e4f8ed;

            color: #28a866;

            font-size: 8px;
            font-weight: 800;
        }


        /* =====================================================
           RECENT ACTIVITY
        ===================================================== */

        .recent-row {
            display: grid;

            grid-template-columns:
                40px 1fr auto;

            align-items: center;

            gap: 12px;

            padding: 13px 0;

            border-bottom:
                1px solid rgba(91,128,180,0.08);
        }


        .recent-row:last-child {
            border-bottom: none;
        }


        .recent-icon {
            width: 36px;
            height: 36px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 11px;

            background: #edf5ff;

            font-size: 15px;
        }


        .recent-name {
            color: #29486f;

            font-size: 10px;
            font-weight: 800;
        }


        .recent-description {
            margin-top: 3px;

            color: #8a9cb4;

            font-size: 9px;
        }


        .recent-time {
            color: #99a9bc;

            font-size: 8px;
        }


        /* =====================================================
           MATCH PANEL
        ===================================================== */

        .match-panel {
            text-align: center;
        }


        .match-score-circle {
            width: 145px;
            height: 145px;

            margin: 10px auto 20px;

            border-radius: 50%;

            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;

            background:
                radial-gradient(
                    circle,
                    #ffffff 48%,
                    transparent 49%
                ),
                conic-gradient(
                    #4d83e8 0deg,
                    #7b6cf0 313deg,
                    #e7edf7 313deg
                );

            box-shadow:
                0 12px 30px rgba(61,105,190,0.12);
        }


        .match-score-number {
            color: #244c87;

            font-size: 29px;
            font-weight: 900;
        }


        .match-score-label {
            color: #8497af;

            font-size: 8px;
            margin-top: 2px;
        }


        .match-stats {
            display: grid;

            grid-template-columns:
                repeat(3, 1fr);

            gap: 8px;
        }


        .match-stat {
            padding: 10px;

            border-radius: 12px;

            background: #f5f8fc;
        }


        .match-stat strong {
            display: block;

            color: #31588f;

            font-size: 15px;
        }


        .match-stat span {
            display: block;

            color: #91a1b5;

            font-size: 8px;

            margin-top: 3px;
        }


        /* =====================================================
           FOOTER
        ===================================================== */

        .footer {
            margin-top: 35px;
            padding: 18px 0 8px;

            text-align: center;

            color: #8ca0b8;

            font-size: 9px;
        }


        /* =====================================================
           STREAMLIT CLEANUP
        ===================================================== */

        div[data-testid="stDecoration"] {
            display: none;
        }


        #MainMenu {
            visibility: hidden;
        }


        footer {
            visibility: hidden;
        }


        /* =====================================================
           RESPONSIVE
        ===================================================== */

        @media (max-width: 1100px) {

            .hero-section {
                grid-template-columns: 1fr;
            }

            .hero-right {
                min-height: 430px;
            }

        }


        @media (max-width: 750px) {

            .hero-section {
                padding: 30px 25px;
            }

            .hero-title {
                font-size: 40px;
            }

            .ai-scene {
                transform: scale(0.82);
            }

            .float-one {
                left: -5px;
            }

            .float-two {
                right: -5px;
            }

            .float-three {
                left: -5px;
            }

            .float-four {
                right: -5px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )