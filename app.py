import streamlit as st
import hashlib
import time
import re
from config import APP_TITLE
import database as db
from chatbot import AutismChatbot

# Init
db.init_db()

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="expanded",
)

_defaults = dict(
    logged_in=False,
    username=None,
    user_id=None,
    chatbot=None,
    messages=[],
    auth_mode="login",
    typing=False,
    show_landing=True,
)
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

#CSS
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<style>


@keyframes pageIn {
  from { opacity: 0; transform: translateY(18px) scale(.985); }
  to   { opacity: 1; transform: translateY(0)     scale(1);   }
}
@keyframes pageOut {
  from { opacity: 1; transform: translateY(0)     scale(1);   }
  to   { opacity: 0; transform: translateY(-14px) scale(.985); }
}
.page-enter {
  animation: pageIn .42s cubic-bezier(.22,1,.36,1) both;
}
.page-exit {
  animation: pageOut .22s ease forwards;
  pointer-events: none;
}

/* Apply entrance animation to the main block */
section[data-testid="stMain"] .block-container {
  animation: pageIn .4s cubic-bezier(.22,1,.36,1) both;
}

:root {
  --g:      #10a37f;
  --g-dark: #0d8f6e;
  --bg:     #0b0f1a;
  --card:   #141b2d;
  --border: rgba(255,255,255,.07);
  --text:   #dde8e4;
  --muted:  #40635a;
  --sub:    #5e8c80;
  --ff:     'Plus Jakarta Sans', sans-serif;
}
html, body, [class*="css"] {
  font-family: var(--ff) !important;
  background:  var(--bg) !important;
  color:       var(--text) !important;
}
#MainMenu, footer { visibility: hidden; }
header { display: block !important; }
[data-testid="collapsedControl"] { display:block!important; visibility:visible!important; opacity:1!important; }

.block-container { padding: 2rem 2.5rem 2rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
  background: #0d1120 !important;
  border-right: 1px solid var(--border) !important;
  min-width: 280px !important; max-width: 280px !important;
  transition: all 0.3s ease !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 1.75rem 1.25rem 1.5rem !important;
  display: flex; flex-direction: column; gap: 0;
}
[data-testid="stSidebar"][aria-expanded="false"] {
  min-width: 0 !important; max-width: 0 !important; overflow: hidden !important;
}
section[data-testid="stMain"] { transition: margin-left 0.3s ease, width 0.3s ease !important; }
[data-testid="stSidebar"] .stButton { margin: 0 !important; }
[data-testid="stSidebar"] .stButton > button {
  font-family: var(--ff) !important; font-size:.875rem !important;
  font-weight:600 !important; width:100% !important; transition:all .2s !important;
}

.sb-btn-primary .stButton > button {
  background: linear-gradient(135deg,#10a37f,#0d8f6e) !important;
  color:#fff !important; border:none !important; border-radius:12px !important;
  padding:.75rem 1rem !important; box-shadow:0 4px 18px rgba(16,163,127,.35) !important;
}
.sb-btn-primary .stButton > button:hover { transform:translateY(-2px) !important; }
.sb-btn-danger .stButton > button {
  background:rgba(239,68,68,.07) !important; color:#ef4444 !important;
  border:1px solid rgba(239,68,68,.18) !important; border-radius:11px !important;
  padding:.65rem 1rem !important; font-size:.82rem !important; font-weight:500 !important;
}
.sb-btn-danger .stButton > button:hover { background:rgba(239,68,68,.14) !important; }

.stButton > button {
  font-family:var(--ff) !important; font-weight:600 !important;
  border-radius:12px !important; transition:all .2s !important; width:100% !important;
}
.btn-ghost .stButton > button {
  background:rgba(255,255,255,.04) !important; color:var(--sub) !important;
  border:1px solid var(--border) !important; border-radius:999px !important;
  padding:.55rem 1rem !important; font-size:.82rem !important; font-weight:500 !important;
}
.btn-ghost .stButton > button:hover {
  background:rgba(16,163,127,.09) !important;
  border-color:rgba(16,163,127,.28) !important; color:var(--g) !important;
}
.btn-switch .stButton > button {
  background:transparent !important; color:var(--sub) !important;
  border:1px solid var(--border) !important; border-radius:12px !important;
  padding:.7rem 1rem !important; font-size:.85rem !important; font-weight:500 !important;
}
.btn-switch .stButton > button:hover {
  border-color:rgba(16,163,127,.3) !important; color:var(--g) !important;
  background:rgba(16,163,127,.05) !important;
}
.btn-cta .stButton > button {
  background:linear-gradient(135deg,#10a37f,#0d8f6e) !important;
  color:#fff !important; border:none !important; border-radius:14px !important;
  padding:1rem 2rem !important; font-size:1rem !important; font-weight:700 !important;
  box-shadow:0 6px 28px rgba(16,163,127,.42) !important; letter-spacing:.02em !important;
}
.btn-cta .stButton > button:hover { transform:translateY(-3px) !important; }

.stTextInput > div > div > input {
  background:rgba(255,255,255,.04) !important;
  border:1.5px solid var(--border) !important; border-radius:12px !important;
  color:var(--text) !important; font-family:var(--ff) !important;
  font-size:.9rem !important; padding:.8rem 1.1rem !important;
  caret-color:var(--g) !important; transition:all .2s !important; height:48px !important;
}
.stTextInput > div > div > input:focus {
  border-color:rgba(16,163,127,.5) !important; background:rgba(16,163,127,.05) !important;
  box-shadow:0 0 0 4px rgba(16,163,127,.1) !important; outline:none !important;
}
.stTextInput > div > div > input::placeholder { color:rgba(255,255,255,.18) !important; }
.stTextInput label {
  color:var(--muted) !important; font-size:.7rem !important; font-weight:700 !important;
  letter-spacing:.08em !important; text-transform:uppercase !important; margin-bottom:.35rem !important;
}

[data-testid="stFormSubmitButton"] > button {
  font-family:var(--ff) !important;
  background:linear-gradient(135deg,#10a37f,#0d8f6e) !important;
  color:#fff !important; border:none !important; border-radius:12px !important;
  padding:.8rem 1.5rem !important; font-size:.9rem !important; font-weight:700 !important;
  width:100% !important; height:48px !important;
  box-shadow:0 4px 20px rgba(16,163,127,.35) !important; transition:all .2s !important;
}
[data-testid="stFormSubmitButton"] > button:hover { transform:translateY(-2px) !important; }



.stAlert { border-radius:12px !important; font-family:var(--ff) !important; font-size:.875rem !important; }
hr { border:none !important; border-top:1px solid var(--border) !important; margin:0 !important; }

[data-testid="stVerticalBlockBorderWrapper"] {
  background:var(--card) !important;
  border:1px solid rgba(16,163,127,.18) !important; border-radius:22px !important;
  padding:2rem 2rem 1.5rem !important;
  box-shadow:0 24px 64px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.055) !important;
}

.brand-mark {
  width:44px; height:44px; border-radius:13px;
  background:linear-gradient(140deg,#13c497,#0a7a5e);
  display:inline-flex; align-items:center; justify-content:center;
  font-size:18px; color:#fff;
  box-shadow:0 0 0 1px rgba(16,163,127,.35), 0 6px 20px rgba(16,163,127,.28);
  flex-shrink:0;
}
.glow-title {
  text-shadow:0 0 12px rgba(16,163,127,.8),0 0 24px rgba(16,163,127,.6),0 0 36px rgba(16,163,127,.4);
  transition:text-shadow .3s,transform .3s; display:inline-block;
}
.glow-title:hover {
  text-shadow:0 0 18px rgba(16,163,127,1),0 0 30px rgba(16,163,127,.8),0 0 42px rgba(16,163,127,.6);
  transform:scale(1.02);
}

/* ── Chat messages ─────────────────────────────────────── */
/* Wrapper row */
.msg-row {
  display:flex; align-items:flex-start; gap:10px;
  margin-bottom:.85rem; padding:0 .25rem;
  width: 100%;
}
.msg-row-user { justify-content: flex-end; }
.msg-row-bot  { justify-content: flex-start; }

/* inner content div that holds bubble+meta */
.msg-content { display:flex; flex-direction:column; max-width:68%; }

/* Avatar */
.msg-av {
  width:32px; height:32px; border-radius:9px; flex-shrink:0;
  display:flex; align-items:center; justify-content:center; font-size:12px;
  margin-top:2px;
}
.msg-av-bot  { background:linear-gradient(140deg,#13c497,#0a7a5e); color:#fff; box-shadow:0 3px 10px rgba(16,163,127,.28); }
.msg-av-user { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.12); color:var(--sub); }

/* Bubble */
.msg-bubble {
  padding:.8rem 1.1rem; font-size:.88rem;
  line-height:1.72;
  overflow-wrap: break-word;
  word-break: normal;
  white-space: normal;
}
.msg-bubble-user {
  background:linear-gradient(135deg,#10a37f,#0d8f6e); color:#fff;
  border-radius:16px 16px 3px 16px;
  box-shadow:0 4px 14px rgba(16,163,127,.28);
}
.msg-bubble-bot {
  background:rgba(20,27,45,.96); border:1px solid rgba(255,255,255,.08);
  color:#b8d0c8; border-radius:16px 16px 16px 3px;
}

/* Meta (time) */
.msg-meta { font-size:.66rem; color:var(--muted); margin-top:3px; padding:0 2px; }
.msg-meta-user { text-align:right; }
.msg-meta-bot  { text-align:left; }

/* Typing */
.typing-dots { display:inline-flex; align-items:center; gap:5px; padding:.4rem .2rem; }
.typing-dot  { width:6px; height:6px; border-radius:50%; background:var(--g); animation:blink 1.4s ease infinite; }
.typing-dot:nth-child(2){animation-delay:.22s}
.typing-dot:nth-child(3){animation-delay:.44s}
@keyframes blink{0%,80%,100%{opacity:.2;transform:scale(.75)}40%{opacity:1;transform:scale(1.15)}}

/* ── Scroll area ───────────────────────────────────────── */
#chat-scroll {
  overflow-y:auto; padding:1rem .2rem 1rem;
  scroll-behavior:smooth;
}
#chat-scroll::-webkit-scrollbar { width:4px; }
#chat-scroll::-webkit-scrollbar-track { background:transparent; }
#chat-scroll::-webkit-scrollbar-thumb { background:rgba(16,163,127,.2); border-radius:99px; }

/* ── Sticky input bar ──────────────────────────────────── */
/* Sticky bar handled by JS directly on stForm element */

/* ── Other ─────────────────────────────────────────────── */
.status-badge { display:inline-flex; align-items:center; gap:7px; font-size:.78rem; color:var(--muted); }
.status-dot   { width:7px; height:7px; border-radius:50%; background:var(--g); display:inline-block;
  box-shadow:0 0 0 2px rgba(16,163,127,.2),0 0 10px rgba(16,163,127,.5); animation:pulse 2.5s ease infinite; }
@keyframes pulse{0%,100%{box-shadow:0 0 0 2px rgba(16,163,127,.2),0 0 8px rgba(16,163,127,.4)}50%{box-shadow:0 0 0 4px rgba(16,163,127,.08),0 0 18px rgba(16,163,127,.6)}}

.hist-item      { display:flex; align-items:center; gap:11px; padding:.65rem .75rem; border-radius:11px; cursor:pointer; transition:background .15s; }
.hist-item:hover{ background:rgba(255,255,255,.045); }
.hist-icon      { width:30px; height:30px; border-radius:9px; flex-shrink:0; background:rgba(255,255,255,.05); border:1px solid var(--border); display:flex; align-items:center; justify-content:center; font-size:11px; color:var(--muted); }
.hist-label     { font-size:.83rem; color:#7ab0a5; font-weight:500; line-height:1.3; }
.hist-ts        { font-size:.7rem; color:var(--muted); margin-top:1px; }

.upgrade-card  { background:linear-gradient(135deg,rgba(16,163,127,.09),rgba(16,163,127,.03)); border:1px solid rgba(16,163,127,.18); border-radius:14px; padding:1rem 1.1rem; }
.upgrade-title { font-size:.83rem; font-weight:700; color:#7abfb0; margin-bottom:4px; }
.upgrade-sub   { font-size:.76rem; color:var(--muted); line-height:1.55; }

.section-label  { font-size:.68rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); padding:.15rem 0 .5rem; display:block; }
.user-pill      { display:flex; align-items:center; gap:10px; background:rgba(255,255,255,.04); border:1px solid var(--border); border-radius:13px; padding:.7rem .9rem; }
.user-av-circle { width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#13c497,#0a7a5e); display:flex; align-items:center; justify-content:center; font-size:.82rem; font-weight:800; color:#fff; flex-shrink:0; }
.user-name      { font-size:.85rem; font-weight:600; color:#9abfb5; line-height:1.3; }
.user-plan      { font-size:.72rem; color:var(--muted); margin-top:1px; }
.disclaimer     { text-align:center; font-size:.72rem; color:var(--muted); padding:.4rem 0 .3rem; line-height:1.5; }

.sp-xs{height:.5rem;display:block} .sp-sm{height:1rem;display:block}
.sp-md{height:1.5rem;display:block} .sp-lg{height:2rem;display:block}

/* ══ Shared animated background ══════════════════════════ */
.bg-grid {
  position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    linear-gradient(rgba(16,163,127,.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(16,163,127,.04) 1px,transparent 1px);
  background-size:40px 40px;
  animation:gridMove 20s linear infinite;
}
@keyframes gridMove{0%{background-position:0 0}100%{background-position:40px 40px}}
.bg-glow {
  position:fixed; top:-20%; left:50%; transform:translateX(-50%);
  width:700px; height:700px; border-radius:50%;
  background:radial-gradient(circle,rgba(16,163,127,.10) 0%,transparent 70%);
  pointer-events:none; z-index:0; animation:glowPulse 4s ease-in-out infinite;
}
@keyframes glowPulse{0%,100%{opacity:.7;transform:translateX(-50%) scale(1)}50%{opacity:1;transform:translateX(-50%) scale(1.08)}}

/* ══ Landing-only ═════════════════════════════════════════ */
.school-logo-wrapper { display:flex; justify-content:center; margin-bottom:2rem; }
.school-logo-ring { width:100px; height:100px; border-radius:50%; border:2px solid rgba(16,163,127,.35); display:flex; align-items:center; justify-content:center; background:rgba(16,163,127,.07); box-shadow:0 0 0 6px rgba(16,163,127,.06),0 0 30px rgba(16,163,127,.18); position:relative; animation:rotateBorder 8s linear infinite; }
.school-logo-ring::before { content:''; position:absolute; inset:-3px; border-radius:50%; background:conic-gradient(from 0deg,rgba(16,163,127,.8),transparent 60%,rgba(16,163,127,.4),transparent); animation:rotateBorder 3s linear infinite; z-index:-1; }
@keyframes rotateBorder{to{transform:rotate(360deg)}}
.school-logo-inner       { width:86px;height:86px;border-radius:50%;background:#0d1120;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;z-index:1; }
.school-logo-placeholder { font-size:2rem;color:#10a37f;opacity:.7; }

.stat-card   { background:linear-gradient(135deg,rgba(16,163,127,.08),rgba(16,163,127,.03)); border:1px solid rgba(16,163,127,.2); border-radius:18px; padding:1.5rem 1rem; text-align:center; transition:transform .25s,box-shadow .25s; position:relative; overflow:hidden; }
.stat-card::after { content:''; position:absolute; top:0;left:0;right:0; height:2px; background:linear-gradient(90deg,transparent,#10a37f,transparent); }
.stat-card:hover { transform:translateY(-4px); box-shadow:0 12px 36px rgba(16,163,127,.2); }
.stat-value  { font-size:2.4rem; font-weight:800; color:#10a37f; letter-spacing:-1px; line-height:1; margin-bottom:.35rem; text-shadow:0 0 20px rgba(16,163,127,.4); }
.stat-label  { font-size:.78rem; font-weight:600; color:var(--muted); letter-spacing:.06em; text-transform:uppercase; }

.tech-pill   { display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:999px;padding:.4rem .9rem;font-size:.78rem;font-weight:600;color:#6aaa98;margin:.25rem;transition:all .2s; }
.tech-pill:hover { background:rgba(16,163,127,.08);border-color:rgba(16,163,127,.25);color:#10a37f;transform:translateY(-1px); }
.tech-pill i { font-size:.72rem; color:#10a37f; }

.feature-row       { display:flex;align-items:flex-start;gap:14px;padding:1rem 1.1rem;border-radius:14px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);margin-bottom:.75rem;transition:background .2s; }
.feature-row:hover { background:rgba(16,163,127,.04); }
.feature-icon-wrap { width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(16,163,127,.2),rgba(16,163,127,.08));display:flex;align-items:center;justify-content:center;font-size:.85rem;color:#10a37f;flex-shrink:0; }
.feature-text-title{ font-size:.85rem;font-weight:700;color:#8abfb5;margin-bottom:2px; }
.feature-text-desc { font-size:.78rem;color:var(--muted);line-height:1.55; }

.recall-track { height:10px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden;margin:.6rem 0; }
.recall-fill  { height:100%;border-radius:99px;background:linear-gradient(90deg,#0a7a5e,#10a37f,#13c497);box-shadow:0 0 12px rgba(16,163,127,.5);animation:fillBar 1.8s cubic-bezier(.22,1,.36,1) both;animation-delay:.4s; }
@keyframes fillBar{from{width:0}}

.section-divider      { display:flex;align-items:center;gap:14px;margin:2.5rem 0 2rem; }
.section-divider-line { flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(16,163,127,.3),transparent); }
.section-divider-text { font-size:.72rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);white-space:nowrap; }
.landing-footer       { text-align:center;padding:2.5rem 0 1rem;font-size:.73rem;color:var(--muted);line-height:1.7;border-top:1px solid var(--border);margin-top:3rem; }

/* ── st.chat_input native widget styling ────────────────── */
[data-testid="stChatInput"] {
  background: rgba(20,27,45,.95) !important;
  border: 1.5px solid rgba(16,163,127,.25) !important;
  border-radius: 16px !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: rgba(16,163,127,.55) !important;
  box-shadow: 0 0 0 4px rgba(16,163,127,.1) !important;
}
[data-testid="stChatInput"] textarea {
  font-family: var(--ff) !important;
  font-size: .92rem !important;
  color: var(--text) !important;
  caret-color: var(--g) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
  color: rgba(255,255,255,.2) !important;
}
[data-testid="stChatInputSubmitButton"] button {
  background: linear-gradient(135deg,#10a37f,#0d8f6e) !important;
  border-radius: 10px !important;
  color: #fff !important;
}
/* Bottom bar that wraps chat_input */
[data-testid="stBottom"] {
  background: linear-gradient(to top, rgba(11,15,26,1) 80%, rgba(11,15,26,0)) !important;
  padding: .3rem 0 .5rem !important;
}

</style>
""", unsafe_allow_html=True)


#bg partagee
def inject_bg():
    st.markdown('<div class="bg-grid"></div><div class="bg-glow"></div>',
                unsafe_allow_html=True)


def page_transition_js():
    """Inject JS that plays exit animation before every st.rerun navigation."""
    st.markdown("""
    <script>
    (function(){
      // Intercept all button clicks and play exit animation before Streamlit reruns
      if(window._transitionBound) return;
      window._transitionBound = true;

      function playExit(cb){
        var main = document.querySelector('section[data-testid="stMain"] .block-container');
        if(!main){ cb(); return; }
        main.style.transition = 'opacity .2s ease, transform .2s ease';
        main.style.opacity    = '0';
        main.style.transform  = 'translateY(-12px) scale(.988)';
        setTimeout(cb, 210);
      }

      // On each Streamlit rerender reset the animation
      document.addEventListener('click', function(e){
        var btn = e.target.closest('button');
        if(!btn) return;
        // give Streamlit a beat then animate out
        setTimeout(function(){
          var main = document.querySelector('section[data-testid="stMain"] .block-container');
          if(main){
            main.style.transition = '';
            main.style.opacity    = '';
            main.style.transform  = '';
          }
        }, 50);
      });
    })();
    </script>
    """, unsafe_allow_html=True)


#landing page
def render_landing():
    inject_bg()
    page_transition_js()
    _, col, _ = st.columns([1, 2.4, 1])
    with col:
        st.markdown('<span class="sp-md"></span>', unsafe_allow_html=True)
        st.markdown("""
        <div class="school-logo-wrapper">
          <div class="school-logo-ring">
            <div class="school-logo-inner">
              <span class="school-logo-placeholder"><i class="fa-solid fa-graduation-cap"></i></span>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-bottom:2.5rem;">
          <div style="font-size:.72rem;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:#2d6a5a;margin-bottom:.7rem;">
            <i class="fa-solid fa-microchip" style="margin-right:6px;color:#10a37f;"></i>Projet de Fin d'Études · 2025 / 2026
          </div>
          <h1 class="glow-title" style="font-size:4.8rem;font-weight:800;color:#10a37f;letter-spacing:-1.5px;margin:0 0 .6rem;line-height:1.1;">
            CHE ~ AUTISM LENS
          </h1>
          <div style="font-size:1.05rem;color:#5a8a7a;font-weight:400;line-height:1.6;">
            Assistant Intelligent pour le Dépistage du<br>
            <span style="color:#7abfb0;font-weight:600;">Trouble du Spectre de l'Autisme (TSA)</span>
          </div>
        </div>""", unsafe_allow_html=True)

        # ── Only Recall stat card, centered ──────────────────────────────────
        _, s_center, _ = st.columns([1, 1, 1])
        with s_center:
            st.markdown('<div class="stat-card"><div class="stat-value">96.88%</div><div class="stat-label"><i class="fa-solid fa-crosshairs" style="margin-right:5px;color:#10a37f;"></i>Recall</div></div>', unsafe_allow_html=True)

        st.markdown('<span class="sp-md"></span>', unsafe_allow_html=True)
        st.markdown("""
        <div class="section-divider">
          <div class="section-divider-line"></div>
          <div class="section-divider-text"><i class="fa-solid fa-circle-info" style="margin-right:5px;"></i>À propos du projet</div>
          <div class="section-divider-line"></div>
        </div>
        <div style="background:rgba(16,163,127,.05);border:1px solid rgba(16,163,127,.15);border-radius:18px;padding:1.5rem 1.8rem;margin-bottom:1.5rem;line-height:1.9;font-size:.88rem;color:#8ab8ad;">
          <p style="margin:0 0 .8rem;"><strong style="color:#10a37f;">CHE – AutismLens</strong> est un assistant conversationnel basé sur l'intelligence artificielle, conçu pour aider les parents, éducateurs et professionnels de santé à identifier les premiers signes du <strong style="color:#7abfb0;">Trouble du Spectre de l'Autisme (TSA)</strong> chez l'enfant.</p>
          <p style="margin:0 0 .8rem;">Face au manque d'outils accessibles et au délai souvent long avant un diagnostic officiel, ce projet propose une solution numérique permettant un <strong style="color:#7abfb0;">pré-dépistage rapide, bienveillant et fiable</strong>, basé sur des critères cliniques reconnus (DSM-5, M-CHAT-R).</p>
          <p style="margin:0;">L'application analyse les comportements décrits par l'utilisateur via un dialogue naturel et génère une évaluation structurée avec des recommandations adaptées — le tout sans remplacer l'avis médical spécialisé.</p>
        </div>""", unsafe_allow_html=True)

        for icon, title, desc in [
            ("fa-comments",      "Dialogue Naturel",            "Interface conversationnelle intuitive, accessible à tous sans formation technique."),
            ("fa-shield-halved", "Basé sur le DSM-5 & M-CHAT-R","Critères cliniques validés internationalement pour un dépistage structuré."),
            ("fa-database",      "Historique Personnalisé",      "Chaque utilisateur dispose d'un compte sécurisé et d'un suivi de ses sessions."),
            ("fa-lock",          "Confidentialité Garantie",     "Aucune donnée partagée avec des tiers. Traitement local et sécurisé."),
        ]:
            st.markdown(f"""
            <div class="feature-row">
              <div class="feature-icon-wrap"><i class="fa-solid {icon}"></i></div>
              <div><div class="feature-text-title">{title}</div><div class="feature-text-desc">{desc}</div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="section-divider" style="margin-top:2.2rem;">
          <div class="section-divider-line"></div>
          <div class="section-divider-text"><i class="fa-solid fa-flask" style="margin-right:5px;"></i>Performances du modèle</div>
          <div class="section-divider-line"></div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
            <div style="margin-bottom:.9rem;">
              <div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:.35rem;">
                <span style="color:#7ab0a5;font-weight:600;">Recall (Sensibilité)</span>
                <span style="color:#10a37f;font-weight:800;">96.88%</span>
              </div>
              <div class="recall-track">
                <div class="recall-fill" style="width:96.88%;background:linear-gradient(90deg,#0a7a5e,#10a37f);"></div>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="section-divider" style="margin-top:2rem;">
          <div class="section-divider-line"></div>
          <div class="section-divider-text"><i class="fa-solid fa-microchip" style="margin-right:5px;"></i>Technologies utilisées</div>
          <div class="section-divider-line"></div>
        </div>""", unsafe_allow_html=True)

        pills = "".join(
            f'<span class="tech-pill"><i class="fa-solid {ic}"></i>{nm}</span>'
            for ic, nm in [
                ("fa-python","Python 3.11"),("fa-brain","NLP / Transformers"),
                ("fa-database","SQLite"),("fa-rocket","Streamlit"),
                ("fa-robot","Scikit-learn"),("fa-fire","PyTorch"),
                ("fa-table-cells","Pandas / NumPy"),("fa-chart-bar","Matplotlib"),
            ]
        )
        st.markdown(f'<div style="text-align:center;margin-bottom:2rem;">{pills}</div>', unsafe_allow_html=True)

        st.markdown('<span class="sp-lg"></span>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:1rem;">
          <div style="font-size:1.1rem;font-weight:700;color:#8abfb5;letter-spacing:-.2px;margin-bottom:.4rem;">Prêt à commencer ?</div>
          <div style="font-size:.82rem;color:var(--muted);">Créez votre compte ou connectez-vous pour accéder à l'assistant.</div>
        </div>""", unsafe_allow_html=True)

        _, cta_col, _ = st.columns([1, 2, 1])
        with cta_col:
            st.markdown('<div class="btn-cta">', unsafe_allow_html=True)
            if st.button("🚀  Accéder à l'Assistant TSA →", key="go_to_auth", use_container_width=True):
                st.session_state.show_landing = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="landing-footer">
          <div style="margin-bottom:.4rem;"><i class="fa-solid fa-shield-halved" style="color:#10a37f;margin-right:5px;"></i>Cet outil est une aide au dépistage et ne remplace pas un diagnostic médical professionnel.</div>
          <div>École Supérieure de Technologie de Guelmim · 2025–2026 · <span style="color:#10a37f;">CHE – AutismLens vbeta</span></div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_auth():
    inject_bg()
    page_transition_js()
    is_login = st.session_state.auth_mode == "login"
    _, col, _ = st.columns([1, 1.15, 1])
    with col:
        st.markdown('<span class="sp-lg"></span>', unsafe_allow_html=True)
        st.markdown('<div class="btn-switch">', unsafe_allow_html=True)
        if st.button("← Retour à l'accueil", key="back_landing", use_container_width=True):
            st.session_state.show_landing = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<span class="sp-sm"></span>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:2rem;">
          <h1 class="glow-title" style="font-size:2.5rem;font-weight:700;color:#10a37f;letter-spacing:-1px;margin:0;">CHE - AUTISM LENS</h1>
        </div>""", unsafe_allow_html=True)

        title = "CONNEXION AU COMPTE" if is_login else "CRÉER UN COMPTE"
        subt  = ("Connectez-vous pour reprendre votre session"
                 if is_login else "Rejoignez l'assistant CHE dès aujourd'hui")
        err = st.empty()

        if is_login:
            with st.container(border=True):
                st.markdown(f'<div style="margin-bottom:1.5rem;"><div style="font-size:1.4rem;font-weight:700;color:#10a37f;letter-spacing:-.4px;margin-bottom:6px;">{title}</div><div style="font-size:.83rem;color:#40635a;line-height:1.5;">{subt}</div></div>', unsafe_allow_html=True)
                with st.form("login_form", clear_on_submit=False, border=False):
                    st.text_input("Nom d'utilisateur", placeholder="estg.admin", key="l_u")
                    st.text_input("Mot de passe", type="password", placeholder="••••••••", key="l_p")
                    st.markdown('<span class="sp-xs"></span>', unsafe_allow_html=True)
                    if st.form_submit_button("Se connecter →", use_container_width=True):
                        u = st.session_state.get("l_u", "")
                        p = st.session_state.get("l_p", "")
                        if u and p:
                            uid = db.get_user(u, hash_password(p))
                            if uid:
                                st.session_state.update(logged_in=True, username=u, user_id=uid)
                                st.rerun()
                            else:
                                err.error("Identifiants incorrects.")
                        else:
                            err.warning("Veuillez remplir tous les champs.")
        else:
            with st.container(border=True):
                st.markdown(f'<div style="margin-bottom:1.5rem;"><div style="font-size:1.4rem;font-weight:700;color:#10a37f;letter-spacing:-.4px;margin-bottom:6px;">{title}</div><div style="font-size:.83rem;color:#40635a;line-height:1.5;">{subt}</div></div>', unsafe_allow_html=True)
                with st.form("reg_form", clear_on_submit=False, border=False):
                    st.text_input("Nom d'utilisateur", placeholder="estg.admin", key="r_u")
                    st.text_input("Adresse email", placeholder="estg.admin@gmail.com", key="r_e")
                    st.text_input("Mot de passe", type="password", placeholder="••••••••", key="r_p")
                    st.text_input("Confirmer le mot de passe", type="password", placeholder="••••••••", key="r_c")
                    st.markdown('<span class="sp-xs"></span>', unsafe_allow_html=True)
                    if st.form_submit_button("Créer mon compte →", use_container_width=True):
                        nu  = st.session_state.get("r_u","").strip()
                        ne  = st.session_state.get("r_e","").strip()
                        np_ = st.session_state.get("r_p","")
                        nc  = st.session_state.get("r_c","")
                        email_re = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        if nu and ne and np_ and nc:
                            if np_ == nc:
                                if not re.match(email_re, ne):
                                    err.error("❌ Format d'email invalide.")
                                elif db.get_user_by_email(ne):
                                    err.error("❌ Cette adresse email est déjà utilisée.")
                                else:
                                    uid = db.add_user(nu, hash_password(np_), ne)
                                    if uid:
                                        st.success("✅ Compte créé ! Connectez-vous maintenant.")
                                        time.sleep(1.5)
                                        st.session_state.auth_mode = "login"
                                        st.rerun()
                                    else:
                                        err.error("❌ Ce nom d'utilisateur est déjà pris.")
                            else:
                                err.error("❌ Les mots de passe ne correspondent pas.")
                        else:
                            err.warning("⚠️ Tous les champs sont obligatoires.")

        st.markdown('<span class="sp-xs"></span>', unsafe_allow_html=True)
        label = "Pas encore de compte ?  S'inscrire →" if is_login else "Déjà un compte ?  Se connecter →"
        key   = "go_reg" if is_login else "go_log"
        st.markdown('<div class="btn-switch">', unsafe_allow_html=True)
        if st.button(label, key=key, use_container_width=True):
            st.session_state.auth_mode = "register" if is_login else "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT PAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_chat():
    initial = (st.session_state.username or "U")[0].upper()

    inject_bg()
    page_transition_js()

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;">
          <div class="brand-mark"><i class="fa-solid fa-brain"></i></div>
          <div>
            <div style="font-size:.92rem;font-weight:700;color:#c0d8d2;letter-spacing:-.2px;">CHE ~ AUTISM LENS</div>
            <div style="font-size:.7rem;color:#2d4840;margin-top:2px;">IA Spécialisée · v1.0</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sb-btn-primary">', unsafe_allow_html=True)
        if st.button("＋  Nouvelle discussion", key="new_chat", use_container_width=True):
            st.session_state.chatbot  = AutismChatbot(st.session_state.user_id)
            st.session_state.messages = []
            st.session_state.typing   = False
            welcome = st.session_state.chatbot.get_response("commencer")
            st.session_state.messages.append({"role": "assistant", "content": welcome})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<span class="sp-md"></span>', unsafe_allow_html=True)
        st.markdown('<span class="section-label">Historique récent</span>', unsafe_allow_html=True)
        for icon, lbl, ts in [
            ("fa-comment-dots",    "Évaluation TSA #1",    "Il y a 2h"),
            ("fa-circle-question", "Questions générales",   "Hier"),
            ("fa-clipboard-list",  "Suivi recommandations", "Lundi"),
        ]:
            st.markdown(f"""
            <div class="hist-item">
              <div class="hist-icon"><i class="fa-solid {icon}"></i></div>
              <div><div class="hist-label">{lbl}</div><div class="hist-ts">{ts}</div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<span class="sp-md"></span>', unsafe_allow_html=True)
        st.markdown("""
        <div class="upgrade-card">
          <div class="upgrade-title"><i class="fa-solid fa-bolt" style="color:#f59e0b;margin-right:5px;"></i>Attention !!</div>
          <div class="upgrade-sub"> L'assistant peut produire des inexactitudes ~ consultez toujours un professionnel de santé.</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<span class="sp-md"></span>', unsafe_allow_html=True)
        st.markdown('<hr>', unsafe_allow_html=True)
        st.markdown('<span class="sp-sm"></span>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="user-pill">
          <div class="user-av-circle">{initial}</div>
          <div style="flex:1;overflow:hidden;">
            <div class="user-name">{st.session_state.username}</div>
            <div class="user-plan"><i class="fa-solid fa-circle" style="font-size:6px;color:#10a37f;margin-right:4px;"></i>Connecté</div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<span class="sp-sm"></span>', unsafe_allow_html=True)
        st.markdown('<div class="sb-btn-danger">', unsafe_allow_html=True)
        if st.button("  Se déconnecter", key="logout", use_container_width=True):
            for k, v in _defaults.items():
                st.session_state[k] = v
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # TOPBAR 
    tl, tr = st.columns([3, 1])
    with tl:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:.4rem 0 .6rem;">
          <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);border-radius:999px;padding:6px 16px;font-size:.78rem;color:#5a8a7a;display:inline-flex;align-items:center;gap:8px;">
            <i class="fa-solid fa-microchip" style="color:#10a37f;font-size:11px;"></i>vBETA
          </div>
        </div>""", unsafe_allow_html=True)
    with tr:
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:flex-end;padding:.4rem 0 .6rem;">
          <span class="status-badge"><span class="status-dot"></span> En ligne</span>
        </div>""", unsafe_allow_html=True)
    st.markdown('<hr>', unsafe_allow_html=True)

    # EMPTY STATE 
    if not st.session_state.messages:
        st.markdown('<span class="sp-md"></span>', unsafe_allow_html=True)
        _, ec, _ = st.columns([1, 2.2, 1])
        with ec:
            st.markdown("""
            <div style="text-align:center;padding:1.5rem 0 1rem;">
              <div class="brand-mark" style="width:56px;height:56px;border-radius:16px;font-size:22px;margin:0 auto 1rem;display:flex;">
                <i class="fa-solid fa-brain"></i>
              </div>
              <div style="font-size:1.7rem;font-weight:700;color:#8aafa5;letter-spacing:-.3px;margin-bottom:.4rem;">CHE ~ AUTISM LENS</div>
              <div style="font-size:.84rem;color:#3d6b5c;line-height:1.65;">
                Posez-moi vos questions sur le Trouble du Spectre de l'Autisme.<br>Je suis là pour vous guider avec bienveillance.
              </div>
            </div>""", unsafe_allow_html=True)
            cc1, cc2 = st.columns(2)
            for i, chip in enumerate(["Qu'est-ce que le TSA ?", "Signes précoces chez l'enfant",
                                       "Comment obtenir un diagnostic ?", "Ressources disponibles"]):
                with (cc1 if i % 2 == 0 else cc2):
                    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
                    if st.button(chip, key=f"chip_{i}", use_container_width=True):
                        st.session_state.messages.append({"role": "user", "content": chip})
                        st.session_state.typing = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # MESSAGES 
    for msg in st.session_state.messages:
        ts      = time.strftime("%H:%M")
        is_user = msg["role"] == "user"
        content = msg["content"]
        if is_user:
            st.markdown(f"""
            <div class="msg-row msg-row-user">
              <div class="msg-content" style="align-items:flex-end;">
                <div class="msg-bubble msg-bubble-user">{content}</div>
                <div class="msg-meta msg-meta-user">
                  <i class="fa-solid fa-check-double" style="color:#10a37f;margin-right:3px;font-size:9px;"></i>{ts}
                </div>
              </div>
              <div class="msg-av msg-av-user"><i class="fa-solid fa-user"></i></div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="msg-row msg-row-bot">
              <div class="msg-av msg-av-bot"><i class="fa-solid fa-brain"></i></div>
              <div class="msg-content" style="align-items:flex-start;">
                <div class="msg-bubble msg-bubble-bot">{content}</div>
                <div class="msg-meta msg-meta-bot">
                  <i class="fa-regular fa-clock" style="margin-right:3px;font-size:9px;"></i>{ts}
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    # Typing indicator
    if st.session_state.typing:
        st.markdown("""
        <div class="msg-row msg-row-bot">
          <div class="msg-av msg-av-bot"><i class="fa-solid fa-brain"></i></div>
          <div class="msg-content" style="align-items:flex-start;">
            <div class="msg-bubble msg-bubble-bot" style="padding:.55rem 1rem;">
              <div class="typing-dots">
                <span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    # DISCLAIMER above chat_input 
    st.markdown("""
    <div class="disclaimer">
      <i class="fa-solid fa-shield-halved" style="margin-right:6px;color:#2d5a4e;"></i>
      L'assistant peut produire des inexactitudes — consultez toujours un professionnel de santé.
    </div>""", unsafe_allow_html=True)

    # st.chat_input — NATIVE Streamlit, always fixed at bottom 
    user_input = st.chat_input("Écrivez votre message…")
    if user_input and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        st.session_state.typing = True
        st.rerun()

    # BOT RESPONSE
    if (
        st.session_state.typing
        and st.session_state.messages
        and st.session_state.messages[-1]["role"] == "user"
    ):
        if st.session_state.chatbot is None:
            st.session_state.chatbot = AutismChatbot(st.session_state.user_id)
        time.sleep(1.0)
        resp = st.session_state.chatbot.get_response(
            st.session_state.messages[-1]["content"])
        st.session_state.messages.append({"role": "assistant", "content": resp})
        st.session_state.typing = False
        st.rerun()


#router
if st.session_state.logged_in:
    render_chat()
elif st.session_state.show_landing:
    render_landing()
else:
    render_auth()