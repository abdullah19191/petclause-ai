# app.py — UPDATED WITH LOGO + FIXED WARNING CSS (Dec 2025)
import os
import streamlit as st
import uuid
import urllib.parse
from utils.db import get_ordinance
from utils.llm import analyze_listing
from utils.pdf import create_pdf



# # ---------------------------
# # Page configuration
# # ---------------------------
st.set_page_config(
    page_title="PetClause AI",
    page_icon="🐾",
    layout="centered"
)
# ====================== UNLOCK CHECK (LemonSqueezy) ======================

# query_params = st.query_params

# if query_params.get("paid") == "1" and query_params.get("order"):
#     st.session_state.paid = True
#     st.session_state.order = query_params.get("order")

#     # Clean URL (remove ?paid=1&order=XXXX)
#     st.query_params.clear()

#     st.rerun()



# ====================== SESSION ID ======================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:12]

# ====================== SESSION STATE ======================
if "scan_completed" not in st.session_state:
    st.session_state.scan_completed = False
if "result" not in st.session_state:
    st.session_state.result = None
if "paid" not in st.session_state:
    st.session_state.paid = False
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())[:12]
if "last_listing" not in st.session_state:
    st.session_state.last_listing = ""
if "current_city" not in st.session_state:
    st.session_state.current_city = "Denver"
if "order_identifier" not in st.session_state: # <-- Add a check for the order ID state
    st.session_state.order_identifier = None

query_params = st.query_params

if query_params.get("paid") == "1" and query_params.get("order"):
    # 1. Set flags in session state (this is what persists the access)
    st.session_state.paid = True
    st.session_state.order_identifier = query_params.get("order")

    # 2. Clean URL (remove ?paid=1&order=XXXX) AND RERUN
    # We clear the query params and force a rerun.
    # This must be the *last* thing in this block.
    st.query_params.clear()
    
    # st.rerun() is now optional as st.query_params.clear() forces one, 
    # but let's keep it for absolute certainty of the redirect behavior.
    st.rerun()

# ====================== DEV MODE TOGGLE (LOCAL TESTING ONLY) ======================
# if st.secrets.get("DEV_MODE", False):
#     if st.button("🔓 Developer Unlock (local only)", type="secondary", use_container_width=True):
#         st.session_state.paid = True
#         st.success("Developer mode enabled — premium unlocked!")
#         st.rerun()


# ---------- WHITE-ONLY THEME + HIDE STREAMLIT CHROME ----------
st.markdown("""
<style>
html,body,.stApp { background:#ffffff !important; color:#0f172a !important; }

/* hide header + decoration + footer */
header[data-testid="stHeader"] {display:none;}
div[data-testid="stDecoration"] {display:none;}
footer {visibility:hidden;height:0;}

/* remove weird top padding */
.stMain > div:first-child { padding-top:0 !important; }
</style>
""", unsafe_allow_html=True)




# ---------- UNLOCK CHECK (bullet-proof) ----------

# 1. Lemon-Squeezy passes ?paid=1&session=XXXX after payment


if query_params.get("paid") == "1" and query_params.get("order"):
    st.session_state.paid = True
    st.session_state.order = query_params.get("order")




# 2. Debug: show what Lemon passed (remove after test)
# if st.query_params.get("paid"):
#     st.write("DEBUG: Lemon passed", st.query_params)


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
        # st.session_state.paid = False  
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
        

        # st.write("DEBUG: Current session ID:", st.session_state.session_id)

        # lemon_link = (
        # f"https://petclauseai.lemonsqueezy.com/buy/634abe5c-e894-4d89-b32e-14bd46ba543c?"
        # f"checkout[custom][session]={st.session_state.session_id}&"
        # f"checkout[custom][paid]=1"
        # )
        lemon_link = "https://petclauseai.lemonsqueezy.com/checkout/buy/634abe5c-e894-4d89-b32e-14bd46ba543c"

        # st.markdown(f"""
        # <a href="{lemon_link}" target="_blank">
        #     <button style="background:#1d4ed8; color:white; padding:1.2rem; font-size:1.3rem;
        #                    border:none; border-radius:12px; width:100%; cursor:pointer;
        #                    box-shadow:0 4px 12px rgba(0,0,0,0.15);">
        #         Unlock Full Report + PDF — Only $19
        #     </button>
        # </a>
        # """, unsafe_allow_html=True)
        # st.markdown(f"""
        # <a href="{lemon_link}" target="_blank">
        #     <button style="background:#1d4ed8; color:white; padding:1.2rem; font-size:1.3rem; font-weight:bold; 
        #                    border:none; border-radius:12px; width:100%; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
        #         Unlock Full Report + PDF — Only $19 (one-time, no subscription)
        #     </button>
        # </a>
        # """, unsafe_allow_html=True)
        st.markdown(f"""
        <a href="{lemon_link}" target="_blank">
        <button style="background:#1d4ed8; color:white; padding:1.2rem; font-size:1.3rem; font-weight:bold; 
                    border:none; border-radius:12px; width:100%; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.15);">
        Unlock Full Report + PDF — $19 one-time
        </button>
        </a>
        """, unsafe_allow_html=True)


        st.caption("Instant access per session • 60-day money-back • No subscription")

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
        # print("[TEST] PDF generated:", pdf_path)  # console log

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