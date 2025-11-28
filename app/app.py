import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from utils.db import list_cities, get_ordinance
from utils.llm import analyze_listing
from utils.pdf import create_pdf
import uuid
import urllib.parse

# ---------- WHITE-ONLY THEME + HIDE CHROME ----------
st.markdown("""
<style>
html,body,.stApp{background:#ffffff !important;color:#0f172a !important;}
header[data-testid="stHeader"]{display:none;}
div[data-testid="stDecoration"]{display:none;}
footer{visibility:hidden;height:0;}
.stMain > div:first-child{padding-top:0 !important;}
</style>
""", unsafe_allow_html=True)

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="PetClause AI", page_icon="🐾", layout="centered")

# ---------- THEME ----------
st.markdown("""
<style>
.hero-title{font-size:2.4rem;font-weight:800;text-align:center;margin-bottom:0.5rem;}
.hero-sub{text-align:center;font-size:1.1rem;opacity:0.8;margin-bottom:2.5rem;}
.stButton button{width:100%;border-radius:10px;padding:0.75rem 1rem;font-size:1.05rem;}
.section-title{font-size:1.3rem;font-weight:700;margin-top:2rem;margin-bottom:0.3rem;}

/* ---- FIX METRIC & ALERT VISIBILITY ---- */
[data-testid="stMetricValue"],[data-testid="stMetricLabel"]{color:#0f172a !important;font-weight:700 !important;}
div.stAlert{padding:1rem !important;border-radius:12px !important;}
div.stAlert.warning{background-color:#ffe98a !important;border-left:6px solid #e6b700 !important;}
div.stAlert.warning p{color:#3a2d00 !important;font-weight:600 !important;}
div.stAlert.info{background-color:#d6ecff !important;border-left:6px solid #4a90e2 !important;}
div.stAlert.info p{color:#0f172a !important;font-weight:600 !important;}
</style>
""", unsafe_allow_html=True)

# ---------- HERO ----------
st.markdown("<h1 class='hero-title'>🐾 PetClause AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-sub'>AI-powered scanning for risky or illegal pet clauses — fast, accurate, and ordinance-aware.</p>", unsafe_allow_html=True)

# ---------- INPUT ----------
st.subheader("🔍 Scan Your Rental Listing")
listing = st.text_area("Paste your full listing text:", height=220, placeholder="Example: No pets allowed unless approved by landlord...")
city = st.selectbox("Select your city:", ["Denver", "Austin", "Berlin"])
scan_button = st.button("🚀 Scan for Pet Clause Compliance", type="primary")

# ---------- ACTION ----------
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
    st.markdown("<div class='section-title'>📊 Analysis Summary</div>", unsafe_allow_html=True)
    st.metric("Confidence Score", f"{result['confidence']}%")
    st.markdown("<div class='section-title'>⚠️ Risky Phrases Detected</div>", unsafe_allow_html=True)
    if result["risky_phrases"]:
        for r in result["risky_phrases"]:
            st.warning(r)
    else:
        st.success("No risky phrases found — looks compliant!")
    st.markdown("<div class='section-title'>🛠️ Improved / Fixed Listing</div>", unsafe_allow_html=True)
    st.code(result["fixed_listing"], language="markdown")
    st.markdown("<div class='section-title'>📚 Relevant Citations</div>", unsafe_allow_html=True)
    if result["citations"]:
        for ctn in result["citations"]:
            st.info(ctn)
    else:
        st.info("No citations returned.")
    st.subheader("📄 Download Your Compliance Report")
    file_id = str(uuid.uuid4())[:8]
    pdf_path = f"report_{file_id}.pdf"
    create_pdf(pdf_path, listing, result["fixed_listing"], result["risky_phrases"], result["citations"])
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Download PDF Report", f, file_name="PetClause_Report.pdf", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("#### ☕ Unlock more features – pay what you want")
    c1, c2, c3 = st.columns(3)
    with c1: st.link_button("$0 (free)", "https://www.buymeacoffee.com/petclauseai/e/126105", use_container_width=True)
    with c2: st.link_button("$9", "https://www.buymeacoffee.com/petclauseai/e/126104", use_container_width=True)
    with c3: st.link_button("$19 (unlimited month)", "https://www.buymeacoffee.com/petclauseai/e/126103", use_container_width=True)
    share_text = f"Just checked my rental ad with PetClause AI – caught {len(result['risky_phrases'])} risky pet clauses in 10s!"
    encoded_share_text = urllib.parse.quote_plus(share_text)
    st.link_button("🐦 Share on Twitter", f"https://twitter.com/intent/tweet?text={encoded_share_text}&url=https://petclauseai.streamlit.app", use_container_width=True)
    st.markdown("---")
    st.markdown("Disclaimer: This tool provides automated compliance guidance only. It is not legal advice. Always verify with a licensed attorney.")