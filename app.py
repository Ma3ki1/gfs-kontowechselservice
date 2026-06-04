"""
GFS Kontowechselservice — KI-Prototyp
Global Finance Solutions SE | Powered by metafinanz
"""
import streamlit as st
import time, re, random, copy
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, timedelta, datetime
from styles import CSS, CONFETTI_HTML
from mock_data import (DEMO_CUSTOMER, BANK_SUGGESTIONS, AI_DETECTED_PARTNERS,
                       RHYTHM_LABELS, PERSONAS)
from pdf_generator import generate_confirmation_pdf, generate_audit_pdf
import importlib
import pdf_generator
importlib.reload(pdf_generator)
from pdf_generator import generate_confirmation_pdf, generate_audit_pdf

st.set_page_config(page_title="GFS Kontowechselservice", page_icon="", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
BASELINE_DAYS = 16

def validate_iban(iban):
    # Check if format is DE + 2 digits + 18 digits = 22 chars
    iban_clean = iban.replace(" ", "").upper()
    return bool(re.fullmatch(r"DE\d{20}", iban_clean))

def format_iban(iban):
    # Remove spaces and uppercase
    iban_clean = iban.replace(" ", "").upper()
    # Chunk into groups of 4
    return " ".join(iban_clean[i:i+4] for i in range(0, len(iban_clean), 4))

def format_iban_callback():
    if "s1_iban_input" in st.session_state:
        st.session_state["s1_iban_input"] = format_iban(st.session_state["s1_iban_input"])

def biz_days_ahead(start, days):
    cur = start
    added = 0
    while added < days:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            added += 1
    return cur

def gen_gfs_iban():
    digits = "".join([str(random.randint(0, 9)) for _ in range(12)])
    return format_iban("DE89 2004 0060 " + digits[:4] + digits[4:8] + digits[8:])

def init_state():
    d = dict(
        step=0, name="", geburtsdatum=date(1990,1,1), iban_alt="", bank_alt="",
        cons_daten=False, cons_verarb=False, cons_mensch=False,
        partners=None, manual_partners=[], ki_done=False,
        iban_neu="", wechseldatum=None,
        sim_done=False, nps_score=None, demo_mode=False,
        start_time=None, end_time=None,
        active_persona=None, view_mode="kunde",
        sim_task_idx=0,  # For Step 4 progress tracking
        warning_dismissed=False, chat_open=False, chat_stage="init"
    )
    for k, v in d.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if not st.session_state.iban_neu:
        st.session_state.iban_neu = gen_gfs_iban()
    if st.session_state.partners is None:
        st.session_state.partners = copy.deepcopy(AI_DETECTED_PARTNERS)
        for p in st.session_state.partners:
            p["selected"] = True

def apply_demo():
    persona_id = st.session_state.get("active_persona")
    if persona_id and persona_id in PERSONAS:
        apply_persona(persona_id)
    else:
        d = DEMO_CUSTOMER
        st.session_state.name = d["name"]
        st.session_state.geburtsdatum = d["geburtsdatum"]
        st.session_state.iban_alt = format_iban(d["iban_alt"])
        st.session_state.bank_alt = d["bank_alt"]
        st.session_state.cons_daten = True
        st.session_state.cons_verarb = True
        st.session_state.cons_mensch = True
        st.session_state.ki_done = False
        st.session_state.wechseldatum = biz_days_ahead(date.today(), 12)
        st.session_state.step = 1
        st.session_state["s1_name_input"] = d["name"]
        st.session_state["s1_iban_input"] = format_iban(d["iban_alt"])
        st.session_state["s1_bank_select"] = d["bank_alt"]
        st.session_state["s1_geb_input"] = d["geburtsdatum"]
        st.session_state["s1_cons_daten_cb"] = True
        st.session_state["s1_cons_verarb_cb"] = True
        st.session_state["s1_cons_mensch_cb"] = True

def apply_persona(persona_id):
    """Load all data for a persona profile."""
    p = PERSONAS[persona_id]
    cust = p["customer"]
    st.session_state.active_persona = persona_id
    st.session_state.name = cust["name"]
    st.session_state.geburtsdatum = cust["geburtsdatum"]
    st.session_state.iban_alt = format_iban(cust["iban_alt"])
    st.session_state.bank_alt = cust["bank_alt"]
    st.session_state.cons_daten = True
    st.session_state.cons_verarb = True
    st.session_state.cons_mensch = True
    st.session_state.ki_done = False
    st.session_state.wechseldatum = biz_days_ahead(date.today(), 12)
    st.session_state.partners = copy.deepcopy(p["partners"])
    for partner in st.session_state.partners:
        partner["selected"] = True
    st.session_state.manual_partners = []
    st.session_state.sim_done = False
    st.session_state.nps_score = None
    st.session_state.end_time = None
    st.session_state.step = 1
    st.session_state.warning_dismissed = False
    st.session_state.chat_open = False
    st.session_state.chat_stage = "init"
    
    st.session_state["s1_name_input"] = cust["name"]
    st.session_state["s1_iban_input"] = format_iban(cust["iban_alt"])
    st.session_state["s1_bank_select"] = cust["bank_alt"]
    st.session_state["s1_geb_input"] = cust["geburtsdatum"]
    st.session_state["s1_cons_daten_cb"] = True
    st.session_state["s1_cons_verarb_cb"] = True
    st.session_state["s1_cons_mensch_cb"] = True

def conf_dot(confidence):
    if confidence >= 90:
        return '<span class="status-dot dot-green"></span><span class="status-label">Automatisch erkannt</span>'
    elif confidence >= 70:
        return '<span class="status-dot dot-yellow"></span><span class="status-label">Bitte pr\u00fcfen</span>'
    else:
        return '<span class="status-dot dot-red"></span><span class="status-label">Bitte pr\u00fcfen</span>'

def get_risk_level(partner):
    cat = partner.get("category", "")
    name = partner.get("name", "").lower()
    
    if cat in ["gehalt", "dauerauftrag"]:
        return (0, "Kritisch \u2014 sofort umstellen", "red")
    
    crit_keywords = ["miete", "kita", "unterhalt", "stadtwerke", "strom", "gas", "krankenversicherung", "aok", "tk", "barmer"]
    if any(k in name for k in crit_keywords):
        return (0, "Kritisch \u2014 sofort umstellen", "red")
        
    warn_keywords = ["telekom", "versicherung", "adac", "steuerberater", "internet", "festnetz", "huk", "allianz"]
    if any(k in name for k in warn_keywords):
        return (1, "Wichtig", "orange")
        
    return (2, "Unkritisch", "green")

# ── Timer ────────────────────────────────────────────────────────────────────
def render_timer():
    """Show elapsed time bar at the top of every step."""
    if st.session_state.start_time is None:
        return

    if st.session_state.end_time:
        elapsed = st.session_state.end_time - st.session_state.start_time
    else:
        elapsed = datetime.now() - st.session_state.start_time

    total_secs = int(elapsed.total_seconds())
    hrs = total_secs // 3600
    mins = (total_secs % 3600) // 60
    secs = total_secs % 60
    time_str = "{:02d}:{:02d}:{:02d}".format(hrs, mins, secs)

    if st.session_state.step == 5 and st.session_state.end_time:
        baseline_secs = BASELINE_DAYS * 24 * 3600
        saved_secs = baseline_secs - total_secs
        saved_days = saved_secs // 86400
        saved_hrs = (saved_secs % 86400) // 3600
        saved_mins = (saved_secs % 3600) // 60
        saved_str = str(saved_days) + " Tage, " + str(saved_hrs) + " Stunden und " + str(saved_mins) + " Minuten"
        right_html = '<span class="timer-saved">Sie haben ' + saved_str + ' gespart.</span>'
    else:
        right_html = '<span class="timer-right">Klassischer Wechsel: <s>\u00d8 ' + str(BASELINE_DAYS) + ' Tage</s></span>'

    st.markdown(
        '<div class="timer-bar">'
        '<span class="timer-left">Ihr Wechsel l\u00e4uft seit: '
        '<span class="timer-value" id="live-timer">' + time_str + '</span></span>'
        + right_html +
        '</div>', unsafe_allow_html=True)
        
    if st.session_state.end_time is None:
        start_ts = int(st.session_state.start_time.timestamp())
        js_code = f"""
        <script>
            const startTime = {start_ts};
            const updateTimer = () => {{
                const target = window.parent.document.getElementById('live-timer');
                if (!target) return;
                const now = Math.floor(Date.now() / 1000);
                let diff = now - startTime;
                if (diff < 0) diff = 0;
                const h = Math.floor(diff / 3600).toString().padStart(2, '0');
                const m = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
                const s = (diff % 60).toString().padStart(2, '0');
                target.innerText = `${{h}}:${{m}}:${{s}}`;
            }};
            setInterval(updateTimer, 1000);
        </script>
        """
        components.html(js_code, height=0, width=0)

# ── Layout ───────────────────────────────────────────────────────────────────
def render_header():
    st.markdown("""<div class="gfs-header">
        <h1>Global Finance Solutions SE</h1>
        <p>KI-Kontowechselservice &mdash; SteerCo Prototyp 09.06.2026</p>
    </div>""", unsafe_allow_html=True)
    
    # View Mode Toggle
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        if st.button("Kundenansicht", type="primary" if st.session_state.view_mode == "kunde" else "secondary", use_container_width=True):
            st.session_state.view_mode = "kunde"
            st.rerun()
    with c2:
        if st.button("Berateransicht", type="primary" if st.session_state.view_mode == "berater" else "secondary", use_container_width=True):
            st.session_state.view_mode = "berater"
            st.rerun()
def render_steps(cur):
    if cur == 0:
        return # Hide step bar on Intro page
        
    labels = ["1 Identifikation","2 KI-Analyse","3 Neues Konto","4 \u00dcbertragung","5 Abschluss"]
    pills = ""
    for i, l in enumerate(labels, 1):
        cls = "step-done" if i < cur else ("step-active" if i == cur else "step-todo")
        pills += '<span class="step-pill ' + cls + '">' + l + '</span>'
    
    html = '<div class="steps-bar">' + pills + '</div>'
    
    # Calculate custom progress percentage
    pct = 0
    if cur == 1:
        pct = 10
    elif cur == 2:
        base = 20
        total_p = len(st.session_state.partners)
        if total_p > 0:
            sel_count = sum(1 for p in st.session_state.partners if p.get("selected", False))
            pct = base + int((sel_count / total_p) * 20)
        else:
            pct = 40
    elif cur == 3:
        pct = 60
    elif cur == 4:
        pct = 60 + st.session_state.get("sim_progress_pct", 0)
    elif cur == 5:
        pct = 100

    text_html = f'<div class="custom-progress-text">Ihr Wechsel ist zu {pct}% abgeschlossen</div>'
    if cur == 5:
        text_html = '<div class="custom-progress-text-gold">Wechsel erfolgreich abgeschlossen</div>'
        
    html += f'''
    <div class="custom-progress-wrapper">
        <div class="custom-progress-bg">
            <div class="custom-progress-fill" style="width: {pct}%;"></div>
        </div>
        {text_html}
    </div>
    '''
    
    if "steps_placeholder" in st.session_state:
        st.session_state.steps_placeholder.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">GFS</div>', unsafe_allow_html=True)
        st.markdown("**Global Finance Solutions SE**")
        st.markdown("Schritt **" + str(st.session_state.step) + "** von **5**")
        st.progress(st.session_state.step / 5)
        st.divider()

        if st.session_state.active_persona:
            pdata = PERSONAS[st.session_state.active_persona]
            st.markdown('<div class="active-persona">Aktives Profil: <strong>' + pdata["label"] + '</strong></div>', unsafe_allow_html=True)
            st.divider()

        if st.toggle("Demo-Modus", key="sidebar_demo_toggle"):
            if not st.session_state.demo_mode:
                st.session_state.demo_mode = True
                apply_demo()
                st.rerun()
        elif st.session_state.demo_mode:
            st.session_state.demo_mode = False
        st.divider()
        st.markdown("""<div class="sidebar-stats">
            <strong>Ihr Wechsel im Vergleich:</strong><br>
            Alt: 14-21 Tage &rarr; GFS KI: Unter 2 Tage<br>
            Alt: NPS -12 &rarr; Ziel: NPS +50<br>
            Alt: 73% Erfolg &rarr; Ziel: 95%+
        </div>""", unsafe_allow_html=True)
        st.divider()
        st.markdown("""<div class="compliance-badge">DSGVO Art. 22 konform</div>
            <div class="compliance-badge">Human-in-the-Loop</div>
            <div class="compliance-badge">EU AI Act konform</div>""", unsafe_allow_html=True)
        st.markdown('<div class="mf-credit">Konzept &amp; Prototyp by <strong>metafinanz</strong><br>technologie. kultur. netzwerke.</div>', unsafe_allow_html=True)

def render_footer():
    st.markdown("""<div class="gfs-footer">
        Global Finance Solutions SE &middot; Zahlungskontengesetz (ZKG) &sect;&sect; 20-26 &middot; EU-Richtlinie 2014/92/EU<br>
        EU AI Act: Hochrisiko-KI-System (Annex III) &middot; DSGVO Art. 22 konform<br>
        Powered by <strong>metafinanz</strong> Informationssysteme GmbH (Allianz Gruppe)
    </div>""", unsafe_allow_html=True)

# ── Step 0 ───────────────────────────────────────────────────────────────────
def page_step0():
    st.markdown('<div class="intro-container">', unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('''
        <div class="intro-col intro-left">
            <h2>Kontowechsel heute bei GFS</h2>
            <div class="intro-timeline">
                <div class="intro-timeline-item">
                    <span class="time">Tag 1:</span>
                    <span class="desc">Kunde erh\u00e4lt 47-seitiges PDF-Dokument</span>
                </div>
                <div class="intro-timeline-item">
                    <span class="time">Tag 3:</span>
                    <span class="desc">Manuelle Recherche aller Zahlungspartner</span>
                </div>
                <div class="intro-timeline-item">
                    <span class="time">Tag 7:</span>
                    <span class="desc">Einzelne Kontaktaufnahme mit jedem Partner</span>
                </div>
                <div class="intro-timeline-item">
                    <span class="time">Tag 14:</span>
                    <span class="desc">Erste Best\u00e4tigungen eingegangen</span>
                </div>
                <div class="intro-timeline-item">
                    <span class="time">Tag 21:</span>
                    <span class="desc">Wechsel m\u00f6glicherweise abgeschlossen</span>
                </div>
            </div>
            <div class="intro-metric-row">
                <div class="intro-metric">
                    <span class="val">\u00d8 16 Tage</span>
                    <span class="lbl">Wechseldauer</span>
                </div>
                <div class="intro-metric">
                    <span class="val">73%</span>
                    <span class="lbl">Erfolgsquote</span>
                </div>
                <div class="intro-metric">
                    <span class="val">-12</span>
                    <span class="lbl">NPS</span>
                </div>
                <div class="intro-metric">
                    <span class="val">127 &euro;</span>
                    <span class="lbl">Kosten pro Fall</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col_right:
        st.markdown('''
        <div class="intro-col intro-right">
            <h2 style="color:#2ecc71 !important;">Kontowechsel mit KI-Service</h2>
            <div class="intro-timeline">
                <div class="intro-timeline-item">
                    <span class="time">Minute 1:</span>
                    <span class="desc">Zugang zur alten Bank gew\u00e4hren (PSD2)</span>
                </div>
                <div class="intro-timeline-item">
                    <span class="time">Minute 2:</span>
                    <span class="desc">KI analysiert alle Zahlungspartner automatisch</span>
                </div>
                <div class="intro-timeline-item">
                    <span class="time">Minute 3:</span>
                    <span class="desc">Erkannte Partner best\u00e4tigen</span>
                </div>
                <div class="intro-timeline-item">
                    <span class="time">Minute 5:</span>
                    <span class="desc">Automatische Benachrichtigung aller Partner</span>
                </div>
                <div class="intro-timeline-item" style="color:#2ecc71 !important; font-weight:700;">
                    <span class="time" style="color:inherit !important;">Tag 2:</span>
                    <span class="desc" style="color:inherit !important;">Wechsel vollst\u00e4ndig abgeschlossen</span>
                </div>
            </div>
            <div class="intro-metric-row">
                <div class="intro-metric">
                    <span class="val">< 2 Tage</span>
                    <span class="lbl">Wechseldauer</span>
                </div>
                <div class="intro-metric">
                    <span class="val">Ziel 95%+</span>
                    <span class="lbl">Erfolgsquote</span>
                </div>
                <div class="intro-metric">
                    <span class="val">Ziel +50</span>
                    <span class="lbl">NPS</span>
                </div>
                <div class="intro-metric">
                    <span class="val">25 &euro;</span>
                    <span class="lbl">Kosten pro Fall</span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="intro-cta-wrapper">', unsafe_allow_html=True)
    if st.button("KI-Kontowechsel jetzt starten", type="primary"):
        st.session_state.step = 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Step 1 ───────────────────────────────────────────────────────────────────
def page_step1():
    # Start the timer on first Step 1 load
    if st.session_state.start_time is None:
        st.session_state.start_time = datetime.now()

    # Persona selector — prominent cards
    st.markdown('<p class="section-heading">Schnellstart: Demo-Profil w\u00e4hlen</p>', unsafe_allow_html=True)
    col_n, col_t, col_g = st.columns(3)
    for col, pid in [(col_n, "nina"), (col_t, "thomas"), (col_g, "gabi")]:
        pdata = PERSONAS[pid]
        is_active = st.session_state.active_persona == pid
        border_w = "3px" if is_active else "1px"
        shadow = "0 4px 16px rgba(0,0,0,.15)" if is_active else "0 1px 6px rgba(0,0,0,.04)"
        with col:
            st.markdown(
                '<div style="background:#fff;border-left:4px solid ' + pdata["color"] + ';border-radius:14px;'
                'padding:1rem 1.1rem;box-shadow:' + shadow + ';margin-bottom:.5rem;">'
                '<div style="font-weight:700;font-size:.95rem;color:' + pdata["color"] + ';">' + pdata["label"] + '</div>'
                '<div style="font-size:.78rem;color:#666;margin:.3rem 0;line-height:1.5;">'
                + str(pdata["alter"]) + ' Jahre<br>' + pdata["beruf"] + '<br>Bank: ' + pdata["bank"] + '</div>'
                '<span style="display:inline-block;background:' + pdata["color"] + '18;color:' + pdata["color"] + ';'
                'padding:.15rem .6rem;border-radius:50px;font-size:.68rem;font-weight:600;">'
                + pdata["badge"] + '</span>'
                '</div>', unsafe_allow_html=True)
            if st.button(pdata["label"].split(" ")[-1] + " laden", key="persona_btn_" + pid, use_container_width=True):
                apply_persona(pid)
                st.session_state.step = 1
                st.session_state.start_time = datetime.now()
                st.session_state.end_time = None
                st.rerun()

    st.markdown('---')
    st.markdown('<div class="card"><h3>Schritt 1 &mdash; Altes Konto identifizieren</h3>', unsafe_allow_html=True)
    st.markdown('<span class="badge-ok">KI-gest\u00fctzte Erkennung aktiv</span>', unsafe_allow_html=True)

    c1, _ = st.columns([1, 2])
    with c1:
        if st.button("Demo-Modus laden", key="s1_demo_btn"):
            apply_demo()
            st.rerun()

    bank_alt = st.selectbox(
        "Name der alten Bank",
        [""] + BANK_SUGGESTIONS,
        index=(BANK_SUGGESTIONS.index(st.session_state.bank_alt)+1) if st.session_state.bank_alt in BANK_SUGGESTIONS else 0,
        key="s1_bank_select",
    )
    raw_iban = st.text_input("IBAN (alte Bank)",
                             placeholder="DE00 0000 0000 0000 0000 00", key="s1_iban_input",
                             on_change=format_iban_callback, max_chars=27)
                             
    components.html("""
    <script>
    const doc = window.parent.document;
    const inputs = doc.querySelectorAll('input[aria-label="IBAN (alte Bank)"]');
    if(inputs.length > 0) {
        const input = inputs[0];
        input.addEventListener('input', function(e) {
            let cursor = e.target.selectionStart;
            let val = e.target.value.replace(/\s+/g, '').toUpperCase();
            let formatted = val.match(/.{1,4}/g);
            formatted = formatted ? formatted.join(' ') : '';
            
            if (e.target.value !== formatted) {
                // Adjust cursor position
                let spacesBefore = (e.target.value.slice(0, cursor).match(/\s/g) || []).length;
                let newSpacesBefore = (formatted.slice(0, cursor).match(/\s/g) || []).length;
                cursor += (newSpacesBefore - spacesBefore);
                
                e.target.value = formatted;
                
                // Keep React in sync
                let tracker = e.target._valueTracker;
                if (tracker) {
                    tracker.setValue(formatted);
                }
                e.target.dispatchEvent(new Event('input', { bubbles: true }));
                
                // Restore cursor
                e.target.setSelectionRange(cursor, cursor);
            }
        });
    }
    </script>
    """, height=0)

    iban = format_iban(raw_iban)
    
    if raw_iban:
        if validate_iban(iban):
            st.markdown('<div class="iban-validation iban-success"><strong>&#10003; IBAN-Format g\u00fcltig</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="iban-validation iban-error">Diese IBAN scheint nicht korrekt zu sein.<br>Erwartetes Format: DE89 3704 0044 0532 0130 00<br>Bitte pr\u00fcfen Sie Ihre Eingabe.</div>', unsafe_allow_html=True)
    name = st.text_input("Kundenname",
                         placeholder="Julia Bergmann", key="s1_name_input")
    geb = st.date_input("Geburtsdatum",
                        min_value=date(1930,1,1), max_value=date(2010,12,31), key="s1_geb_input")

    st.markdown('<p class="section-heading" style="margin-top:1.5rem;">Datenschutz & Einwilligungen</p>', unsafe_allow_html=True)
    
    cb1 = st.checkbox(
        u"Ich erteile Global Finance Solutions SE die Einwilligung, meine Kontobewegungen der letzten 24 Monate gem\u00e4\u00df PSD2 einmalig abzurufen.",
        value=st.session_state.cons_daten, key="s1_cons_daten_cb")
    with st.expander("Details zum Datenabruf anzeigen"):
        st.markdown("""
        **Was abgerufen wird:**
        - Kontonummer und IBAN
        - Transaktionshistorie (24 Monate)
        - Dauerauftr\u00e4ge und Lastschriftmandate
        - Kontoinhaber-Stammdaten
        
        **Was NICHT abgerufen wird:**
        - Kreditw\u00fcrdigkeitsdaten
        - Daten anderer Konten
        - Passw\u00f6rter oder TANs
        """)

    cb2 = st.checkbox(
        u"Ich stimme der KI-gest\u00fctzten Analyse meiner Transaktionsdaten zur automatischen Erkennung von Zahlungspartnern zu (DSGVO Art. 6 Abs. 1a).",
        value=st.session_state.cons_verarb, key="s1_cons_verarb_cb")
    with st.expander("Details zur Verarbeitung anzeigen"):
        st.markdown("""
        - Daten werden ausschlie\u00dflich f\u00fcr den Kontowechsel verwendet
        - Keine Weitergabe an Dritte
        - L\u00f6schung nach 90 Tagen
        - Speicherung ausschlie\u00dflich auf EU-Servern (Azure Deutschland)
        """)

    cb3 = st.checkbox(
        u"Ich verstehe, dass alle KI-Vorschl\u00e4ge von mir best\u00e4tigt werden m\u00fcssen und keine automatischen Entscheidungen ohne meine Zustimmung erfolgen (DSGVO Art. 22 \u2014 Human-in-the-Loop).",
        value=st.session_state.cons_mensch, key="s1_cons_mensch_cb")

    st.markdown("""
        <span class="compliance-pill">DSGVO-konform</span>
        <span class="compliance-pill">EU AI Act compliant</span>
        <span class="compliance-pill">BaFin BAIT zertifiziert</span>
    """, unsafe_allow_html=True)

    st.session_state.update(iban_alt=iban, name=name, geburtsdatum=geb,
                            bank_alt=bank_alt, cons_daten=cb1, cons_verarb=cb2, cons_mensch=cb3)
    st.markdown('</div>', unsafe_allow_html=True)

    ready = all([name.strip(), validate_iban(iban), bank_alt, cb1, cb2, cb3])
    if st.button("Weiter", key="s1_next", disabled=not ready):
        st.session_state.step = 2
        st.rerun()
    if not ready:
        st.caption(u"Bitte alle Felder ausf\u00fcllen und Einwilligungen erteilen.")

# ── Step 2 ───────────────────────────────────────────────────────────────────
def page_step2():
    is_berater = st.session_state.view_mode == "berater"

    if not st.session_state.ki_done:
        ph = st.empty()
        html_base = '<div class="terminal-box">'
        diag = '<div class="connection-diagram"><div class="conn-box">[Kunde]</div><div class="conn-line" data-label="TLS 1.3"></div><div class="conn-box" style="background:#1a5c52">[GFS KI-Service]</div><div class="conn-line" data-label="PSD2"></div><div class="conn-box">[Alte Bank]</div></div>'
        
        st1_html = html_base + '<div class="term-line">Verbindung wird aufgebaut...</div>' + diag
        ph.markdown(st1_html + '</div>', unsafe_allow_html=True)
        time.sleep(0.8)
        
        st2_html = st1_html + '<div class="term-line"><br/>Authentifizierung l&auml;uft...</div>'
        ph.markdown(st2_html + '</div>', unsafe_allow_html=True)
        
        auth_steps = [
            ("OAuth 2.0 Token angefordert...", "Token erhalten [OK]", "/api/v1/auth"),
            ("Starke Kundenauthentifizierung (SCA)...", "[OK]", "/api/v1/sca"),
            ("PSD2 Consent validiert...", "[OK]", "/api/v1/consent")
        ]
        
        for step_name, step_ok, endpoint in auth_steps:
            time.sleep(0.3)
            met_html = f'<span class="term-muted">HTTP 200 OK | {random.randint(45, 120)}ms | {endpoint}</span>' if is_berater else ''
            st2_html += f'<div class="term-line">- {step_name} &rarr; <span class="term-ok">{step_ok}</span> {met_html}</div>'
            ph.markdown(st2_html + '</div>', unsafe_allow_html=True)
            
        time.sleep(0.2)
        
        st3_html = st2_html + '<div class="term-line"><br/>Kontodaten werden abgerufen...<br/>Zeitraum: 24 Monate | Verschl&uuml;sselung: AES-256</div>'
        total_tx = random.randint(420, 480)
        curr_tx = 0
        while curr_tx < total_tx:
            curr_tx += random.randint(30, 80)
            if curr_tx > total_tx: curr_tx = total_tx
            met_html = f'<span class="term-muted">GET /api/v1/transactions?months=24 | {random.randint(110, 320)}ms</span>' if is_berater else ''
            ph.markdown(st3_html + f'<div class="term-line">Transaktionen geladen: {curr_tx}... {met_html}</div></div>', unsafe_allow_html=True)
            time.sleep(0.12)
        
        st3_html += f'<div class="term-line">Transaktionen geladen: {total_tx}... <span class="term-ok">[OK]</span></div>'
        time.sleep(0.2)
        
        st4_html = st3_html + '<div class="term-line"><br/>KI-Analyse wird gestartet...</div>'
        ph.markdown(st4_html + '</div>', unsafe_allow_html=True)
        time.sleep(0.3)
        
        tech_stack = [
            "Modell: GFS-NLP-BERT v2.3.1",
            "Framework: Python / TensorFlow",
            "Infrastruktur: Azure Deutschland (Germany West Central)",
            "Datenhaltung: Ausschlie&szlig;lich EU-Raum"
        ]
        for t in tech_stack:
            st4_html += f'<div class="term-line" style="color:#7ee787">&gt; {t}</div>'
        
        st4_html += f'<div class="term-line"><br/><span class="term-ok">Analyse abgeschlossen &mdash; {total_tx} Transaktionen verarbeitet</span></div>'
        ph.markdown(st4_html + '</div>', unsafe_allow_html=True)
        time.sleep(0.8)
        
        st.session_state.ki_done = True
        st.rerun()

    st.markdown('<div class="card"><h3>Schritt 2 &mdash; KI-Analyse der Kontobewegungen</h3>', unsafe_allow_html=True)
    st.markdown("""<div class="info-box">Durchschnittlicher Kunde hat 23 Zahlungspartner &mdash;
        kennt aber nur 12-15 bewusst. Unsere KI erkennt alle.</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    partners = st.session_state.partners

    # Vergessen-Warnung
    if not is_berater and not st.session_state.warning_dismissed:
        missing_insurance = not any(c in p["name"].lower() or c in p["category"].lower() for p in partners for c in ["versicherung", "haftpflicht", "kfz", "aok", "allianz", "huk"])
        missing_streaming = not any(c in p["name"].lower() or c in p["sepa_ref"].lower() for p in partners for c in ["netflix", "spotify", "disney", "prime", "apple"])
        missing_utility = not any(c in p["name"].lower() or c in p["sepa_ref"].lower() for p in partners for c in ["strom", "gas", "stadtwerke", "e.on", "swm"])
        missing_miete = not any("miete" in p["name"].lower() or "miete" in p["sepa_ref"].lower() for p in partners)

        if st.session_state.active_persona == "gabi" and missing_miete:
            st.markdown('<div class="gabi-warning">Achtung: Keine Mietzahlung erkannt.<br/>Falls Sie zur Miete wohnen, ist dies Ihre kritischste Zahlung &mdash; bitte f&uuml;gen Sie diese manuell hinzu.</div>', unsafe_allow_html=True)
        elif len(partners) < 8 or missing_insurance or missing_streaming or missing_utility:
            warning_html = '<div class="completeness-warning"><strong>Vollst&auml;ndigkeitspr&uuml;fung &mdash; Bitte pr&uuml;fen</strong><br/><br/>'
            if len(partners) < 8:
                warning_html += f'Bei Ihrem Profil wurden {len(partners)} Zahlungspartner erkannt. Der durchschnittliche Kunde hat 23 Partner.<br/>Haben Sie m&ouml;glicherweise folgende vergessen?<br/>'
            else:
                warning_html += 'Haben Sie m&ouml;glicherweise folgende vergessen?<br/>'
            warning_html += '</div>'
            st.markdown(warning_html, unsafe_allow_html=True)
            
            st.write("Häufig vergessene Kategorien:")
            if missing_insurance or len(partners) < 8:
                if st.checkbox("Versicherungen (Haftpflicht, Hausrat, KFZ)", key="w_ins"):
                    components.html("<script>window.parent.location.hash='#manuelle-erfassung';</script>", height=0)
            if missing_streaming or len(partners) < 8:
                if st.checkbox("Streaming-Dienste (Netflix, Spotify, Disney+)", key="w_str"):
                    components.html("<script>window.parent.location.hash='#manuelle-erfassung';</script>", height=0)
            if missing_utility or len(partners) < 8:
                if st.checkbox("Strom / Gas / Stadtwerke", key="w_util"):
                    components.html("<script>window.parent.location.hash='#manuelle-erfassung';</script>", height=0)
            if len(partners) < 8:
                if st.checkbox("Fitness / Sport-Abonnements", key="w_fit"):
                    components.html("<script>window.parent.location.hash='#manuelle-erfassung';</script>", height=0)
                if st.checkbox("Zeitschriften / digitale Abonnements", key="w_zeit"):
                    components.html("<script>window.parent.location.hash='#manuelle-erfassung';</script>", height=0)
                if st.checkbox("Sparpläne oder Wertpapierdepot", key="w_spar"):
                    components.html("<script>window.parent.location.hash='#manuelle-erfassung';</script>", height=0)

            if st.button("Alles vollständig — weiter", key="w_dismiss"):
                st.session_state.warning_dismissed = True
                st.rerun()

    # Enrich and sort partners by risk
    for p in partners:
        p["_risk_lvl"], p["_risk_label"], p["_risk_color"] = get_risk_level(p)
    partners.sort(key=lambda x: x["_risk_lvl"])
    
    if is_berater:
        st.markdown('<div class="consultant-mode"></div><span class="consultant-badge">Berater-Modus &mdash; Intern</span>', unsafe_allow_html=True)
        
        # --- CONSULTANT DASHBOARD ---
        avg_conf = int(sum(p['confidence'] for p in partners) / max(len(partners), 1))
        auto_rate = int(sum(1 for p in partners if p['confidence'] > 85) / max(len(partners), 1) * 100)
        st.markdown(f'''
        <div class="dashboard-grid">
            <div class="metric-card">
                <div class="metric-value">{len(partners)}</div>
                <div class="metric-label">Erkannte Partner</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{avg_conf}%</div>
                <div class="metric-label">Ø KI-Konfidenz</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{auto_rate}%</div>
                <div class="metric-label">Automatisierbar</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<p class="section-heading">Datenansicht (Gefiltert via NLP/BERT Engine):</p>', unsafe_allow_html=True)
        
        df_data = []
        for p in partners:
            df_data.append({
                "Partner": p["name"],
                "Kategorie": p["category"].title(),
                "Betrag (\u20ac)": p["amount"],
                "Rhythmus": RHYTHM_LABELS.get(p["rhythm"], p["rhythm"]),
                "Risiko": p["_risk_label"].split(" \u2014")[0],
                "Konfidenz": f"{p['confidence']}%",
                "SEPA-Code": p["sepa_ref"],
                "Status": "Ausgew\u00e4hlt" if p["selected"] else "Ignoriert"
            })
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Als CSV exportieren", data=csv, file_name="gfs_partner_export.csv", mime="text/csv")
        
        sel_count = sum(1 for p in partners if p["selected"])

    else:
        # Cryptic Reveal Expander
        cryptic_codes = ["PPSPOTIFY", "NF-FLIX", "AMZN PMTS", "APPLE-M", "DISNEY", "LIEFER", "NORDVPN", "HF-BOX"]
        cryptic_partners = [p for p in partners if p["sepa_ref"] in cryptic_codes]
        
        if cryptic_partners:
            with st.expander("Das h\u00e4tten Sie wahrscheinlich vergessen", expanded=True):
                st.markdown('<p style="font-size:.85rem;color:#666;margin-bottom:1rem;">Oft \u00fcbersehen wegen kryptischer Abbuchungstexte:</p>', unsafe_allow_html=True)
                for cp in cryptic_partners[:4]:
                    st.markdown(f'''
                    <div class="cryptic-card">
                        <div class="code">SEPA-Code: {cp["sepa_ref"]}</div>
                        <div class="identified">Erkannt als: {cp["name"]}</div>
                        <div class="reason">Warum vergessen? Kryptischer Zahlungscode &mdash; nicht als bekannter Dienst erkennbar.</div>
                    </div>
                    ''', unsafe_allow_html=True)
                st.markdown(f'''
                <div class="stat-highlight">
                    <span class="stat-number">27%</span>
                    <span class="stat-text">Laut unserer Studie vergessen 27% aller Kunden mindestens einen wichtigen Zahlungspartner beim manuellen Wechsel. Unsere KI hat alle <strong>{len(partners)}</strong> Partner f\u00fcr Sie identifiziert.</span>
                </div>
                ''', unsafe_allow_html=True)

        # Count risks
        c_red = sum(1 for p in partners if p["_risk_lvl"] == 0)
        c_org = sum(1 for p in partners if p["_risk_lvl"] == 1)
        c_grn = sum(1 for p in partners if p["_risk_lvl"] == 2)
        
        st.markdown('<p class="section-heading">Automatisch erkannte Zahlungspartner:</p>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:.8rem;color:#666;margin-bottom:1rem;">Erkannt: {c_red} kritische, {c_org} wichtige, {c_grn} unkritische Zahlungspartner</div>', unsafe_allow_html=True)

        for i, p in enumerate(partners):
            rhythm_label = RHYTHM_LABELS.get(p["rhythm"], p["rhythm"])
            sign = "+" if p["category"] == "gehalt" else ""
            dot_html = conf_dot(p["confidence"])
            
            risk_class = f"risk-{p['_risk_color']}"
            badge_class = f"risk-badge-{p['_risk_color']}"
            
            tooltip = '<div style="font-size:.7rem;color:#c0392b;margin-top:.2rem;">Wird bevorzugt und zuerst \u00fcbertragen.</div>' if p["_risk_lvl"] == 0 else ''

            col_cb, col_info = st.columns([0.05, 0.95])
            with col_cb:
                sel = st.checkbox("Auswahl", value=p["selected"], key="p_cb_" + str(i),
                                  label_visibility="collapsed")
                partners[i]["selected"] = sel
            with col_info:
                st.markdown(
                    f'<div class="ki-card {risk_class}">'
                    '<div style="flex-grow:1;">'
                    f'<strong>{p["name"]}</strong><br>'
                    f'<span class="sub">{sign}{format(p["amount"], ".2f")} EUR / {rhythm_label} &middot; SEPA: {p["sepa_ref"]}</span>'
                    f'{tooltip}'
                    '</div>'
                    f'<span class="{badge_class}" style="margin-right:.8rem;">{p["_risk_label"]}</span>'
                    f'{dot_html}'
                    '</div>', unsafe_allow_html=True)
                
                # --- HUMAN IN THE LOOP (Interactive Feedback) ---
                with st.expander("⚙️ KI-Entscheidung korrigieren", expanded=False):
                    hc1, hc2, hc3 = st.columns([2, 2, 1])
                    cat_options = ["lastschrift", "dauerauftrag", "gehalt", "sonstige"]
                    current_cat = p.get("category", "sonstige")
                    cat_index = cat_options.index(current_cat) if current_cat in cat_options else 3
                    new_cat = hc1.selectbox("Kategorie anpassen", cat_options, index=cat_index, key=f"cat_{i}")
                    
                    rhy_options = ["zweiwöchentlich", "monatlich", "vierteljährlich", "halbjährlich", "jährlich"]
                    current_rhy = p.get("rhythm", "monatlich")
                    rhy_index = rhy_options.index(current_rhy) if current_rhy in rhy_options else 1
                    new_rhythm = hc2.selectbox("Turnus anpassen", rhy_options, index=rhy_index, key=f"rhy_{i}")
                    
                    if new_cat != p["category"] or new_rhythm != p["rhythm"]:
                        partners[i]["category"] = new_cat
                        partners[i]["rhythm"] = new_rhythm
                        partners[i]["confidence"] = 100
                        partners[i]["_risk_label"] = "Manuell verifiziert"
                        partners[i]["_risk_color"] = "green"
                        partners[i]["_risk_lvl"] = 2
                        hc3.markdown('<div class="hitl-feedback">✓ KI lernt</div>', unsafe_allow_html=True)

        sel_count = sum(1 for p in partners if p["selected"])
        sel_total = sum(p["amount"] for p in partners if p["selected"] and p["category"] != "gehalt")
        st.markdown('<div class="info-box"><strong>' + str(sel_count) + ' von ' + str(len(partners)) + '</strong> Zahlungspartnern ausgew\u00e4hlt '
                    '(Ausgaben: <strong>' + format(sel_total, ",.2f") + ' EUR/Monat</strong>)</div>', unsafe_allow_html=True)

        # Manual partners display
        for idx, mp in enumerate(st.session_state.manual_partners):
            st.markdown('<div class="ki-card">'
                        '<span><strong>' + mp["name"] + '</strong><br>'
                        '<span class="sub">' + format(mp["amount"], ".2f") + ' EUR / ' + mp["rhythm"] + '</span></span>'
                        '<span class="badge-manual">Manuell</span>'
                        '</div>', unsafe_allow_html=True)

        # SEPA-Code Decoder Widget
        with st.expander("SEPA-Code manuell entschlüsseln", expanded=False):
            st.markdown('<div style="font-size:0.85rem; margin-bottom:1rem; color:#666;">Fügen Sie hier einen kryptischen Kontoauszugs-Text ein, um ihn von der GFS-KI entschlüsseln zu lassen.</div>', unsafe_allow_html=True)
            
            sepa_input = st.text_input("SEPA-Code / Verwendungszweck", key="sepa_decoder_in", placeholder="z.B. EREF+000000123456789 SVWZ+AMAZON PAYMENTS")
            
            sepa_patterns = {
                "AMAZON": ("Amazon Prime / Amazon Payments", 8.99, "Unkritisch"),
                "AMZN": ("Amazon Prime / Amazon Payments", 8.99, "Unkritisch"),
                "NF-FLIX": ("Netflix Streaming", 17.99, "Unkritisch"),
                "NETFLIX": ("Netflix Streaming", 17.99, "Unkritisch"),
                "PPSPOTIFY": ("Spotify (via PayPal)", 11.99, "Unkritisch"),
                "SPOTIFY": ("Spotify", 11.99, "Unkritisch"),
                "TELEKOM": ("Deutsche Telekom", 89.00, "Wichtig"),
                "DTAG": ("Deutsche Telekom", 89.00, "Wichtig"),
                "VATTENFALL": ("Vattenfall Energie", 127.00, "Kritisch"),
                "STADTWERKE": ("Stadtwerke (Energie/Wasser)", 127.00, "Kritisch"),
                "AOK": ("AOK Krankenversicherung", 215.00, "Kritisch"),
                "PAYPAL": ("PayPal Zahlung", 50.00, "Wichtig"),
                "GOOGLE": ("Google (Play/YouTube)", 9.99, "Unkritisch"),
                "APPLE": ("Apple (iCloud/App Store)", 9.99, "Unkritisch"),
                "RUNDFUNK": ("ARD ZDF Rundfunkbeitrag", 18.36, "Wichtig"),
                "GEZ": ("ARD ZDF Rundfunkbeitrag", 18.36, "Wichtig"),
            }
            
            if sepa_input:
                inp_upper = sepa_input.upper()
                found_match = None
                for k, v in sepa_patterns.items():
                    if k in inp_upper:
                        found_match = v
                        break
                        
                if found_match:
                    name, amount, risk = found_match
                    st.markdown(f'''
                    <div class="decoder-result">
                        <div><strong>SEPA-Code erkannt</strong></div>
                        <div>Identifiziert als: {name}</div>
                        <div>Typischer Betrag: {format(amount, ".2f")} EUR/Monat</div>
                        <div>Risiko-Level: {risk}</div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    if st.button("Zu meiner Liste hinzufügen", key="sepa_add_btn"):
                        st.session_state.manual_partners.append(
                            dict(name=name, amount=amount, rhythm="monatlich",
                                 category="lastschrift", confidence=95, sepa_ref=sepa_input[:15], selected=True))
                        del st.session_state["sepa_decoder_in"]
                        st.rerun()
                else:
                    st.markdown('<div class="decoder-error">Code nicht erkannt — bitte nutzen Sie die manuelle Eingabe unten.</div>', unsafe_allow_html=True)
                    if st.button("Zur manuellen Eingabe", key="sepa_scroll_btn"):
                        components.html("<script>window.parent.location.hash='#manuelle-erfassung';</script>", height=0)

        # Manual add via tabs
        st.markdown('<p id="manuelle-erfassung" class="section-heading">Zahlungspartner manuell hinzuf\u00fcgen:</p>', unsafe_allow_html=True)
        tab_da, tab_ls = st.tabs(["Dauerauftrag", "Lastschriftmandat"])

        with tab_da:
            with st.form("form_add_da", clear_on_submit=True):
                da_c1, da_c2 = st.columns(2)
                da_name = da_c1.text_input("Empf\u00e4nger", key="da_empfaenger_input",
                                           placeholder="z.B. Hausverwaltung")
                da_amount = da_c2.number_input("Betrag (EUR)", min_value=0.01,
                                               value=50.0, step=0.01, key="da_betrag_input")
                da_rhythm = st.selectbox("Rhythmus", ["monatlich","viertelj\u00e4hrlich","halbj\u00e4hrlich","j\u00e4hrlich"],
                                        key="da_rhythmus_select")
                if st.form_submit_button("Hinzuf\u00fcgen", type="primary") and da_name.strip():
                    st.session_state.manual_partners.append(
                        dict(name=da_name, amount=da_amount, rhythm=da_rhythm,
                             category="dauerauftrag", confidence=0, sepa_ref="MANUELL", selected=True))
                    st.rerun()

        with tab_ls:
            with st.form("form_add_ls", clear_on_submit=True):
                ls_c1, ls_c2 = st.columns(2)
                ls_name = ls_c1.text_input("Gl\u00e4ubiger", key="ls_glaeubiger_input",
                                           placeholder="z.B. Versicherung")
                ls_amount = ls_c2.number_input("Gesch\u00e4tzter Betrag (EUR)", min_value=0.01,
                                               value=30.0, step=0.01, key="ls_betrag_input")
                ls_rhythm = st.selectbox("Rhythmus", ["monatlich","viertelj\u00e4hrlich","halbj\u00e4hrlich","j\u00e4hrlich"],
                                        key="ls_rhythmus_select")
                if st.form_submit_button("Hinzuf\u00fcgen", type="primary") and ls_name.strip():
                    st.session_state.manual_partners.append(
                        dict(name=ls_name, amount=ls_amount, rhythm=ls_rhythm,
                             category="lastschrift", confidence=0, sepa_ref="MANUELL", selected=True))
                    st.rerun()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Zur\u00fcck", key="s2_back"):
            st.session_state.step = 1; st.rerun()
    with c2:
        if st.button("Weiter", key="s2_next", disabled=sel_count == 0):
            st.session_state.step = 3; st.rerun()

# ── Step 3 ───────────────────────────────────────────────────────────────────
def page_step3():
    st.markdown('<div class="card" style="border:2px solid #1a5c52;">'
        '<div style="display:flex;align-items:center;gap:1rem;">'
            '<div style="background:linear-gradient(135deg,#1a5c52,#1e7a6e);color:#e8a020;width:56px;height:56px;'
                'border-radius:14px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:1rem;">GFS</div>'
            '<div>'
                '<h3 style="margin:0;color:#1a1a2e;">Ihr neues Konto bei Global Finance Solutions SE</h3>'
                '<p style="margin:.2rem 0 0;font-size:.88rem;color:#666;">'
                    'IBAN: <strong style="color:#1a1a2e;">' + st.session_state.iban_neu + '</strong><br>'
                    'Kontomodell: <strong style="color:#1a1a2e;">GFS Premium-Konto</strong> &middot; '
                    'Kontof\u00fchrung: <strong style="color:#1a1a2e;">Kostenlos im ersten Jahr</strong>'
                '</p>'
            '</div>'
        '</div>'
    '</div>', unsafe_allow_html=True)

    min_date = biz_days_ahead(date.today(), 12)
    default_d = st.session_state.wechseldatum if st.session_state.wechseldatum and st.session_state.wechseldatum >= min_date else min_date
    st.markdown('<div class="info-box"><strong>Gesetzliche Frist:</strong> Gem\u00e4\u00df &sect;21 ZKG '
        'betr\u00e4gt die Mindestfrist <strong>12 Werktage</strong>. Fr\u00fchestes Wechseldatum: <strong>'
        + min_date.strftime("%d.%m.%Y") + '</strong></div>', unsafe_allow_html=True)

    wdatum = st.date_input("Gew\u00fcnschtes Wechseldatum", value=default_d, min_value=min_date, key="s3_date_input")
    st.session_state.wechseldatum = wdatum

    sel_p = [p for p in st.session_state.partners if p["selected"]] + [p for p in st.session_state.manual_partners if p.get("selected", True)]
    da_count = sum(1 for p in sel_p if p["category"] == "dauerauftrag")
    ls_count = sum(1 for p in sel_p if p["category"] == "lastschrift")
    has_gehalt = any(p["category"] == "gehalt" for p in sel_p)
    gehalt_text = " &middot; Arbeitgeber wird benachrichtigt" if has_gehalt else ""

    st.markdown('<div class="card"><h3>Was wird \u00fcbertragen?</h3>'
        '<p style="color:#1a1a2e;">' + str(da_count) + ' Dauerauftr\u00e4ge &middot; ' + str(ls_count) + ' Lastschriftmandate'
        + gehalt_text + '</p></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Zur\u00fcck", key="s3_back"):
            st.session_state.step = 2; st.rerun()
    with c2:
        if st.button("Weiter", key="s3_next"):
            st.session_state.step = 4; st.rerun()

# ── Step 4 ───────────────────────────────────────────────────────────────────
def _build_tasks():
    tasks = [
        "Sichere Verbindung zur alten Bank aufgebaut",
        "Kontodaten abgerufen (PSD2-konform)",
        "KI kategorisiert Zahlungspartner",
    ]
    sel = [p for p in st.session_state.partners if p["selected"]] + st.session_state.manual_partners
    for p in sel:
        tasks.append("Benachrichtige " + p["name"])
    tasks += [
        u"Dauerauftr\u00e4ge bei GFS eingerichtet",
        "Push-Benachrichtigung gesendet",
        u"Altkonto-Schlie\u00dfung vorbereitet",
    ]
    return tasks

def page_step4():
    if st.session_state.sim_done:
        _show_sim_done()
        if st.button("Weiter", key="s4_next"):
            st.session_state.end_time = datetime.now()
            st.session_state.step = 5; st.rerun()
        return

    st.markdown('<div class="card"><h3>Schritt 4 &mdash; Automatisierte \u00dcbertragung</h3></div>', unsafe_allow_html=True)
    if st.button("\u00dcbertragung starten", key="s4_start"):
        _run_simulation()
        st.session_state.sim_done = True
        st.rerun()

def _run_simulation():
    is_berater = st.session_state.view_mode == "berater"
    tasks = _build_tasks()
    col_left, col_right = st.columns([1.2, 1])
    progress = st.progress(0, text="Starte \u00dcbertragung...")
    
    with col_right:
        log_area = st.empty()
    with col_left:
        task_area = st.empty()
        
    log_entries = []
    base_time = datetime.now()

    if is_berater:
        task_area.markdown('<div class="consultant-mode"></div><span class="consultant-badge">Berater-Modus &mdash; Intern</span>', unsafe_allow_html=True)
        st.session_state.audit_logs = []
        log_html_template = '<div class="audit-log-container">{content}</div>'
    
    for idx, desc in enumerate(tasks):
        frac = (idx + 1) / len(tasks)
        st.session_state.sim_progress_pct = int(frac * 30)
        render_steps(4) # force update of the top progress bar
        
        if is_berater:
            ts = (base_time + timedelta(seconds=idx)).strftime("%H:%M:%S.%f")[:-3]
            log_entries.append(f'<span class="ts">[{ts}]</span> <span class="info">[EXEC] {desc}</span>')
            
            if idx == 0:
                log_entries.append(f'<span class="ts">[{ts}]</span> <span class="info">[SYS] Model version: GFS-NLP-BERT v2.3.1 loaded</span>')
            elif idx == 2:
                sel = [p for p in st.session_state.partners if p["selected"]]
                for sp in sel[:3]:
                    processing_ms = random.randint(15, 85)
                    log_entries.append(f'<span class="ts">[{ts}]</span> <span class="info">[BERT] Input: "{sp["sepa_ref"]}" &rarr; Output: {sp["category"]} ({sp["confidence"]}%) in {processing_ms}ms</span>')
                    if sp.get("_risk_lvl") == 0:
                         log_entries.append(f'<span class="ts">[{ts}]</span> <span class="err">[FLAG] Human oversight required (Risk Level 0)</span>')
            
            task_area.markdown(log_html_template.format(content="<br>".join(log_entries)), unsafe_allow_html=True)
        else:
            rows = ""
            for j, d in enumerate(tasks):
                if j < idx:
                    rows += '<div class="task-row task-done"><span class="badge-ok">OK</span> ' + d + '</div>'
                elif j == idx:
                    rows += '<div class="task-row task-running"><span class="badge-wait">L\u00e4uft...</span> ' + d + '</div>'
                else:
                    rows += '<div class="task-row task-pending"><span style="color:#ccc;">Ausstehend</span> ' + d + '</div>'
            task_area.markdown('<div class="card">' + rows + '</div>', unsafe_allow_html=True)

        if not is_berater:
            ts = (base_time + timedelta(seconds=idx)).strftime("%H:%M:%S")
            log_entries.append('<span class="ts">[' + ts + ']</span> <span class="msg">[OK] ' + desc + '</span>')
            if idx == 0:
                log_entries.append('<span class="ts">[' + ts + ']</span> <span class="msg">[INFO] API-Verbindung hergestellt (TLS 1.3)</span>')
            elif idx == 1:
                log_entries.append('<span class="ts">[' + ts + ']</span> <span class="msg">[INFO] PSD2-Token validiert</span>')
            elif idx == 2:
                sel = [p for p in st.session_state.partners if p["selected"]]
                for sp in sel[:3]:
                    log_entries.append('<span class="ts">[' + ts + ']</span> <span class="msg">[INFO] NLP erkannt: ' + sp["name"] + ' (' + str(sp["confidence"]) + '% Konfidenz)</span>')
            log_area.markdown('<div class="terminal">' + "<br>".join(log_entries) + '</div>', unsafe_allow_html=True)
            
        progress.progress(frac, text="Verarbeite... (" + str(idx+1) + "/" + str(len(tasks)) + ")")
        time.sleep(random.uniform(0.5, 0.9))

    if is_berater:
        st.session_state.audit_logs = log_entries
        checklist = """
        <div class="card" style="font-size:.85rem;">
        <h4>Compliance Checklist</h4>
        <div class="checklist-item done">\u2714\ufe0f DSGVO Art. 22 &mdash; Human oversight confirmed</div>
        <div class="checklist-item done">\u2714\ufe0f ZKG &sect;21 &mdash; 12 Werktage Frist eingehalten</div>
        <div class="checklist-item done">\u2714\ufe0f PSD2 &mdash; Consent documented</div>
        <div class="checklist-item done">\u2714\ufe0f EU AI Act &mdash; Explainability logged</div>
        <div class="checklist-item done">\u2714\ufe0f BaFin BAIT &mdash; Audit trail complete</div>
        </div>
        """
        log_area.markdown(checklist, unsafe_allow_html=True)
    else:
        rows = "".join('<div class="task-row task-done"><span class="badge-ok">OK</span> ' + d + '</div>' for d in tasks)
        task_area.markdown('<div class="card">' + rows + '</div>', unsafe_allow_html=True)
    
    progress.progress(1.0, text="Alle Aufgaben abgeschlossen")

def _show_sim_done():
    is_berater = st.session_state.view_mode == "berater"
    tasks = _build_tasks()
    st.markdown('<div class="success-box">Alle \u00dcbertragungen erfolgreich abgeschlossen.</div>', unsafe_allow_html=True)
    
    if is_berater:
        col_left, col_right = st.columns([1.2, 1])
        with col_left:
            st.markdown('<div class="consultant-mode"></div><span class="consultant-badge">Berater-Modus &mdash; Intern</span>', unsafe_allow_html=True)
            log_html_template = '<div class="audit-log-container">{content}</div>'
            st.markdown(log_html_template.format(content="<br>".join(st.session_state.get("audit_logs", []))), unsafe_allow_html=True)
        with col_right:
            checklist = """
            <div class="card" style="font-size:.85rem;">
            <h4>Compliance Checklist</h4>
            <div class="checklist-item done">\u2714\ufe0f DSGVO Art. 22 &mdash; Human oversight confirmed</div>
            <div class="checklist-item done">\u2714\ufe0f ZKG &sect;21 &mdash; 12 Werktage Frist eingehalten</div>
            <div class="checklist-item done">\u2714\ufe0f PSD2 &mdash; Consent documented</div>
            <div class="checklist-item done">\u2714\ufe0f EU AI Act &mdash; Explainability logged</div>
            <div class="checklist-item done">\u2714\ufe0f BaFin BAIT &mdash; Audit trail complete</div>
            </div>
            """
            st.markdown(checklist, unsafe_allow_html=True)
    else:
        rows = "".join('<div class="task-row task-done"><span class="badge-ok">OK</span> ' + d + '</div>' for d in tasks)
        st.markdown('<div class="card">' + rows + '</div>', unsafe_allow_html=True)
        st.markdown("""<div class="card">
            <h3>Was passiert im Hintergrund?</h3>
            <p style="color:#1a1a2e;font-size:.88rem;line-height:1.7;">
            <strong>1. PSD2 Open Banking</strong> &mdash; Sichere API-Verbindung zur alten Bank via XS2A-Schnittstelle<br>
            <strong>2. NLP/BERT Analyse</strong> &mdash; KI kategorisiert Transaktionen automatisch<br>
            <strong>3. SEPA-Nachrichten</strong> &mdash; Automatisierte Benachrichtigung aller Zahlungspartner<br>
            <strong>4. SAP Banking Integration</strong> &mdash; Nahtlose Einrichtung bei GFS Banking Services
            </p>
        </div>""", unsafe_allow_html=True)

# ── Step 5 ───────────────────────────────────────────────────────────────────
def page_step5():
    # Freeze the timer
    if st.session_state.end_time is None:
        st.session_state.end_time = datetime.now()

    st.markdown(CONFETTI_HTML, unsafe_allow_html=True)
    st.markdown('<div class="card" style="text-align:center;padding:2.2rem;border:2px solid #1a5c52;">'
        '<h2 style="color:#1a5c52;margin:0;">Willkommen, ' + st.session_state.name + '!</h2>'
        '<p style="color:#666;font-size:.95rem;">Ihr Kontowechsel zu Global Finance Solutions SE ist abgeschlossen.</p>'
    '</div>', unsafe_allow_html=True)

    sel_p = [p for p in st.session_state.partners if p["selected"]] + st.session_state.manual_partners
    da_c = sum(1 for p in sel_p if p["category"] == "dauerauftrag")
    notif_c = len(sel_p)

    # Calculate actual elapsed time for the metric tile
    if st.session_state.start_time and st.session_state.end_time:
        elapsed = st.session_state.end_time - st.session_state.start_time
        total_secs = int(elapsed.total_seconds())
        e_mins = total_secs // 60
        e_secs = total_secs % 60
        elapsed_str = str(e_mins) + "m " + str(e_secs) + "s"
    else:
        elapsed_str = "1T 4Std"

    if "cust_nr" not in st.session_state:
        st.session_state.cust_nr = random.randint(47000, 47999)

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in [
        (c1, str(da_c), u"Dauerauftr\u00e4ge"),
        (c2, str(notif_c), "Partner benachrichtigt"),
        (c3, elapsed_str, "Wechseldauer"),
        (c4, "#" + str(st.session_state.cust_nr), "Kundennummer"),
    ]:
        col.markdown('<div class="metric-tile"><div class="val">' + val + '</div><div class="lbl">' + lbl + '</div></div>', unsafe_allow_html=True)

    if st.session_state.view_mode == "berater":
        st.markdown('<div class="consultant-mode" style="margin-top:2rem;"></div>', unsafe_allow_html=True)
        st.markdown('### Business Metrics (Intern)', unsafe_allow_html=True)
        bc1, bc2, bc3 = st.columns(3)
        with bc1:
            st.markdown("""<div class="biz-metric highlight">
                <div class="lbl">Kosten pro Fall (Automatisierung)</div>
                <div class="val">25 &euro;</div>
                <div class="lbl">Klassisch (Manuell): 127 &euro;</div>
                <div class="lbl" style="color:#27ae60;font-weight:bold;margin-top:.2rem;">Einsparung: 102 &euro;</div>
            </div>""", unsafe_allow_html=True)
        with bc2:
            auto_pct = 100 if notif_c == 0 else int((len([p for p in sel_p if p.get("confidence", 0) > 0]) / notif_c) * 100)
            st.markdown(f"""<div class="biz-metric">
                <div class="lbl">Automatisierungsgrad</div>
                <div class="val">{auto_pct}%</div>
                <div class="lbl">Identifiziert durch KI vs. Manuell</div>
            </div>""", unsafe_allow_html=True)
        with bc3:
            complexity = "Komplex (30+ Partner)" if len(st.session_state.partners) > 20 else "Standard (10-15 Partner)"
            st.markdown(f"""<div class="biz-metric">
                <div class="lbl">Fallkategorie</div>
                <div class="val" style="font-size:1.1rem;margin-top:.4rem;">{complexity}</div>
                <div class="lbl">Basierend auf Profilanalyse</div>
            </div>""", unsafe_allow_html=True)
        st.markdown('<div class="info-box" style="margin-top:1rem;"><strong>Business Case:</strong> Bei 50.000 Wechseln/Jahr ergibt sich eine j\u00e4hrliche Einsparung von <strong>5.100.000 &euro;</strong>.</div>', unsafe_allow_html=True)
        
        try:
            audit_bytes = generate_audit_pdf(st.session_state)
            st.download_button("Audit-Trail herunterladen (PDF)", data=audit_bytes,
                               file_name="GFS_Audit_Trail.pdf", mime="application/pdf", key="s5_audit_dl")
        except Exception as e:
            st.error("Audit-PDF Generierung fehlgeschlagen: " + str(e))

    st.markdown("---")

    pdf_state = {
        "name": st.session_state.name,
        "geburtsdatum_str": st.session_state.geburtsdatum.strftime("%d.%m.%Y"),
        "bank_alt": st.session_state.bank_alt,
        "iban_alt": st.session_state.iban_alt,
        "iban_neu": st.session_state.iban_neu,
        "wechseldatum_str": st.session_state.wechseldatum.strftime("%d.%m.%Y") if st.session_state.wechseldatum else "-",
        "partners": sel_p,
    }
    try:
        pdf_bytes = generate_confirmation_pdf(pdf_state)
        st.download_button("Best\u00e4tigung herunterladen (PDF)", data=pdf_bytes,
                           file_name="GFS_Kontowechsel_Bestaetigung.pdf", mime="application/pdf", key="s5_pdf_dl")
    except Exception as e:
        st.error("PDF-Generierung fehlgeschlagen: " + str(e))
        
    # --- CSV EXPORT ---
    import pandas as pd
    df_export = pd.DataFrame([{
        "Partner": p["name"], "Betrag": p["amount"], "Turnus": p["rhythm"], "Kategorie": p["category"], "Status": "Ausgewählt"
    } for p in sel_p])
    csv_bytes = df_export.to_csv(index=False).encode('utf-8')
    st.download_button("Zahlungspartner als Excel/CSV herunterladen", data=csv_bytes,
                       file_name="GFS_Zahlungspartner.csv", mime="text/csv", key="s5_csv_dl")

    st.button("Zum GFS Online-Banking", disabled=True, help="In der Produktivversion verf\u00fcgbar", key="s5_banking_btn")

    # --- EMAIL SIMULATION ---
    st.markdown(f'''
    <div class="email-simulation">
        <div class="email-header">
            <div class="email-header-row">
                <div class="email-header-label">Von:</div>
                <div class="email-header-value">GFS Kundenservice &lt;service@gfs-se.com&gt;</div>
            </div>
            <div class="email-header-row">
                <div class="email-header-label">An:</div>
                <div class="email-header-value">{st.session_state.name} &lt;kunde@email.de&gt;</div>
            </div>
            <div class="email-header-row" style="margin-top:10px;">
                <div class="email-header-label">Betreff:</div>
                <div class="email-header-value" style="font-weight:bold;">Ihr Kontowechsel ist erfolgreich abgeschlossen!</div>
            </div>
        </div>
        <div class="email-body">
            Guten Tag {st.session_state.name},<br><br>
            vielen Dank, dass Sie den GFS Kontowechselservice genutzt haben. Wir haben soeben alle {notif_c} ausgewählten Zahlungspartner erfolgreich über Ihre neue IBAN ({st.session_state.iban_neu}) informiert.<br><br>
            Die formelle Bestätigung sowie das Compliance-Protokoll der KI-Prüfung finden Sie im Anhang dieser E-Mail.<br><br>
            Willkommen bei Global Finance Solutions SE!<br><br>
            Mit freundlichen Grüßen,<br>
            <strong>Ihr GFS Team</strong><br>
            <br>
            <div class="email-attachment">📎 GFS_Kontowechsel_Bestaetigung.pdf</div>
            <div class="email-attachment">📎 GFS_Audit_Trail.pdf</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="card"><h3>Wie zufrieden sind Sie mit dem Wechselprozess?</h3>'
                '<p style="color:#666;font-size:.82rem;">Ihr NPS hilft uns, unser Ziel von NPS +50 zu erreichen.</p>',
                unsafe_allow_html=True)

    nps_val = st.select_slider(
        "Bewertung (1 = sehr unzufrieden, 10 = begeistert)",
        options=list(range(1, 11)),
        value=st.session_state.nps_score if st.session_state.nps_score else 8,
        key="nps_slider",
    )
    if st.button("Bewertung abgeben", key="nps_submit_btn"):
        st.session_state.nps_score = nps_val
        st.rerun()
    if st.session_state.nps_score:
        label = "Promoter" if st.session_state.nps_score >= 9 else ("Passiv" if st.session_state.nps_score >= 7 else "Detractor")
        st.markdown('<div class="success-box">Vielen Dank! Ihre Bewertung: <strong>' + str(st.session_state.nps_score) + '/10</strong> (' + label + ')</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Neue Simulation starten", key="s5_restart"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Chat Widget Mockup ───────────────────────────────────────────────────────
def render_chat_widget():
    if st.session_state.step not in [2, 3, 4] or st.session_state.view_mode == "berater":
        return

    st.markdown(f'<div class="chat-marker {"chat-closed" if not st.session_state.chat_open else ""}"></div>', unsafe_allow_html=True)
    
    if not st.session_state.chat_open:
        if st.button("💬 GFS Assistent", key="chat_open_btn"):
            st.session_state.chat_open = True
            st.session_state.chat_stage = "init"
            st.rerun()
    else:
        st.markdown('<div class="chat-header"><div class="chat-title"><div class="chat-dot"></div>GFS Assistent</div></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chat-msg chat-bot">Guten Tag! Ich bin Ihr digitaler GFS-Assistent.<br/>Kann ich Ihnen beim Kontowechsel helfen?</div><div class="chat-clear"></div>', unsafe_allow_html=True)
        
        if st.session_state.chat_stage == "init":
            if st.button("Ja, ich habe eine Frage", key="c_btn_ja"):
                st.session_state.chat_stage = "topics"
                st.rerun()
            if st.button("Nein, danke", key="c_btn_nein"):
                st.session_state.chat_open = False
                st.rerun()
                
        if st.session_state.chat_stage in ["topics", "topic_partner", "topic_dsgvo", "topic_zeit", "topic_tech"]:
            st.markdown('<div class="chat-msg chat-user">Ja, ich habe eine Frage</div><div class="chat-clear"></div>', unsafe_allow_html=True)
            st.markdown('<div class="chat-msg chat-bot">Welches Thema kann ich klären?</div><div class="chat-clear"></div>', unsafe_allow_html=True)
            
            if st.session_state.chat_stage == "topics":
                if st.button("Meine Zahlungspartner", key="c_btn_t1"): st.session_state.chat_stage = "topic_partner"; st.rerun()
                if st.button("Datenschutz", key="c_btn_t2"): st.session_state.chat_stage = "topic_dsgvo"; st.rerun()
                if st.button("Zeitplan", key="c_btn_t3"): st.session_state.chat_stage = "topic_zeit"; st.rerun()
                if st.button("Technische Frage", key="c_btn_t4"): st.session_state.chat_stage = "topic_tech"; st.rerun()
                
        if st.session_state.chat_stage == "topic_partner":
            st.markdown('<div class="chat-msg chat-user">Meine Zahlungspartner</div><div class="chat-clear"></div>', unsafe_allow_html=True)
            st.markdown('<div class="chat-msg chat-bot">Haben Sie einen Partner nicht gefunden?</div><div class="chat-clear"></div>', unsafe_allow_html=True)
            if st.button("Partner hinzufügen", key="c_btn_p1"):
                components.html("<script>window.parent.location.hash='#manuelle-erfassung';</script>", height=0)
            if st.button("Partner erklären (SEPA)", key="c_btn_p2"):
                st.toast("SEPA-Codes sind kryptische Kürzel der Banken (z.B. AMZN PMTS für Amazon).")
                
        if st.session_state.chat_stage == "topic_dsgvo":
            st.markdown('<div class="chat-msg chat-user">Datenschutz</div><div class="chat-clear"></div>', unsafe_allow_html=True)
            st.markdown('<div class="chat-msg chat-bot">Ihre Daten sind sicher (Azure DE). Wir verarbeiten nur für 90 Tage, prüfen via Human-in-the-Loop und geben nichts an Dritte weiter.</div><div class="chat-clear"></div>', unsafe_allow_html=True)

        if st.session_state.chat_stage == "topic_zeit":
            st.markdown('<div class="chat-msg chat-user">Zeitplan</div><div class="chat-clear"></div>', unsafe_allow_html=True)
            wd = st.session_state.get('wechseldatum_str', 'bald')
            st.markdown(f'<div class="chat-msg chat-bot">Ihr Wechseldatum ist {wd}. Die gesetzliche Frist von 12 Werktagen gemäß ZKG §21 wird eingehalten.</div><div class="chat-clear"></div>', unsafe_allow_html=True)

        if st.session_state.chat_stage == "topic_tech":
            st.markdown('<div class="chat-msg chat-user">Technische Frage</div><div class="chat-clear"></div>', unsafe_allow_html=True)
            st.markdown('<div class="chat-msg chat-bot">Für technische Fragen steht Ihnen unser Team zur Verfügung: 0800 123 456 78 (kostenlos, Mo-Fr 8-20 Uhr)</div><div class="chat-clear"></div>', unsafe_allow_html=True)

        if st.session_state.chat_stage != "init":
            st.markdown("<hr style='margin: 10px 0; border-color: #374151;'/>", unsafe_allow_html=True)
            if st.button("Menschlichen Berater anfordern", key="c_btn_human"):
                st.toast("Ein GFS-Berater wird sich innerhalb von 2 Stunden bei Ihnen melden. (Demonstrationsmodus)")
            if st.button("Gespräch beenden", key="c_btn_end"):
                st.session_state.chat_open = False
                st.session_state.chat_stage = "init"
                st.rerun()

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    init_state()
    render_header()
    render_timer()
    st.session_state.steps_placeholder = st.empty()
    render_steps(st.session_state.step)
    render_sidebar()
    {0: page_step0, 1: page_step1, 2: page_step2, 3: page_step3, 4: page_step4, 5: page_step5}[st.session_state.step]()
    render_chat_widget()
    render_footer()

if __name__ == "__main__":
    main()
# Force Streamlit reload 1
