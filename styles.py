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

/* Timer bar */
.timer-bar {
    background: #1a1a2e; border-radius: 50px; padding: .6rem 1.5rem;
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 1rem; box-shadow: 0 2px 12px rgba(26,26,46,.3);
    flex-wrap: wrap; gap: .3rem;
}
.timer-bar .timer-left { color: #1a5c52; font-weight: 600; font-size: .88rem; }
.timer-bar .timer-left .timer-value { color: #2ecc71; font-family: 'Courier New', monospace; font-weight: 700; }
.timer-bar .timer-right { color: #e8a020; font-size: .82rem; font-weight: 500; }
.timer-bar .timer-right s { color: #e74c3c; }
.timer-saved { color: #2ecc71 !important; font-weight: 700 !important; font-size: .85rem !important; }

/* Persona cards in sidebar */
.persona-card {
    background: rgba(255,255,255,.06); border-radius: 12px; padding: .7rem .9rem;
    margin-bottom: .4rem; cursor: pointer; transition: all .2s;
    font-size: .78rem; line-height: 1.5;
}
.persona-card:hover { background: rgba(255,255,255,.12); }
.persona-card .persona-name { font-weight: 700; font-size: .85rem; }
.persona-card .persona-meta { color: #aaa; font-size: .72rem; }
.persona-badge {
    display: inline-block; padding: .15rem .5rem; border-radius: 50px;
    font-size: .65rem; font-weight: 600; margin-top: .3rem;
}

/* Active persona indicator */
.active-persona { color: var(--text-color); font-size: .8rem; margin-top: .3rem; font-weight: 500; }

/* Critical warning banner */
.warning-banner {
    background: linear-gradient(135deg, #fdedec, #fadbd8) !important;
    border-left: 4px solid #c0392b; border-radius: 8px;
    padding: .9rem 1.1rem; margin: .8rem 0; font-size: .85rem;
    color: #922b21 !important; font-weight: 500;
}
.warning-banner strong { color: #c0392b !important; }

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

.card { background:#fff !important; border:1px solid #e8ecf1; border-radius:16px; padding:1.6rem 1.8rem; margin-bottom:1rem; box-shadow:0 1px 8px rgba(0,0,0,.04); color:#1a1a2e !important; }
.card h3 { margin-top:0; font-size:1.05rem; color:#1a1a2e !important; font-weight:600; }
.card p, .card span, .card strong, .card td { color:#1a1a2e !important; }

.info-box { background:linear-gradient(135deg,#f0faf8,#e0f2ef) !important; border-left:4px solid #1a5c52; border-radius:8px; padding:.9rem 1.1rem; margin:.8rem 0; font-size:.85rem; color:#1a5c52 !important; }
.info-box strong { color:#1a5c52 !important; }
.success-box { background:linear-gradient(135deg,#e8f8f5,#d5f5e3) !important; border-left:4px solid #27ae60; border-radius:8px; padding:.9rem 1.1rem; margin:.8rem 0; font-size:.85rem; color:#1e6e3e !important; }

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

.sidebar-logo { background:linear-gradient(135deg,#1a5c52,#1e7a6e); color:#e8a020; width:60px; height:60px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:1.1rem; margin-bottom:.6rem; }
.sidebar-stats { background:rgba(128,128,128,.12); border-radius:12px; padding:1rem; font-size:.8rem; line-height:1.8; color: var(--text-color); }
.mf-credit { font-size:.7rem; color:#999; margin-top:1rem; }
.compliance-badge { display:inline-flex; align-items:center; gap:.3rem; background:rgba(26,92,82,.15); border:1px solid #1a5c52; color:#1a5c52; padding:.25rem .6rem; border-radius:50px; font-size:.68rem; font-weight:500; margin:.2rem; }

div[data-testid="stProgress"] > div > div > div { background-color: #e8a020 !important; }

@keyframes confetti-fall {
    0% { transform: translateY(-100vh) rotate(0deg); opacity:1; }
    100% { transform: translateY(100vh) rotate(720deg); opacity:0; }
}
.confetti-container { position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:9999; overflow:hidden; }
.confetti-piece { position:absolute; width:10px; height:10px; border-radius:2px; animation: confetti-fall 3s ease-in forwards; }

.gfs-footer { text-align:center; font-size:.7rem; color:#999; margin-top:2rem; padding-top:1rem; border-top:1px solid rgba(128,128,128,.2); }

/* --- FEATURE 1: Risiko-Ampel --- */
.risk-red { border-left: 4px solid #c0392b !important; }
.risk-orange { border-left: 4px solid #e8a020 !important; }
.risk-green { border-left: 4px solid #1a5c52 !important; }

.risk-badge-red { background: #fadbd8; color: #c0392b; font-size: .65rem; font-weight: 700; padding: .15rem .5rem; border-radius: 50px; }
.risk-badge-orange { background: #fef9e7; color: #b7950b; font-size: .65rem; font-weight: 700; padding: .15rem .5rem; border-radius: 50px; }
.risk-badge-green { background: #d5f5e3; color: #1a5c52; font-size: .65rem; font-weight: 700; padding: .15rem .5rem; border-radius: 50px; }

/* --- FEATURE 2: Kryptische SEPA Cards --- */
.cryptic-card {
    background: #1a1a2e; border-left: 4px solid #1a5c52; border-radius: 8px;
    padding: .8rem 1rem; margin-bottom: .6rem; color: #fff; font-family: 'Inter', sans-serif;
}
.cryptic-card .code { font-family: 'Courier New', monospace; color: #e8a020; font-weight: 700; font-size: .9rem; margin-bottom: .3rem; }
.cryptic-card .identified { font-weight: 600; font-size: .85rem; color: #2ecc71; margin-bottom: .3rem; }
.cryptic-card .reason { font-size: .75rem; color: #aaa; }
.stat-highlight {
    background: rgba(26,92,82,.1); border: 1px solid #1a5c52; border-radius: 8px;
    padding: 1rem; text-align: center; margin-top: 1rem;
}
.stat-highlight .stat-number { color: #e8a020; font-size: 1.8rem; font-weight: 700; display: block; margin-bottom: .3rem; }
.stat-highlight .stat-text { color: var(--text-color); font-size: .85rem; }

/* --- FEATURE 3: Berater-Ansicht --- */
.consultant-mode { border-top: 4px solid #1a5c52; }
.consultant-badge {
    position: absolute; top: -10px; right: 10px; background: #1a5c52; color: #fff;
    font-size: .65rem; font-weight: 700; padding: .2rem .6rem; border-radius: 4px;
}
.audit-log-container {
    background: #0d1117; color: #c9d1d9; border-radius: 12px; padding: 1rem;
    font-family: 'Courier New', monospace; font-size: .75rem; max-height: 500px; overflow-y: auto;
}
.audit-log-container .ts { color: #7ee787; }
.audit-log-container .info { color: #58a6ff; }
.audit-log-container .warn { color: #e8a020; }
.audit-log-container .err { color: #f85149; }
.checklist-item { font-size: .8rem; margin-bottom: .4rem; display: flex; align-items: center; gap: .5rem; }
.checklist-item.done { color: #2ecc71; }
.biz-metric {
    background: #fff; border: 1px solid #e8ecf1; border-radius: 8px; padding: 1rem;
    text-align: center; height: 100%; box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.biz-metric .val { font-size: 1.5rem; font-weight: 700; color: #1a1a2e; }
.biz-metric .lbl { font-size: .75rem; color: #666; margin-top: .3rem; }
.biz-metric.highlight .val { color: #2ecc71; }
/* --- FEATURE 1: IBAN Validation --- */
.iban-validation { padding: .7rem 1rem; border-radius: 8px; font-size: .85rem; margin-top: -.5rem; margin-bottom: 1rem; }
.iban-error { background: #fadbd8; border: 1px solid #c0392b; color: #922b21; }
.iban-success { background: #d5f5e3; border: 1px solid #27ae60; color: #1e6e3e; }
.iban-validation strong { color: inherit !important; }

/* --- FEATURE 2: Custom Progress Bar --- */
.custom-progress-wrapper { margin-top: 1rem; margin-bottom: 1.5rem; text-align: center; }
.custom-progress-bg { background: #1a1a2e; height: 6px; border-radius: 3px; width: 100%; overflow: hidden; }
.custom-progress-fill { height: 100%; background: linear-gradient(90deg, #1a5c52, #00d4aa); transition: width 1s ease-in-out; }
.custom-progress-text { font-size: .8rem; color: #666; margin-top: .5rem; }
.custom-progress-text-gold { font-size: .85rem; color: #e8a020; font-weight: 700; margin-top: .5rem; }

/* --- FEATURE 3: Step 0 Intro --- */
.intro-container { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.intro-col { border-radius: 16px; padding: 1.5rem; color: #fff !important; flex: 1; display: flex; flex-direction: column; gap: 1rem; }
.intro-col * { color: #fff !important; }
.intro-left { background: #1a0a0a; border: 1px solid #4a1c1c; }
.intro-right { background: #0a1a16; border: 1px solid #1a5c52; }
.intro-col h2 { margin: 0; font-size: 1.25rem; font-weight: 700; border-bottom: 1px solid rgba(255,255,255,.2); padding-bottom: .5rem; }

.intro-timeline { margin-top: 1rem; flex-grow: 1; }
.intro-timeline-item { display: flex; gap: 1rem; margin-bottom: 1rem; font-size: .85rem; line-height: 1.4; }
.intro-timeline-item .time { font-weight: 700; min-width: 70px; opacity: .8; }
.intro-timeline-item .desc { flex: 1; }

.intro-metric-row { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1rem; }
.intro-metric { background: rgba(255,255,255,.05); border-radius: 8px; padding: .8rem; flex: 1; min-width: 120px; text-align: center; }
.intro-left .intro-metric { border-top: 2px solid #e74c3c; }
.intro-right .intro-metric { border-top: 2px solid #2ecc71; }
.intro-metric .val { font-size: 1.3rem; font-weight: 700; display: block; margin-bottom: .2rem; }
.intro-left .intro-metric .val { color: #e74c3c !important; }
.intro-right .intro-metric .val { color: #e8a020 !important; }
.intro-metric .lbl { font-size: .7rem; opacity: .7; text-transform: uppercase; letter-spacing: .5px; }

.intro-cta-wrapper { text-align: center; margin-top: 1rem; margin-bottom: 2rem; }
.intro-cta-wrapper button { font-size: 1.1rem !important; padding: .8rem 2.5rem !important; border-radius: 50px !important; }
.compliance-pill { display: inline-block; background: #eaecee; color: #555; border-radius: 50px; padding: .2rem .7rem; font-size: .7rem; font-weight: 600; margin-right: .5rem; margin-top: .5rem; }

/* --- FEATURE 1 & 2: Warnings & Chat --- */
.completeness-warning { border-left: 4px solid #e8a020; background: #fffaf0; padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem; }
.gabi-warning { background: #c0392b; color: #fff; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; font-weight: 600; text-align: center; }

/* Chat Container Positioning via :has() */
div[data-testid="stVerticalBlock"]:has(.chat-marker) {
    position: fixed !important;
    bottom: 20px !important;
    right: 20px !important;
    z-index: 99999 !important;
    width: 320px !important;
    background: #111827 !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
    padding: 1rem !important;
    border: 1px solid #374151;
    transition: all 0.3s ease;
}

div[data-testid="stVerticalBlock"]:has(.chat-marker.chat-closed) {
    width: auto !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.chat-marker { display: none; }

.chat-header {
    display: flex; justify-content: space-between; align-items: center;
    border-bottom: 1px solid #374151; padding-bottom: .8rem; margin-bottom: 1rem;
}
.chat-title { color: #2ecc71; font-weight: 600; font-size: .95rem; display: flex; align-items: center; gap: 8px; }
.chat-dot { width: 8px; height: 8px; background: #2ecc71; border-radius: 50%; box-shadow: 0 0 5px #2ecc71; }

.chat-msg { margin-bottom: .8rem; padding: .6rem .8rem; border-radius: 8px; font-size: .85rem; line-height: 1.4; max-width: 90%; clear: both; }
.chat-bot { background: #1e293b; color: #f8fafc; float: left; border-bottom-left-radius: 2px; }
.chat-user { background: #e8a020; color: #1a1a2e; float: right; border-bottom-right-radius: 2px; font-weight: 500; }
.chat-clear { clear: both; margin-bottom: 1rem; }

/* Override streamlit buttons inside chat */
div[data-testid="stVerticalBlock"]:has(.chat-marker) button {
    width: 100% !important; border-radius: 6px !important;
    padding: .4rem !important; min-height: 0 !important;
    font-size: .8rem !important; border: 1px solid #475569 !important;
    background: #1e293b !important; color: #f8fafc !important;
}
div[data-testid="stVerticalBlock"]:has(.chat-marker) button:hover {
    border-color: #2ecc71 !important; color: #2ecc71 !important;
}
/* Main floating button */
div[data-testid="stVerticalBlock"]:has(.chat-marker.chat-closed) button {
    background: #1a5c52 !important; border: none !important; color: white !important;
    border-radius: 50px !important; padding: .6rem 1.2rem !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important; font-size: .9rem !important;
    font-weight: 600 !important;
}

/* --- FEATURE 1 & 2 (Tech Credibility): Terminal & SEPA Decoder --- */
.terminal-box {
    background: #0a0e1a; color: #a5b4fc; font-family: 'Courier New', monospace;
    padding: 1.5rem; border-radius: 8px; border: 1px solid #1e293b; min-height: 220px;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
}
.term-line { margin-bottom: 0.4rem; font-size: 0.85rem; line-height: 1.4; }
.term-ok { color: #2ecc71; font-weight: bold; }
.term-muted { color: #475569; font-size: 0.75rem; float: right; }

.connection-diagram { display: flex; justify-content: space-between; align-items: center; margin: 1rem 0; font-family: 'Courier New', monospace; font-size: 0.8rem; }
.conn-box { background: #1e293b; padding: 0.5rem 0.8rem; border-radius: 4px; border: 1px solid #475569; color: white; text-align: center; }
.conn-line { flex-grow: 1; height: 2px; background: repeating-linear-gradient(90deg, #2ecc71 0, #2ecc71 10px, transparent 10px, transparent 20px); background-size: 40px 100%; animation: dash 1s linear infinite; margin: 0 10px; position: relative; }
.conn-line::after { content: attr(data-label); position: absolute; top: -18px; left: 50%; transform: translateX(-50%); font-size: 0.7rem; color: #a5b4fc; white-space: nowrap; }
@keyframes dash { to { background-position: 40px 0; } }

.decoder-result {
    border: 1px solid #1a5c52; background: rgba(26,92,82,0.05); padding: 1rem;
    border-radius: 8px; margin-top: 1rem; font-family: 'Courier New', monospace;
    color: #333; font-size: 0.85rem;
}
.decoder-result strong { color: #1a5c52; }
.decoder-error { color: #c0392b; font-weight: bold; font-family: 'Courier New', monospace; margin-top: 0.5rem; }

/* Premium Features CSS */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}
.metric-card {
    background: #fff;
    border: 1px solid #e1e4e8;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a5c52;
}
.metric-label {
    font-size: 0.85rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.email-simulation {
    background: #f8f9fa;
    border: 1px solid #dfe1e5;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 25px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.email-header {
    background: #fff;
    padding: 15px 20px;
    border-bottom: 1px solid #dfe1e5;
}
.email-header-row {
    display: flex;
    margin-bottom: 5px;
    font-size: 0.9rem;
}
.email-header-label {
    color: #666;
    width: 60px;
    font-weight: 500;
}
.email-header-value {
    color: #202124;
}
.email-body {
    padding: 25px;
    background: #fff;
    color: #3c4043;
    font-size: 0.95rem;
    line-height: 1.5;
}
.email-attachment {
    display: inline-flex;
    align-items: center;
    padding: 8px 12px;
    border: 1px solid #dadce0;
    border-radius: 18px;
    font-size: 0.85rem;
    color: #1a73e8;
    background: #fff;
    margin-right: 10px;
    margin-top: 15px;
    font-weight: 500;
}
.interactive-hitl {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed #eee;
}
.hitl-feedback {
    font-size: 0.75rem;
    color: #1a5c52;
    background: #e8f5e9;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 600;
    animation: fadeInOut 2s ease-in-out;
}
@keyframes fadeInOut {
    0% { opacity: 0; transform: scale(0.9); }
    10% { opacity: 1; transform: scale(1); }
    80% { opacity: 1; transform: scale(1); }
    100% { opacity: 0.7; }
}
/* Premium Visuals CSS */
.hero-section {
    text-align: center;
    padding: 60px 20px 40px;
    background: linear-gradient(180deg, #f0f7f6 0%, #ffffff 100%);
    border-radius: 16px;
    margin-bottom: 30px;
    border: 1px solid #e8f0ef;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 15px;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 1.2rem;
    color: #666;
    max-width: 600px;
    margin: 0 auto 30px;
    line-height: 1.5;
}
.e-signature-box {
    background: #fdfdfd;
    border: 1px dashed #1a5c52;
    border-radius: 8px;
    padding: 15px;
    margin-top: 20px;
    text-align: center;
    font-family: 'Courier New', Courier, monospace;
    color: #1a5c52;
}
.e-signature-box .seal {
    font-weight: bold;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}
.skeleton-card {
    background: #fff;
    border: 1px solid #e1e4e8;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 15px;
}
.skeleton-avatar {
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background: #eee;
    animation: shimmer 1.5s infinite linear;
}
.skeleton-line-1 {
    width: 60%;
    height: 14px;
    background: #eee;
    border-radius: 4px;
    margin-bottom: 8px;
    animation: shimmer 1.5s infinite linear;
}
.skeleton-line-2 {
    width: 40%;
    height: 12px;
    background: #eee;
    border-radius: 4px;
    animation: shimmer 1.5s infinite linear;
}
@keyframes shimmer {
    0% { background-color: #eee; }
    50% { background-color: #f8f8f8; }
    100% { background-color: #eee; }
}
/* Next-Gen AI CSS */
.fraud-alert {
    background: #fff0f0;
    border: 2px solid #ff4d4f;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 25px;
    display: flex;
    align-items: flex-start;
    gap: 15px;
    box-shadow: 0 4px 12px rgba(255, 77, 79, 0.15);
    animation: pulse-red 2s infinite;
}
@keyframes pulse-red {
    0% { box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(255, 77, 79, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 77, 79, 0); }
}
.fraud-icon {
    font-size: 2rem;
    line-height: 1;
}
.canceled-partner {
    opacity: 0.5;
    text-decoration: line-through;
    background: #fafafa !important;
    border-color: #eee !important;
}
.canceled-badge {
    color: #e74c3c;
    font-size: 0.75rem;
    font-weight: bold;
    border: 1px solid #e74c3c;
    padding: 2px 6px;
    border-radius: 4px;
    display: inline-block;
    margin-top: 5px;
    text-decoration: none !important;
}
.eco-card {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    border: 1px solid #a5d6a7;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.eco-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #2e7d32;
}
.eco-label {
    font-size: 0.85rem;
    color: #1b5e20;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.chat-container {
    background: #f8f9fa;
    border: 1px solid #e1e4e8;
    border-radius: 12px;
    padding: 20px;
    margin-top: 30px;
}
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
