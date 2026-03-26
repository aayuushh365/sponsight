import streamlit as st
import time
import pandas as pd
from score import get_score, ROLE_SOC_MAP

st.set_page_config(
    page_title="Sponsight — Know before you apply",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown('<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">', unsafe_allow_html=True)

st.markdown("""<style>
:root {
  --p:#4338CA; --pl:#6366F1; --pg:rgba(99,102,241,0.1);
  --s:#059669; --w:#D97706; --d:#DC2626;
  --t1:#0F172A; --t2:#475569; --t3:#94A3B8;
  --r:16px; --rsm:10px;
}
html, body {
  background: linear-gradient(145deg,#E0E7FF 0%,#EEF2FF 30%,#F5F3FF 60%,#EDE9FE 100%) !important;
  background-attachment: fixed !important; min-height: 100vh;
}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"],.main,.stApp { background: transparent !important; }
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer { display:none !important; }
.block-container,[data-testid="stMainBlockContainer"] { padding:0 !important; max-width:100% !important; }
section[data-testid="stSidebar"] { display:none !important; }

[data-testid="stTextInput"] label,[data-testid="stSelectbox"] label {
  font-family:'DM Sans',sans-serif !important; font-size:.74rem !important; font-weight:600 !important;
  text-transform:uppercase !important; letter-spacing:.07em !important;
  color:#475569 !important; display:block !important; margin-bottom:6px !important;
}
[data-testid="stTextInput"] > div { background:transparent !important; border:none !important; box-shadow:none !important; }
[data-testid="stTextInput"] input {
  background:#FFFFFF !important; border:1.5px solid #E2E8F0 !important; border-radius:10px !important;
  color:#0F172A !important; font-family:'DM Sans',sans-serif !important;
  font-size:1rem !important; padding:.7rem 1.1rem !important;
  transition:border-color .2s,box-shadow .2s !important;
  box-shadow:0 1px 4px rgba(0,0,0,0.06) !important; width:100% !important;
}
[data-testid="stTextInput"] input:focus { border-color:#6366F1 !important; box-shadow:0 0 0 3px rgba(99,102,241,0.12),0 1px 4px rgba(0,0,0,0.06) !important; outline:none !important; }
[data-testid="stTextInput"] input::placeholder { color:#94A3B8 !important; }

[data-testid="stSelectbox"] > div { background:transparent !important; border:none !important; }
[data-testid="stSelectbox"] > div > div {
  background:#FFFFFF !important; border:1.5px solid #E2E8F0 !important; border-radius:10px !important;
  font-family:'DM Sans',sans-serif !important; font-size:1rem !important;
  min-height:48px !important; box-shadow:0 1px 4px rgba(0,0,0,0.06) !important;
}
[data-testid="stSelectbox"] * { color:#0F172A !important; font-family:'DM Sans',sans-serif !important; background:transparent !important; }
[data-testid="stSelectbox"] > div > div > div > div { background:#FFFFFF !important; }
[data-testid="stSelectbox"] svg { fill:#475569 !important; }
[data-testid="stSelectbox"] > div > div:focus-within { border-color:#6366F1 !important; box-shadow:0 0 0 3px rgba(99,102,241,0.12) !important; }

[data-testid="stButton"] > button {
  width:100% !important; height:48px !important;
  background:linear-gradient(135deg,#3730A3,#4F46E5,#6366F1) !important;
  color:#fff !important; border:none !important; border-radius:10px !important;
  font-family:'Syne',sans-serif !important; font-size:1rem !important; font-weight:700 !important;
  cursor:pointer !important; transition:all .2s !important;
  box-shadow:0 4px 14px rgba(79,70,229,.4) !important; white-space:nowrap !important; padding:0 1.5rem !important;
}
[data-testid="stButton"] > button:hover { transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(79,70,229,.5) !important; }
[data-testid="stButton"] > button p { font-family:'Syne',sans-serif !important; font-weight:700 !important; color:#fff !important; }

/* Feedback buttons override */
.fb-row [data-testid="stButton"] > button {
  background:#F8FAFC !important; color:#475569 !important; border:1.5px solid #E2E8F0 !important;
  box-shadow:none !important; font-family:'DM Sans',sans-serif !important; font-weight:500 !important;
  font-size:.85rem !important; height:38px !important; width:auto !important; padding:0 1.1rem !important;
}
.fb-row [data-testid="stButton"] > button:hover { border-color:#6366F1 !important; color:#6366F1 !important; background:rgba(99,102,241,.06) !important; transform:none !important; }
.fb-row [data-testid="stButton"] > button p { color:inherit !important; }

[data-testid="stHorizontalBlock"] { gap:1rem !important; }
[data-testid="stColumn"] { padding:0 !important; }

/* Search card — columns get the card bottom */
[data-testid="stHorizontalBlock"] {
  background:#FFFFFF !important; border-radius:0 0 16px 16px !important;
  box-shadow:0 8px 40px rgba(67,56,202,0.12),0 2px 6px rgba(0,0,0,0.05) !important;
  border:1px solid #E2E8F0 !important; border-top:none !important;
  padding:1.4rem 2rem 1.8rem !important;
  max-width:960px !important; margin:0 auto !important;
}

/* Autocomplete suggestion list */
.ac-list { background:#FFFFFF; border:1.5px solid #E2E8F0; border-radius:10px; max-height:220px; overflow-y:auto; margin-top:2px; box-shadow:0 4px 16px rgba(67,56,202,0.12); }
.ac-item { padding:.6rem 1rem; font-family:'DM Sans',sans-serif; font-size:.9rem; color:#0F172A; cursor:pointer; border-bottom:1px solid #F1F5F9; }
.ac-item:last-child { border-bottom:none; }
.ac-item:hover { background:#EEF2FF; color:#4338CA; }
.ac-none { padding:.6rem 1rem; font-family:'DM Sans',sans-serif; font-size:.85rem; color:#94A3B8; }

@keyframes fadeUp { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn { from{opacity:0} to{opacity:1} }
@keyframes gm { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

.sh { background:linear-gradient(135deg,#1E1B4B 0%,#312E81 35%,#4338CA 65%,#6366F1 100%); background-size:200% 200%; animation:gm 10s ease infinite; padding:3.5rem 5vw 4.5rem; position:relative; overflow:hidden; width:100%; }
.sh::before { content:''; position:absolute; inset:0; background:radial-gradient(ellipse at 75% 40%,rgba(165,180,252,.2) 0%,transparent 60%); pointer-events:none; }
.sh-i { max-width:1400px; margin:0 auto; display:flex; align-items:center; justify-content:space-between; gap:2.5rem; flex-wrap:wrap; position:relative; z-index:1; }
.sh-l { flex:1; min-width:280px; }
.sh-brand { display:flex; align-items:center; gap:.65rem; margin-bottom:1.4rem; animation:fadeUp .5s ease both; }
.sh-logo { width:42px; height:42px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.22); border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:22px; }
.sh-wm { font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800; color:#fff; letter-spacing:-.02em; }
.sh-hl { font-family:'Syne',sans-serif; font-size:clamp(2rem,3.5vw,3.1rem); font-weight:800; color:#fff; line-height:1.12; letter-spacing:-.03em; margin-bottom:1rem; animation:fadeUp .5s ease .08s both; }
.sh-hl em { font-style:normal; background:linear-gradient(90deg,#A5B4FC,#E0E7FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.sh-sub { font-family:'DM Sans',sans-serif; font-size:1.05rem; color:rgba(255,255,255,.72); line-height:1.65; max-width:520px; margin-bottom:1.6rem; font-weight:300; animation:fadeUp .5s ease .16s both; }
.sh-pills { display:flex; gap:.55rem; flex-wrap:wrap; animation:fadeUp .5s ease .24s both; }
.sh-pill { background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.2); color:rgba(255,255,255,.9); padding:.35rem .95rem; border-radius:100px; font-family:'DM Sans',sans-serif; font-size:.8rem; font-weight:500; }
.sh-r { animation:fadeUp .5s ease .2s both; }
.sh-stats { display:grid; grid-template-columns:repeat(2,1fr); gap:.75rem; min-width:260px; }
.sh-stat { background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14); border-radius:14px; padding:1.1rem 1.3rem; text-align:center; }
.sh-sn { font-family:'Syne',sans-serif; font-size:1.55rem; font-weight:800; color:#fff; line-height:1; margin-bottom:.28rem; }
.sh-sl { font-family:'DM Sans',sans-serif; font-size:.7rem; color:rgba(255,255,255,.55); text-transform:uppercase; letter-spacing:.07em; font-weight:500; }
.ss-head { max-width:960px; margin:-1px auto 0; padding:0 5vw; position:relative; z-index:10; }
.ss-ttl { background:#FFFFFF; border-radius:16px 16px 0 0; border:1px solid #E2E8F0; border-bottom:1px solid #F1F5F9; padding:1.4rem 2rem 1.2rem; margin-top:-2rem; box-shadow:0 -4px 20px rgba(67,56,202,0.06); }
.ss-ttl-text { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; color:#0F172A; letter-spacing:-.01em; }
.ss-ttl-text span { color:#6366F1; }
.sl-wrap { max-width:960px; margin:1rem auto 0; padding:0 5vw 2rem; }
.sl-card { background:#FFFFFF; border-radius:16px; box-shadow:0 4px 20px rgba(67,56,202,0.08); border:1px solid #E2E8F0; padding:2.5rem 2rem; text-align:center; animation:fadeIn .3s ease both; }
.sl-steps { display:flex; flex-direction:column; gap:.7rem; max-width:400px; margin:0 auto 1.5rem; text-align:left; }
.sl-step { display:flex; align-items:center; gap:.75rem; padding:.6rem .9rem; border-radius:10px; font-family:'DM Sans',sans-serif; font-size:.9rem; color:#94A3B8; transition:all .25s; }
.sl-step.a { background:rgba(99,102,241,.08); color:#6366F1; font-weight:500; }
.sl-step.d { color:#059669; }
.sl-si { width:24px; height:24px; border-radius:50%; background:#F8FAFC; border:1.5px solid #E2E8F0; display:flex; align-items:center; justify-content:center; font-size:13px; flex-shrink:0; }
.sl-step.a .sl-si { background:rgba(99,102,241,.1); border-color:#6366F1; animation:pulse 1.2s ease infinite; }
.sl-step.d .sl-si { background:#DCFCE7; border-color:#86EFAC; }
.sl-pb { height:4px; background:#E2E8F0; border-radius:100px; overflow:hidden; max-width:400px; margin:0 auto; }
.sl-pf { height:100%; background:linear-gradient(90deg,#4338CA,#6366F1); border-radius:100px; transition:width .45s ease; }
.sr-wrap { max-width:960px; margin:1.5rem auto 0; padding:0 5vw 4rem; }
.sr-rb { border-radius:16px 16px 0 0; padding:1.2rem 2rem; display:flex; align-items:flex-start; gap:.9rem; animation:fadeUp .45s ease both; }
.sr-rb.st { background:linear-gradient(135deg,#DCFCE7,#D1FAE5); border:1.5px solid #86EFAC; border-bottom:none; }
.sr-rb.mo { background:linear-gradient(135deg,#FEF3C7,#FDE68A44); border:1.5px solid #FCD34D; border-bottom:none; }
.sr-rb.wk { background:linear-gradient(135deg,#FEE2E2,#FECACA44); border:1.5px solid #FCA5A5; border-bottom:none; }
.sr-ri { font-size:1.3rem; flex-shrink:0; margin-top:2px; }
.sr-rt { font-family:'DM Sans',sans-serif; font-size:1rem; line-height:1.5; }
.sr-rb.st .sr-rt { color:#065F46; } .sr-rb.mo .sr-rt { color:#92400E; } .sr-rb.wk .sr-rt { color:#991B1B; }
.sr-mc { background:linear-gradient(135deg,#FAFBFF 0%,#F5F7FF 50%,#F8F6FF 100%); border-radius:0 0 16px 16px; box-shadow:0 8px 40px rgba(67,56,202,0.12),0 2px 6px rgba(0,0,0,0.05); border:1.5px solid #E2E8F0; border-top:none; padding:2.2rem 2.5rem; margin-bottom:1rem; animation:fadeUp .45s ease .05s both; }
.sr-tg { display:grid; grid-template-columns:210px 1fr; gap:3rem; align-items:center; }
@media(max-width:640px) { .sr-tg,.sh-i { grid-template-columns:1fr; flex-direction:column; } }
.sr-cw { display:flex; flex-direction:column; align-items:center; gap:.6rem; }
.sr-scl { font-family:'Syne',sans-serif; font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.07em; }
.sr-cf { background:rgba(255,255,255,.9); border:1px solid #E2E8F0; border-radius:100px; padding:.3rem .9rem; font-family:'DM Sans',sans-serif; font-size:.76rem; color:#475569; font-weight:500; }
.sr-dg { display:grid; grid-template-columns:repeat(3,1fr); gap:.9rem; }
@media(max-width:700px) { .sr-dg { grid-template-columns:repeat(2,1fr); } }
.sr-di { background:linear-gradient(135deg,#FFFFFF,#F8FAFF); border:1px solid #E8EEFF; border-radius:10px; padding:.85rem 1.1rem; box-shadow:0 1px 4px rgba(99,102,241,0.06); }
.sr-dl { font-family:'DM Sans',sans-serif; font-size:.71rem; font-weight:600; text-transform:uppercase; letter-spacing:.06em; color:#94A3B8; margin-bottom:.3rem; }
.sr-dv { font-family:'Syne',sans-serif; font-size:.98rem; font-weight:700; color:#0F172A; }
.sr-bg { display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem; }
@media(max-width:680px) { .sr-bg { grid-template-columns:1fr; } }
.sr-sgc { background:linear-gradient(135deg,#FAFBFF,#F5F7FF); border-radius:16px; box-shadow:0 4px 20px rgba(67,56,202,0.08); border:1px solid #E8EEFF; padding:1.6rem 1.9rem; animation:fadeUp .45s ease .1s both; }
.sr-ct { font-family:'Syne',sans-serif; font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.09em; color:#6366F1; margin-bottom:1.3rem; }
.sr-sr { display:grid; grid-template-columns:120px 1fr 44px; align-items:center; gap:.8rem; margin-bottom:.9rem; }
.sr-srl { font-family:'DM Sans',sans-serif; font-size:.82rem; color:#475569; font-weight:500; }
.sr-srt { height:8px; background:#EEF2FF; border-radius:100px; overflow:hidden; }
.sr-srf { height:100%; border-radius:100px; animation:fadeIn .8s ease both; }
.sr-srv { font-family:'Syne',sans-serif; font-size:.8rem; font-weight:700; color:#0F172A; text-align:right; }
.sr-ec { background:linear-gradient(135deg,#FFFBF5,#FFF7ED); border-radius:16px; box-shadow:0 4px 20px rgba(217,119,6,0.06); border:1px solid #FDE68A; padding:1.6rem 1.9rem; animation:fadeUp .45s ease .15s both; }
.sr-ec .sr-ct { color:#D97706; }
.sr-ei { display:flex; gap:.75rem; margin-bottom:.75rem; font-family:'DM Sans',sans-serif; font-size:.9rem; color:#475569; line-height:1.6; align-items:flex-start; }
.sr-dot { width:7px; height:7px; border-radius:50%; background:#F59E0B; margin-top:.5rem; flex-shrink:0; }
.sr-fbc { background:#FFFFFF; border-radius:16px; border:1px solid #E2E8F0; padding:1.2rem 2rem; display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; animation:fadeUp .45s ease .2s both; margin-bottom:.75rem; box-shadow:0 2px 8px rgba(0,0,0,0.04); }
.sr-fbl { font-family:'DM Sans',sans-serif; font-size:.85rem; color:#475569; font-weight:500; }
.sr-foot { text-align:center; font-family:'DM Sans',sans-serif; font-size:.74rem; color:#94A3B8; padding-bottom:.5rem; animation:fadeIn .5s ease .3s both; }
.sr-err { background:#FEE2E2; border:1.5px solid #FCA5A5; border-radius:16px; padding:1.6rem 2rem; text-align:center; animation:fadeIn .3s ease both; }
.sr-err h3 { font-family:'Syne',sans-serif; font-weight:700; color:#DC2626; margin-bottom:.4rem; }
.sr-err p { font-family:'DM Sans',sans-serif; font-size:.88rem; color:#475569; }
.s-div { height:3px; background:linear-gradient(90deg,#4338CA,#6366F1,#8B5CF6,#6366F1,#4338CA); background-size:200% 100%; animation:gm 4s ease infinite; width:100%; }
@media(max-width:900px) { .ss-head,.sl-wrap,.sr-wrap { padding-left:1.2rem !important; padding-right:1.2rem !important; } .sh { padding-left:1.5rem; padding-right:1.5rem; } }
</style>""", unsafe_allow_html=True)

# ── Cache company names ──────────────────────────────────────────────
@st.cache_data
def load_company_names():
    df = pd.read_csv("company_signals.csv")
    names = df["clean_name"].dropna().unique().tolist()
    return sorted([n.title() for n in names if isinstance(n, str) and len(n) > 2])

# ── HERO ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="sh">
  <div class="sh-i">
    <div class="sh-l">
      <div class="sh-brand"><div class="sh-logo">🎯</div><span class="sh-wm">Sponsight</span></div>
      <div class="sh-hl">Know if a company will<br>sponsor you. <em>Before you apply.</em></div>
      <div class="sh-sub">Synthesized from 2.9 million government filings across 171,632 companies. A role-specific sponsorship likelihood score in seconds.</div>
      <div class="sh-pills">
        <div class="sh-pill">✓ USCIS + DOL Verified</div>
        <div class="sh-pill">✓ 5 Years of Data</div>
        <div class="sh-pill">✓ Free, No Sign-Up</div>
        <div class="sh-pill">✓ 60+ Role Types</div>
      </div>
    </div>
    <div class="sh-r">
      <div class="sh-stats">
        <div class="sh-stat"><div class="sh-sn">171K+</div><div class="sh-sl">Companies</div></div>
        <div class="sh-stat"><div class="sh-sn">2.9M</div><div class="sh-sl">Gov't Records</div></div>
        <div class="sh-stat"><div class="sh-sn">FY21–26</div><div class="sh-sl">Coverage</div></div>
        <div class="sh-stat"><div class="sh-sn">60+</div><div class="sh-sl">Role Types</div></div>
      </div>
    </div>
  </div>
</div>
<div class="s-div"></div>
""", unsafe_allow_html=True)

# ── SEARCH CARD TITLE ─────────────────────────────────────────────────
st.markdown("""
<div class="ss-head">
  <div class="ss-ttl">
    <div class="ss-ttl-text">Check sponsorship signal <span>→</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── INPUTS ────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([3, 2, 1.4])
with col1:
    company_input = st.text_input(
        "Company",
        placeholder="Start typing a company name...",
        key="ci",
        value=st.session_state.get("selected_company", "")
    )
with col2:
    role_input = st.selectbox(
        "Target Role",
        options=list(ROLE_SOC_MAP.keys()),
        index=0,
        key="ri"
    )
with col3:
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    calculate = st.button("Check Signal →", type="primary", key="calc")

# ── AUTOCOMPLETE SUGGESTIONS ─────────────────────────────────────────
# Show matching companies when user has typed 2+ chars
# and hasn't already selected a match
if company_input and len(company_input) >= 2 and not st.session_state.get("company_confirmed"):
    all_companies = load_company_names()
    query = company_input.upper()
    starts_with = [c for c in all_companies if c.upper().startswith(query)][:8]
    contains = [c for c in all_companies if query in c.upper() and not c.upper().startswith(query)][:4]
    suggestions = starts_with + contains

    if suggestions:
        st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] ~ div [data-testid="stSelectbox"] > div > div {
          border-radius: 0 0 10px 10px !important;
          border-top: none !important;
          margin-top: -2px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        ac_col1, ac_col2, ac_col3 = st.columns([3, 2, 1.4])
        with ac_col1:
            selected = st.selectbox(
                "Matching companies",
                options=["— select to confirm —"] + suggestions,
                key="ac_select",
                label_visibility="collapsed"
            )
        with ac_col2:
            st.empty()
        with ac_col3:
            st.empty()
        if selected != "— select to confirm —":
            st.session_state["selected_company"] = selected
            st.session_state["company_confirmed"] = True
            st.rerun()
        if selected != "— select to confirm —":
            st.session_state["selected_company"] = selected
            st.session_state["company_confirmed"] = True
            st.rerun()

# Reset confirmation if user clears or changes input
if st.session_state.get("company_confirmed") and company_input != st.session_state.get("selected_company", ""):
    st.session_state["company_confirmed"] = False
    st.session_state["selected_company"] = ""

# ── SESSION STATE ─────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "sc" not in st.session_state:
    st.session_state.sc = ""
if "sr" not in st.session_state:
    st.session_state.sr = ""

# ── CALCULATE ─────────────────────────────────────────────────────────
if calculate:
    company = company_input.strip()
    if not company:
        st.markdown('<div class="sr-wrap"><div class="sr-err"><h3>Enter a company name</h3><p>Type a company name and select from the suggestions, then click Check Signal.</p></div></div>', unsafe_allow_html=True)
    else:
        st.session_state.sc = company
        st.session_state.sr = role_input
        st.session_state["company_confirmed"] = False
        slot = st.empty()
        steps_cfg = [
            ("🔍", f'Searching 171,632 companies for "{company}"'),
            ("📋", "Checking petition history and approval rates"),
            ("🎯", f"Analyzing {role_input} role type match"),
            ("📊", "Calculating confidence score"),
        ]
        for i in range(len(steps_cfg) + 1):
            rows = ""
            for j, (ic, lb) in enumerate(steps_cfg):
                c = "d" if j < i else ("a" if j == i else "")
                ico = "✓" if j < i else ic
                rows += f'<div class="sl-step {c}"><div class="sl-si">{ico}</div>{lb}</div>'
            pct = int(i / len(steps_cfg) * 100)
            slot.markdown(
                f'<div class="sl-wrap"><div class="sl-card"><div class="sl-steps">{rows}</div>'
                f'<div class="sl-pb"><div class="sl-pf" style="width:{pct}%"></div></div></div></div>',
                unsafe_allow_html=True
            )
            time.sleep(0.5)
        result = get_score(company, role_input)
        st.session_state.result = result
        slot.empty()
        st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────
if st.session_state.result:
    result = st.session_state.result
    company = st.session_state.sc
    role = st.session_state.sr

    if not result.get("found"):
        st.markdown(
            f'<div class="sr-wrap"><div class="sr-err"><h3>No data found for "{company}"</h3>'
            f'<p>Try a shorter term. Example: "Amazon" not "Amazon.com Services LLC".</p></div></div>',
            unsafe_allow_html=True
        )
    else:
        score = result["final_score"]
        confidence = result["confidence"]
        sigs = result["signals"]
        name = result["company_name"].title()
        wage = str(result["wage_level"])
        ltext = result["lottery_text"]
        appr = result["total_approvals"]
        yr = result["most_recent_year"]

        if score >= 66:
            col = "#059669"; cls = "st"; ico = "🟢"
            reco = f"<strong>Strong signal.</strong> {name} has a consistent track record sponsoring {role} roles. Worth your tailoring time."
        elif score >= 35:
            col = "#D97706"; cls = "mo"; ico = "🟡"
            reco = f"<strong>Moderate signal.</strong> {name} has some sponsorship history for {role}, but with notable gaps. Proceed with awareness."
        else:
            col = "#DC2626"; cls = "wk"; ico = "🔴"
            reco = f"<strong>Weak signal.</strong> Limited evidence {name} sponsors {role} roles. Consider prioritizing other targets first."

        R = 72; C = 2 * 3.14159 * R; off = C * (1 - score / 100)
        wm = {"I":"Level I (Entry)","II":"Level II (Mid)","III":"Level III (Senior)","IV":"Level IV (Lead)"}
        wd = wm.get(wage, wage)
        try:
            lp = ltext.split(" ")[1] if "unknown" not in ltext else "N/A"
        except Exception:
            lp = "N/A"

        sc_cfg = [
            ("Recency", sigs["recency"], "#4F46E5"),
            ("Approval Rate", sigs["approval_rate"], "#059669"),
            ("Role Match", sigs["role_match"], "#0EA5E9"),
            ("Trend", sigs["trend"], "#8B5CF6"),
            ("Entry Level", sigs["entry_level"], "#F59E0B"),
            ("Volume", sigs["volume"], "#EC4899"),
        ]
        srows = "".join(
            f'<div class="sr-sr"><div class="sr-srl">{l}</div>'
            f'<div class="sr-srt"><div class="sr-srf" style="width:{min(int(v),100)}%;background:{c};"></div></div>'
            f'<div class="sr-srv">{int(v)}</div></div>'
            for l, v, c in sc_cfg
        )

        expl = []
        if sigs["recency"] >= 80: expl.append(f"Filed H1B petitions as recently as {yr} — a strong current signal.")
        elif sigs["recency"] >= 50: expl.append("Has filed petitions in recent years but activity may be slowing.")
        else: expl.append(f"Last petition filing was in {yr}. Recency is a concern.")
        if sigs["approval_rate"] >= 90: expl.append(f"Approval rate of {sigs['approval_rate']:.0f}% — almost always follows through when sponsoring.")
        elif sigs["approval_rate"] >= 70: expl.append(f"Approval rate of {sigs['approval_rate']:.0f}% is reasonable.")
        else: expl.append(f"Approval rate of {sigs['approval_rate']:.0f}% is below average, which may indicate speculative filings.")
        if sigs["role_match"] >= 30: expl.append(f"{sigs['role_match']:.0f}% of filings match {role} role types — a meaningful signal.")
        elif sigs["role_match"] >= 10: expl.append(f"Only {sigs['role_match']:.0f}% of filings match {role} types.")
        else: expl.append(f"Very few filings ({sigs['role_match']:.0f}%) match {role} types. They may not typically sponsor this role.")
        if sigs["trend"] >= 65: expl.append("Sponsorship activity is growing year over year — a positive directional signal.")
        elif sigs["trend"] <= 35: expl.append("Sponsorship activity has declined in recent years, which reduces confidence.")

        ehtml = "".join(f'<div class="sr-ei"><div class="sr-dot"></div><span>{e}</span></div>' for e in expl)
        lbl = cls.replace("st","Strong").replace("mo","Moderate").replace("wk","Weak")

        st.markdown(f"""
<div class="sr-wrap">
  <div class="sr-rb {cls}"><span class="sr-ri">{ico}</span><span class="sr-rt">{reco}</span></div>
  <div class="sr-mc">
    <div class="sr-tg">
      <div class="sr-cw">
        <svg width="175" height="175" viewBox="0 0 175 175" style="filter:drop-shadow(0 4px 14px rgba(67,56,202,.18));">
          <circle cx="87" cy="87" r="{R}" fill="none" stroke="#EEF2FF" stroke-width="10"/>
          <circle cx="87" cy="87" r="{R}" fill="none" stroke="{col}" stroke-width="10"
            stroke-dasharray="{C:.2f}" stroke-dashoffset="{off:.2f}"
            stroke-linecap="round" transform="rotate(-90 87 87)"/>
          <text x="87" y="81" text-anchor="middle" font-family="Syne,sans-serif" font-size="32" font-weight="800" fill="{col}">{score}</text>
          <text x="87" y="101" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="12" fill="#94A3B8">/100</text>
        </svg>
        <div class="sr-scl" style="color:{col};">{lbl} Signal</div>
        <div class="sr-cf">Confidence: {confidence}%</div>
      </div>
      <div class="sr-dg">
        <div class="sr-di"><div class="sr-dl">Company</div><div class="sr-dv">{name}</div></div>
        <div class="sr-di"><div class="sr-dl">Role Searched</div><div class="sr-dv">{role}</div></div>
        <div class="sr-di"><div class="sr-dl">Total Approvals</div><div class="sr-dv">{appr:,}</div></div>
        <div class="sr-di"><div class="sr-dl">Last Filing Year</div><div class="sr-dv">{yr}</div></div>
        <div class="sr-di"><div class="sr-dl">Typical Wage Level</div><div class="sr-dv">{wd}</div></div>
        <div class="sr-di"><div class="sr-dl">2026 Lottery Odds</div><div class="sr-dv">{lp}</div></div>
      </div>
    </div>
  </div>
  <div class="sr-bg">
    <div class="sr-sgc"><div class="sr-ct">Signal Breakdown</div>{srows}</div>
    <div class="sr-ec"><div class="sr-ct">Why this score</div>{ehtml}</div>
  </div>
  <div class="sr-fbc">
    <div class="sr-fbl">Was this score accurate for your experience?</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Feedback buttons
        st.markdown('<div class="fb-row" style="max-width:960px;margin:0 auto;padding:0 5vw .5rem;">', unsafe_allow_html=True)
        fb1, fb2, fb3 = st.columns([1.5, 1.5, 9])
        with fb1:
            if st.button("👍 Yes, helpful", key="fb_yes"):
                st.session_state["feedback"] = "positive"
        with fb2:
            if st.button("👎 Needs work", key="fb_no"):
                st.session_state["feedback"] = "negative"
        st.markdown("</div>", unsafe_allow_html=True)

        fb = st.session_state.get("feedback")
        if fb == "positive":
            st.markdown('<div style="max-width:960px;margin:0 auto;padding:0 5vw;"><p style="font-family:DM Sans,sans-serif;font-size:.85rem;color:#059669;font-weight:500;">Thanks for the feedback. Glad it was helpful.</p></div>', unsafe_allow_html=True)
        elif fb == "negative":
            st.markdown('<div style="max-width:960px;margin:0 auto;padding:0 5vw;"><p style="font-family:DM Sans,sans-serif;font-size:.85rem;color:#D97706;font-weight:500;">Thanks. We will keep improving the scores.</p></div>', unsafe_allow_html=True)

        st.markdown('<div class="sr-wrap" style="padding-top:0;padding-bottom:2rem;"><div class="sr-foot">Data: USCIS H1B Employer Data Hub + DOL LCA Disclosure Files · FY2021–FY2026 · Historical patterns only, not a guarantee of future intent</div></div>', unsafe_allow_html=True)