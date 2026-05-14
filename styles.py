"""CSS styles for GFS Kontowechselservice — Light + Dark mode compatible."""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

#MainMenu, footer, header { visibility: hidden; }
.main .block-container { max-width: 820px; padding-top: 1.5rem; }

/* Section headings: follow Streamlit theme automatically */
.section-heading {
    font-weight: 600; font-size: .95rem; margin-bottom: .5rem;
    color: var(--text-color) !important;
}

.gfs-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #fff; padding: 1.3rem 1.8rem; border-radius: 16px;
    margin-bottom: .5rem; box-shadow: 0 4px 24px rgba(26,26,46,.4);
    border-bottom: 3px solid #1a5c52;
}
.gfs-header h1 { margin:0; font-size:1.35rem; font-weight:700; color:#e8a020; }
.gfs-header p { margin:.2rem 0 0; font-size:.78rem; color:rgba(255,255,255,.65); }

.steps-bar { display:flex; gap:.4rem; margin-bottom:1.4rem; justify-content:center; flex-wrap:wrap; }
.step-pill { padding:.4rem .9rem; border-radius:50px; font-size:.72rem; font-weight:600; white-space:nowrap; }
.step-active { background:linear-gradient(135deg,#e8a020,#d4911a); color:#fff; box-shadow:0 2px 12px rgba(232,160,32,.4); }
.step-done { background:#d5f5e3; color:#1a5c52; }
.step-todo { background:#eaecee; color:#999; }

/* Cards: always white bg + dark text (works in both modes) */
.card { background:#fff !important; border:1px solid #e8ecf1; border-radius:16px; padding:1.6rem 1.8rem; margin-bottom:1rem; box-shadow:0 1px 8px rgba(0,0,0,.04); color:#1a1a2e !important; }
.card h3 { margin-top:0; font-size:1.05rem; color:#1a1a2e !important; font-weight:600; }
.card p, .card span, .card strong, .card td { color:#1a1a2e !important; }

.info-box { background:linear-gradient(135deg,#f0faf8,#e0f2ef) !important; border-left:4px solid #1a5c52; border-radius:8px; padding:.9rem 1.1rem; margin:.8rem 0; font-size:.85rem; color:#1a5c52 !important; }
.info-box strong { color:#1a5c52 !important; }
.success-box { background:linear-gradient(135deg,#e8f8f5,#d5f5e3) !important; border-left:4px solid #27ae60; border-radius:8px; padding:.9rem 1.1rem; margin:.8rem 0; font-size:.85rem; color:#1e6e3e !important; }

/* KI partner cards */
.ki-card { background:#fff !important; border:1px solid #e8ecf1; border-radius:12px; padding:.9rem 1.1rem; margin-bottom:.5rem; display:flex; align-items:center; gap:.7rem; font-size:.88rem; color:#1a1a2e !important; }
.ki-card:hover { box-shadow:0 2px 12px rgba(26,92,82,.12); }
.ki-card strong { color:#1a1a2e !important; }
.ki-card .sub { font-size:.78rem; color:#666 !important; }

.status-dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-left:auto; flex-shrink:0; }
.status-label { font-size:.68rem; color:#888 !important; margin-left:.3rem; white-space:nowrap; }
.dot-green { background:#27ae60; }
.dot-yellow { background:#e8a020; }
.dot-red { background:#e74c3c; }

.badge-ok { display:inline-block; background:#d5f5e3; color:#1a5c52 !important; font-size:.72rem; font-weight:600; padding:.15rem .5rem; border-radius:50px; }
.badge-wait { display:inline-block; background:#fef9e7; color:#b7950b !important; font-size:.72rem; font-weight:600; padding:.15rem .5rem; border-radius:50px; }
.badge-err { display:inline-block; background:#fadbd8; color:#c0392b !important; font-size:.72rem; font-weight:600; padding:.15rem .5rem; border-radius:50px; }
.badge-manual { display:inline-block; background:#eaecee; color:#666 !important; font-size:.72rem; font-weight:600; padding:.15rem .5rem; border-radius:50px; }

.terminal { background:#0d1117; color:#58a6ff; border-radius:12px; padding:1rem 1.2rem; font-family:'Courier New',monospace; font-size:.76rem; line-height:1.7; max-height:400px; overflow-y:auto; }
.terminal .ts { color:#7ee787; }
.terminal .msg { color:#c9d1d9; }

.task-row { display:flex; align-items:center; gap:.7rem; padding:.55rem .8rem; border-radius:8px; margin-bottom:.3rem; font-size:.85rem; }
.task-pending { background:#f8f9fa !important; color:#aaa !important; }
.task-running { background:#fef9e7 !important; color:#7d6608 !important; }
.task-done { background:#eafaf1 !important; color:#1a5c52 !important; }

.metric-tile { background:#fff !important; border:1px solid #e8ecf1; border-radius:14px; padding:1.2rem; text-align:center; box-shadow:0 1px 6px rgba(0,0,0,.04); }
.metric-tile .val { font-size:1.6rem; font-weight:700; color:#1a5c52 !important; }
.metric-tile .lbl { font-size:.78rem; color:#666 !important; margin-top:.2rem; }

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #e8a020, #d4911a) !important;
    color: #fff !important; border:none !important; border-radius:10px !important;
    padding:.55rem 1.6rem !important; font-weight:600 !important; font-size:.88rem !important;
    white-space: nowrap !important;
}
div.stButton > button:hover {
    transform:translateY(-1px) !important;
    box-shadow:0 4px 16px rgba(232,160,32,.4) !important;
}
div.stButton > button:disabled {
    background: #ccc !important; color: #888 !important;
    box-shadow: none !important; transform: none !important;
}

/* Sidebar */
.sidebar-logo { background:linear-gradient(135deg,#1a5c52,#1e7a6e); color:#e8a020; width:60px; height:60px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1.1rem; margin-bottom:.6rem; }
.sidebar-stats { background:rgba(128,128,128,.12); border-radius:12px; padding:1rem; font-size:.8rem; line-height:1.8; color: var(--text-color); }
.mf-credit { font-size:.7rem; color:#999; margin-top:1rem; }
.compliance-badge { display:inline-flex; align-items:center; gap:.3rem; background:rgba(26,92,82,.15); border:1px solid #1a5c52; color:#1a5c52; padding:.25rem .6rem; border-radius:50px; font-size:.68rem; font-weight:500; margin:.2rem; }

/* Progress bar gold */
div[data-testid="stProgress"] > div > div > div { background-color: #e8a020 !important; }

@keyframes confetti-fall {
    0% { transform: translateY(-100vh) rotate(0deg); opacity:1; }
    100% { transform: translateY(100vh) rotate(720deg); opacity:0; }
}
.confetti-container { position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:9999; overflow:hidden; }
.confetti-piece { position:absolute; width:10px; height:10px; border-radius:2px; animation: confetti-fall 3s ease-in forwards; }

.gfs-footer { text-align:center; font-size:.7rem; color:#999; margin-top:2rem; padding-top:1rem; border-top:1px solid rgba(128,128,128,.2); }
</style>
"""

CONFETTI_HTML = '<div class="confetti-container">' + "".join([
    '<div class="confetti-piece" style="left:' + str(x) + '%;background:' + c + ';animation-delay:' + str(d) + 's;width:' + str(s) + 'px;height:' + str(s) + 'px;"></div>'
    for x, c, d, s in [
        (5,"#e8a020",0,8),(12,"#1a5c52",0.2,10),(20,"#e8a020",0.5,7),(28,"#7ed321",0.3,9),
        (35,"#f5c518",0.1,11),(42,"#1a5c52",0.6,8),(50,"#e8a020",0.4,10),(58,"#7ed321",0.7,7),
        (65,"#f5c518",0.2,9),(72,"#1a5c52",0.5,11),(80,"#e8a020",0.3,8),(88,"#7ed321",0.1,10),
        (95,"#f5c518",0.6,9),(8,"#1a5c52",0.8,7),(45,"#e8a020",0.9,11),(75,"#7ed321",1.0,8),
    ]
]) + "</div>"
