import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from utils.db import list_cities, get_ordinance
from utils.llm import analyze_listing
from utils.pdf import create_pdf
import uuid
import urllib.parse # Import for safe URL encoding

# ---------- WHITE-ONLY THEME + HIDE CHROME ----------
hide_css = """
<style>
/* ---- lock white background ---- */
html,body,.stApp{background:#ffffff !important;color:#0f172a !important;}

/* ---- hide Streamlit header + fork + footer ---- */
header[data-testid="stHeader"]{display:none;}
div[data-testid="stDecoration"]{display:none;}
footer{visibility:hidden;height:0;}

/* ---- remove top padding gap ---- */
.stMain > div:first-child{padding-top:0 !important;}
</style>
"""
st.markdown(hide_css, unsafe_allow_html=True)

# # ---------- HIDE STREAMLIT CHROME ----------
# hide_streamlit_style = """
# <style>
# /* Hide the entire header block */
# header[data-testid="stHeader"] {display: none;}
# /* Hide fork-me ribbon */
# div[data-testid="stDecoration"] {display: none;}
# /* Hide bottom “Made with Streamlit” */
# footer {visibility: hidden;height:0;}
# </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="PetClause AI",
    page_icon="🐾",
    layout="centered"
)

# ---------------------------
# Custom CSS for modern UI
# ---------------------------
st.markdown("""
<style>
/* Main Container */
.main {
    padding-top: 2rem;
}

/* Hero Title */
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.5rem;
}

.hero-sub {
    text-align: center;
    font-size: 1.1rem;
    opacity: 0.8;
    margin-bottom: 2.5rem;
}

/* Card */
.card {
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 1.8rem;
    border: 1px solid rgba(200, 200, 200, 0.35);
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
}

/* For dark mode */
[data-theme="dark"] .card {
    background: rgba(20,20,20,0.5);
    border-color: rgba(255,255,255,0.05);
}

/* Buttons */
.stButton button {
    width: 100%;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 1.05rem;
}

/* Result labels */
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 0.3rem;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>

/* --- FIX st.metric text visibility --- */
[data-testid="stMetricValue"], 
[data-testid="stMetricLabel"] {
    color: #0f172a !important;      /* dark navy */
    font-weight: 700 !important;
}

/* --- FIX st.warning visibility on white background --- */
div.stAlert {
    background-color: #fff4c2 !important;  /* stronger yellow */
    border-left: 5px solid #e0a800 !important;
    color: #3a2d00 !important;
    padding: 1rem !important;
    border-radius: 10px !important;
}

/* --- FIX st.info visibility (citations) --- */
div.stAlert.info {
    background-color: #e8f3ff !important;
    border-left: 5px solid #2b6cb0 !important;
    color: #0f1e33 !important;
    border-radius: 10px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# HERO SECTION
# ---------------------------
st.markdown("<h1 class='hero-title'>🐾 PetClause AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-sub'>AI-powered scanning for risky or illegal pet clauses — fast, accurate, and ordinance-aware.</p>",
            unsafe_allow_html=True)

# ---------------------------
# INPUT SECTION
# ---------------------------
with st.container():
    # st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("🔍 Scan Your Rental Listing")

    listing = st.text_area(
        "Paste your full listing text:",
        height=220,
        placeholder="Example: No pets allowed unless approved by landlord...",
    )

    city = st.selectbox(
        "Select your city:",
        ["Denver", "Austin", "Berlin"],  # update as db grows
    )

    scan_button = st.button("🚀 Scan for Pet Clause Compliance", type="primary")


# ---------------------------
# ACTION
# ---------------------------
if scan_button:

    if not listing.strip():
        st.error("🚫 Please paste your listing before scanning.")
        st.stop()

    ordinance = get_ordinance(city)
    if not ordinance:
        st.error("City ordinance missing from database.")
        st.stop()

    with st.spinner("Analyzing your listing with AI…"):
        result = analyze_listing(listing, ordinance)

    # -------------------------
    # RESULTS SECTION
    # -------------------------
    # st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📊 Analysis Summary</div>", unsafe_allow_html=True)
    st.metric("Confidence Score", f"{result['confidence']}%")

    # Risky phrases
    st.markdown("<div class='section-title'>⚠️ Risky Phrases Detected</div>", unsafe_allow_html=True)
    if result["risky_phrases"]:
        for r in result["risky_phrases"]:
            st.warning(r)
    else:
        st.success("No risky phrases found — looks compliant!")

    # Fixed listing
    st.markdown("<div class='section-title'>🛠️ Improved / Fixed Listing</div>", unsafe_allow_html=True)
    st.code(result["fixed_listing"], language="markdown")

    # Citations
    st.markdown("<div class='section-title'>📚 Relevant Citations</div>", unsafe_allow_html=True)
    if result["citations"]:
        for ctn in result["citations"]:
            st.info(ctn)
    else:
        st.info("No citations returned.")


    # -------------------------
    # PDF DOWNLOAD SECTION
    # -------------------------
    # st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("📄 Download Your Compliance Report")

    file_id = str(uuid.uuid4())[:8]
    pdf_path = f"report_{file_id}.pdf"
    create_pdf(pdf_path, listing, result["fixed_listing"], result["risky_phrases"], result["citations"])

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇️ Download PDF Report",
            f,
            file_name="PetClause_Report.pdf",
            type="primary"
        )
    
    # -------------------------
    # SUPPORT / BUY ME A COFFEE (REQUESTED ADDITION)
    # -------------------------
    st.markdown("---")
    st.markdown("#### ☕ Unlock more features – pay what you want")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.link_button("$0 (free)", "https://www.buymeacoffee.com/petclauseai/e/126105", use_container_width=True)
    with c2:
        st.link_button("$9", "https://www.buymeacoffee.com/petclauseai/e/126104", use_container_width=True)
    with c3:
        st.link_button("$19 (unlimited month)", "https://www.buymeacoffee.com/petclauseai/e/126103", use_container_width=True)

    st.markdown("---")
    st.markdown("💙 **Help other landlords** – share this scan:")
    
    # Encode the share text for the URL
    share_text = f"Just checked my rental ad with PetClause AI – caught {len(result['risky_phrases'])} risky pet clauses in 10s!"
    encoded_share_text = urllib.parse.quote_plus(share_text)
    
    st.link_button("🐦 Share on Twitter", f"https://twitter.com/intent/tweet?text={encoded_share_text}&url=https://petclauseai.streamlit.app", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# GLOBAL FOOTER (Old coffee button removed/moved)
# -------------------------
st.markdown("Disclaimer: This tool provides automated compliance guidance only. It is not legal advice. Always verify with a licensed attorney.", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)