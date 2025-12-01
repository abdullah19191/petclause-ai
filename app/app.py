# app.py — UPDATED WITH LOGO + FIXED WARNING CSS (Dec 2025)
import os
import streamlit as st
import uuid
import urllib.parse
from utils.db import get_ordinance
from utils.llm import analyze_listing
from utils.pdf import create_pdf





# ====================== SESSION STATE ======================
if "scan_completed" not in st.session_state:
    st.session_state.scan_completed = False
if "result" not in st.session_state:
    st.session_state.result = None
if "paid" not in st.session_state:
    st.session_state.paid = False
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:12]
if "last_listing" not in st.session_state:
    st.session_state.last_listing = ""
if "current_city" not in st.session_state:
    st.session_state.current_city = "Denver"


# ====================== DEV MODE TOGGLE (LOCAL TESTING ONLY) ======================
# if st.secrets.get("DEV_MODE", False):
#     if st.button("🔓 Developer Unlock (local only)", type="secondary", use_container_width=True):
#         st.session_state.paid = True
#         st.success("Developer mode enabled — premium unlocked!")
#         st.rerun()

# ====================== PAYMENT SUCCESS CHECK ======================
query_params = st.query_params
if query_params.get("paid") == "1" and query_params.get("session") == st.session_state.session_id:
    st.session_state.paid = True
    st.query_params.clear()
    st.success("Payment confirmed! Full report unlocked below")
    st.rerun()

# ====================== STYLING ======================
st.markdown("""
<style>
    html, body, .stApp {
        background:#ffffff !important;
        color:#0f172a !important;
    }
    header[data-testid="stHeader"], footer, div[data-testid="stDecoration"] {
        display:none !important;
    }

    /* LOGO + HERO */
    .hero-container {
        text-align:center;
        margin-top:1rem;
        margin-bottom:1rem;
    }
    .hero-title {
        font-size:2.8rem;
        font-weight:800;
        margin-top:0.3rem;
        margin-bottom:0.3rem;
    }
    .hero-sub {
        font-size:1.25rem;
        opacity:0.9;
        margin-bottom:2.2rem;
    }

    /* Section headers */
    .section-title {
        font-size:1.5rem;
        font-weight:700;
        margin:2.2rem 0 0.8rem 0;
    }

    /* Paywall teaser */
    .teaser {
        background:#fff8e1;
        padding:1.5rem;
        border-radius:12px;
        border-left:6px solid #f59e0b;
        font-size:1.05rem;
        margin-top:1rem;
    }

    /* ===== CRUCIAL FIX: ALERT TEXT VISIBILITY ===== */
    div.stAlert, div.stAlert * {
        color:#222 !important;
        font-weight:600 !important;
    }
    div.stAlert.warning {
        background:#fff3b3 !important;
        border-left:6px solid #e6b700 !important;
    }
    div.stAlert.info {
        background:#d6ecff !important;
        border-left:6px solid #3b82f6 !important;
    }
            /* Custom CSS (Add this to your existing <style> block) */

/* Target the primary button specifically */
.stButton button[kind="primary"] {
    /* Background color: Yellowish-Golden */
    background-color: #FFC72C !important; 
    /* Border color: Slightly darker golden */
    border-color: #FFC72C !important;
    /* Text color: Black for high contrast */
    color: #000000 !important; 
    font-weight: 700;
    /* Subtle box shadow for depth */
    box-shadow: 0 4px 12px rgba(255, 199, 44, 0.5); 
    transition: all 0.2s ease-in-out;
}

.stButton button[kind="primary"]:hover {
    /* Slightly darker on hover */
    background-color: #e6b327 !important; 
}

</style>
""", unsafe_allow_html=True)

# ====================== LOGO + HERO ======================
st.markdown("""
<div class="hero-container">
    <img src="https://static.vecteezy.com/system/resources/previews/049/249/362/non_2x/cute-and-friendly-cartoon-dog-logo-design-perfect-for-pet-businesses-animal-shelters-dog-training-or-any-brand-needing-a-playful-and-approachable-mascot-free-vector.jpg" width="90" style="margin-bottom: 5px;" />
    <div class="hero-title">🐾 PetClause AI</div>
    <div class="hero-sub">Catch illegal pet clauses in 10 seconds • Avoid $4,150+ fines • Court-ready PDF</div>
</div>
""", unsafe_allow_html=True)

# ====================== INPUT ======================
st.subheader("Scan Your Rental Listing")

listing = st.text_area(
    "Paste your full listing text:",
    height=230,
    value=st.session_state.last_listing,
    placeholder="Example: No aggressive breeds • $500 pet deposit • No dogs over 40 lbs..."
)

city = st.selectbox("Select city:", [
    "Denver", "Austin", "Seattle", "Portland", "Atlanta",
    "Chicago", "Boston", "Berlin", "Miami", "San Francisco"
], index=0)

scan_button = st.button("🚀 Scan for Pet Clause Compliance", type="primary", use_container_width=True)
# ====================== RUN ANALYSIS ======================
if scan_button:
    if not listing.strip():
        st.error("Please paste your listing first.")
        st.stop()

    ordinance = get_ordinance(city)
    if not ordinance:
        st.error(f"Ordinance for {city} coming soon! Check back in 24h.")
        st.stop()

    with st.spinner("AI checking against local + federal law…"):
        result = analyze_listing(listing, ordinance)
        st.session_state.result = result
        st.session_state.scan_completed = True
        st.session_state.last_listing = listing
        st.session_state.current_city = city
        st.session_state.paid = False  
    st.rerun()

# ====================== SHOW RESULTS ======================
if st.session_state.scan_completed and st.session_state.result:
    r = st.session_state.result
    score = r.get('confidence', 0)
    risks = len(r.get("risky_phrases", []))

    # Define color based on score (using hex codes)
    if score >= 80:
       color = "#4CAF50"  # Green
    elif score >= 50:
       color = "#FF9800"  # Orange/Amber
    else:
       color = "#F44336"  # Red

    html_score = f"""
    <div style="
    background-color: {color};
    color: white;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    font-size: 1.5em;
    font-weight: bold;
    margin-bottom: 10px;
    ">
    {score}%
    </div>
    <p style="text-align: center; font-size: 0.9em;">Compliance Score</p>
    """

    html_risks = f"""
    <div style="
    background-color: {"#780800" if risks > 0 else "#1A9C1E"};
    color: white;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    font-size: 1.5em;
    font-weight: bold;
    margin-bottom: 10px;
    ">
    {risks}
    </div>
    <p style="text-align: center; font-size: 0.9em;">Risks Found</p>
    """
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(html_score, unsafe_allow_html=True)
    with col2:
        st.markdown(html_risks, unsafe_allow_html=True)
    # RISKY PHRASES
    st.markdown("<div class='section-title'>Risky / Illegal Phrases</div>", unsafe_allow_html=True)
    if r.get("risky_phrases"):
        for phrase in r["risky_phrases"]:
            st.warning(phrase)
    else:
        st.success("No major violations detected — looks compliant!")

    # FIXED LISTING
    st.markdown("<div class='section-title'>Compliant Version (Fixed)</div>", unsafe_allow_html=True)

    if st.session_state.paid:
        st.code(r["fixed_listing"], language="text")
    else:
        teaser = "\n".join(r["fixed_listing"].strip().split("\n")[:2]) if r["fixed_listing"] else "Pets welcome with the following restrictions..."
        st.code(teaser + "\n\n... [rest hidden — unlock full version below]", language="text")

        st.markdown("""
        <div class='teaser'>
            <strong>Full compliant rewrite ready!</strong><br>
            Includes precise legal wording + court-ready PDF with citations.<br>
            One-time payment • Used by landlords in 30+ cities.
        </div>
        """, unsafe_allow_html=True)

    # PAYWALL
    if not st.session_state.paid:
        st.markdown("---")
        st.markdown("#### Unlock Full Compliant Listing + PDF Report")
        

        lemon_link = (
            "https://petclause.lemonsqueezy.com/checkout/buy/YOUR_PRODUCT_ID?"
            f"checkout[custom][session_id]={st.session_state.session_id}&media=0&checkout[email]=true"
        )

        # st.markdown(f"""
        # <a href="{lemon_link}" target="_blank">
        #     <button style="background:#1d4ed8; color:white; padding:1.2rem; font-size:1.3rem;
        #                    border:none; border-radius:12px; width:100%; cursor:pointer;
        #                    box-shadow:0 4px 12px rgba(0,0,0,0.15);">
        #         Unlock Full Report + PDF — Only $19
        #     </button>
        # </a>
        # """, unsafe_allow_html=True)
        st.markdown(f"""
        <a href="{lemon_link}" target="_blank">
            <button style="background:#1d4ed8; color:white; padding:1.2rem; font-size:1.3rem; font-weight:bold; 
                           border:none; border-radius:12px; width:100%; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
                Unlock Full Report + PDF — Only $19 (one-time, no subscription)
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.caption("Instant access • 60-day money-back • No subscription")

    # FULL ACCESS
    if st.session_state.paid:
        st.markdown("---")

        if r.get("citations"):
            st.markdown("<div class='section-title'>Legal Sources & Citations</div>", unsafe_allow_html=True)
            for c in r["citations"]:
                st.info(c)

        # PDF
        st.markdown("#### Download Your Court-Ready Report")
        os.makedirs("reports", exist_ok=True)
        pdf_path = f"reports/report_{uuid.uuid4().hex[:8]}.pdf"

        create_pdf(
            pdf_path,
            st.session_state.last_listing,
            r["fixed_listing"],
            r.get("risky_phrases", []),
            r.get("citations", []),
            city=st.session_state.current_city
        )


        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download Full PDF Report",
                f,
                file_name=f"PetClause_Report_{st.session_state.current_city}_{uuid.uuid4().hex[:6]}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        st.success("You now have a fully compliant, court-defendable pet policy!")

    # SHARE
    st.markdown("---")
    risks_found = len(r.get("risky_phrases", []))
    share_text = (
        f"Just scanned my rental listing with @PetClauseAI — caught {risks_found} illegal pet clauses!"
    )
    st.link_button("Share on X",
        f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}&url=https://petclauseai.streamlit.app",
        use_container_width=True)

    st.caption("⚖️ Automated guidance only; not legal advice.")


# import os
# from dotenv import load_dotenv
# load_dotenv()
# import streamlit as st
# from utils.db import list_cities, get_ordinance
# from utils.llm import analyze_listing
# from utils.pdf import create_pdf
# import uuid
# import urllib.parse

# # ---------- WHITE-ONLY THEME + HIDE STREAMLIT CHROME ----------
# st.markdown("""
# <style>
# html,body,.stApp { background:#ffffff !important; color:#0f172a !important; }

# /* hide header + decoration + footer */
# header[data-testid="stHeader"] {display:none;}
# div[data-testid="stDecoration"] {display:none;}
# footer {visibility:hidden;height:0;}

# /* remove weird top padding */
# .stMain > div:first-child { padding-top:0 !important; }
# </style>
# """, unsafe_allow_html=True)


# # ---------------------------
# # Page configuration
# # ---------------------------
# st.set_page_config(
#     page_title="PetClause AI",
#     page_icon="🐾",
#     layout="centered"
# )

# # ---------------------------
# # Main UI Theme
# # ---------------------------
# st.markdown("""
# <style>

# /* HERO */
# .hero-title {
#     font-size: 2.4rem;
#     font-weight: 800;
#     text-align: center;
#     margin-bottom: 0.5rem;
# }

# .hero-sub {
#     text-align: center;
#     font-size: 1.1rem;
#     opacity: 0.8;
#     margin-bottom: 2.5rem;
# }

# /* Buttons */
# .stButton button {
#     width: 100%;
#     border-radius: 10px;
#     padding: 0.75rem 1rem;
#     font-size: 1.05rem;
# }

# /* Section Titles */
# .section-title {
#     font-size: 1.3rem;
#     font-weight: 700;
#     margin-top: 2rem;
#     margin-bottom: 0.3rem;
# }

# /* ---- FIX METRIC VISIBILITY ---- */
# [data-testid="stMetricValue"],
# [data-testid="stMetricLabel"] {
#     color: #0f172a !important;
#     font-weight: 700 !important;
# }

# /* ---- FIX ALERT (WARNING + INFO) TEXT VISIBILITY ---- */

# /* general stAlert rules */
# div.stAlert {
#     padding: 1rem !important;
#     border-radius: 12px !important;
# }

# /* Yellow warnings (risky phrases) */
# div.stAlert.warning {
#     background-color: #ffe98a !important;
#     border-left: 6px solid #e6b700 !important;
# }
# div.stAlert.warning p {
#     color: #3a2d00 !important;
#     font-weight: 600 !important;
# }

# /* Blue info (citations) */
# div.stAlert.info {
#     background-color: #d6ecff !important;
#     border-left: 6px solid #4a90e2 !important;
# }
# div.stAlert.info p {
#     color: #0f172a !important;
#     font-weight: 600 !important;
# }

# </style>
# """, unsafe_allow_html=True)


# # ---------------------------
# # HERO SECTION
# # ---------------------------
# st.markdown("<h1 class='hero-title'>🐾 PetClause AI</h1>", unsafe_allow_html=True)
# st.markdown("<p class='hero-sub'>AI-powered scanning for risky or illegal pet clauses — fast, accurate, and ordinance-aware.</p>", unsafe_allow_html=True)


# # ---------------------------
# # INPUT SECTION
# # ---------------------------
# st.subheader("🔍 Scan Your Rental Listing")

# listing = st.text_area(
#     "Paste your full listing text:",
#     height=220,
#     placeholder="Example: No pets allowed unless approved by landlord..."
# )

# city = st.selectbox(
#     "Select your city:",
#     ["Denver", "Austin", "Berlin"]
# )

# scan_button = st.button("🚀 Scan for Pet Clause Compliance", type="primary")


# # ---------------------------
# # ACTION
# # ---------------------------
# if scan_button:

#     if not listing.strip():
#         st.error("🚫 Please paste your listing before scanning.")
#         st.stop()

#     ordinance = get_ordinance(city)
#     if not ordinance:
#         st.error("City ordinance missing from database.")
#         st.stop()

#     with st.spinner("Analyzing your listing with AI…"):
#         result = analyze_listing(listing, ordinance)

#     # -------------------------
#     # RESULTS
#     # -------------------------
#     st.markdown("<div class='section-title'>📊 Analysis Summary</div>", unsafe_allow_html=True)
#     st.metric("Confidence Score", f"{result['confidence']}%")

#     # Risky phrases
#     st.markdown("<div class='section-title'>⚠️ Risky Phrases Detected</div>", unsafe_allow_html=True)
#     if result["risky_phrases"]:
#         for r in result["risky_phrases"]:
#             st.info(r)
#     else:
#         st.success("No risky phrases found — looks compliant!")

#     # Fixed listing
#     st.markdown("<div class='section-title'>🛠️ Improved / Fixed Listing</div>", unsafe_allow_html=True)
#     st.code(result["fixed_listing"], language="markdown")

#     # Citations
#     st.markdown("<div class='section-title'>📚 Relevant Citations</div>", unsafe_allow_html=True)
#     if result["citations"]:
#         for ctn in result["citations"]:
#             st.info(ctn)
#     else:
#         st.info("No citations returned.")

#     # -------------------------
#     # PDF DOWNLOAD
#     # -------------------------
#     st.subheader("📄 Download Your Compliance Report")

#     file_id = str(uuid.uuid4())[:8]
#     pdf_path = f"report_{file_id}.pdf"

#     create_pdf(pdf_path, listing, result["fixed_listing"], result["risky_phrases"], result["citations"])

#     with open(pdf_path, "rb") as f:
#         st.download_button(
#             "⬇️ Download PDF Report",
#             f,
#             file_name="PetClause_Report.pdf",
#             type="primary"
#         )

#     # -------------------------
#     # SUPPORT
#     # -------------------------
#     st.markdown("---")
#     st.markdown("#### ☕ Unlock more features – pay what you want")

#     c1, c2, c3 = st.columns(3)
#     with c1:
#         st.link_button("$0 (free)", "https://www.buymeacoffee.com/petclauseai/e/126105", use_container_width=True)
#     with c2:
#         st.link_button("$9", "https://www.buymeacoffee.com/petclauseai/e/126104", use_container_width=True)
#     with c3:
#         st.link_button("$19 (unlimited month)", "https://www.buymeacoffee.com/petclauseai/e/126103", use_container_width=True)

#     st.markdown("---")
#     st.markdown("💙 **Help other landlords** – share this scan:")

#     share_text = f"Just checked my rental ad with PetClause AI – caught {len(result['risky_phrases'])} risky pet clauses in 10s!"
#     encoded_share_text = urllib.parse.quote_plus(share_text)

#     st.link_button(
#         "🐦 Share on Twitter",
#         f"https://twitter.com/intent/tweet?text={encoded_share_text}&url=https://petclauseai.streamlit.app",
#         use_container_width=True
#     )


# # ---------------------------
# # FOOTER DISCLAIMER
# # ---------------------------
# st.markdown("Disclaimer: This tool provides automated compliance guidance only. It is not legal advice. Always verify with a licensed attorney.")
