"""
GFS Kontowechselservice — KI-Prototyp
Global Finance Solutions SE | Powered by metafinanz
"""
import streamlit as st
import time, re, random, copy
from datetime import date, timedelta, datetime
from styles import CSS, CONFETTI_HTML
from mock_data import (DEMO_CUSTOMER, BANK_SUGGESTIONS, AI_DETECTED_PARTNERS,
                       RHYTHM_LABELS, PERSONAS)
from pdf_generator import generate_confirmation_pdf

st.set_page_config(page_title="GFS Kontowechselservice", page_icon="", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
BASELINE_DAYS = 16

def validate_iban(iban):
    return bool(re.fullmatch(r"DE\d{20}", iban.replace(" ", "")))

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
    return "DE89 2004 0060 " + digits[:4] + " " + digits[4:8] + " " + digits[8:]

def init_state():
    d = dict(
        step=1, name="", geburtsdatum=date(1990,1,1), iban_alt="", bank_alt="",
        psd2_consent=False, dsgvo_consent=False,
        partners=None, manual_partners=[], ki_done=False,
        iban_neu="", wechseldatum=None,
        sim_done=False, nps_score=None, demo_mode=False,
        start_time=None, end_time=None,
        active_persona=None,
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
        st.session_state.iban_alt = d["iban_alt"]
        st.session_state.bank_alt = d["bank_alt"]
        st.session_state.psd2_consent = True
        st.session_state.dsgvo_consent = True
        st.session_state.ki_done = True
        st.session_state.wechseldatum = biz_days_ahead(date.today(), 12)
        for wk in ["s1_bank_select", "s1_iban_input", "s1_name_input",
                   "s1_geb_input", "s1_psd2_cb", "s1_dsgvo_cb"]:
            if wk in st.session_state:
                del st.session_state[wk]

def apply_persona(persona_id):
    """Load all data for a persona profile."""
    p = PERSONAS[persona_id]
    cust = p["customer"]
    st.session_state.active_persona = persona_id
    st.session_state.name = cust["name"]
    st.session_state.geburtsdatum = cust["geburtsdatum"]
    st.session_state.iban_alt = cust["iban_alt"]
    st.session_state.bank_alt = cust["bank_alt"]
    st.session_state.psd2_consent = True
    st.session_state.dsgvo_consent = True
    st.session_state.ki_done = True
    st.session_state.wechseldatum = biz_days_ahead(date.today(), 12)
    st.session_state.partners = copy.deepcopy(p["partners"])
    for partner in st.session_state.partners:
        partner["selected"] = True
    st.session_state.manual_partners = []
    st.session_state.sim_done = False
    st.session_state.nps_score = None
    st.session_state.end_time = None
    # Clear cached widget keys so Streamlit picks up new values
    for wk in ["s1_bank_select", "s1_iban_input", "s1_name_input",
               "s1_geb_input", "s1_psd2_cb", "s1_dsgvo_cb"]:
        if wk in st.session_state:
            del st.session_state[wk]

def conf_dot(confidence):
    if confidence >= 90:
        return '<span class="status-dot dot-green"></span><span class="status-label">Automatisch erkannt</span>'
    elif confidence >= 70:
        return '<span class="status-dot dot-yellow"></span><span class="status-label">Bitte pr\u00fcfen</span>'
    else:
        return '<span class="status-dot dot-red"></span><span class="status-label">Bitte pr\u00fcfen</span>'

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
        '<span class="timer-value">' + time_str + '</span></span>'
        + right_html +
        '</div>', unsafe_allow_html=True)

# ── Layout ───────────────────────────────────────────────────────────────────
def render_header():
    st.markdown("""<div class="gfs-header">
        <h1>Global Finance Solutions SE</h1>
        <p>KI-Kontowechselservice &mdash; SteerCo Prototyp 09.06.2026</p>
    </div>""", unsafe_allow_html=True)
def render_steps(cur):
    labels = ["1 Identifikation","2 KI-Analyse","3 Neues Konto","4 \u00dcbertragung","5 Abschluss"]
    pills = ""
    for i, l in enumerate(labels, 1):
        cls = "step-done" if i < cur else ("step-active" if i == cur else "step-todo")
        pills += '<span class="step-pill ' + cls + '">' + l + '</span>'
    st.markdown('<div class="steps-bar">' + pills + '</div>', unsafe_allow_html=True)

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
    iban = st.text_input("IBAN (alte Bank)", value=st.session_state.iban_alt,
                         placeholder="DE00 0000 0000 0000 0000 00", key="s1_iban_input")
    name = st.text_input("Kundenname", value=st.session_state.name,
                         placeholder="Julia Bergmann", key="s1_name_input")
    geb = st.date_input("Geburtsdatum", value=st.session_state.geburtsdatum,
                        min_value=date(1930,1,1), max_value=date(2010,12,31), key="s1_geb_input")

    psd2 = st.checkbox(
        u"Ich erteile Global Finance Solutions SE die Einwilligung, meine Kontodaten gem\u00e4\u00df PSD2 abzurufen",
        value=st.session_state.psd2_consent, key="s1_psd2_cb")
    dsgvo = st.checkbox(
        u"Ich stimme der Verarbeitung meiner Daten gem\u00e4\u00df DSGVO zu",
        value=st.session_state.dsgvo_consent, key="s1_dsgvo_cb")

    st.session_state.update(iban_alt=iban, name=name, geburtsdatum=geb,
                            bank_alt=bank_alt, psd2_consent=psd2, dsgvo_consent=dsgvo)
    st.markdown('</div>', unsafe_allow_html=True)

    ready = all([name.strip(), validate_iban(iban), bank_alt, psd2, dsgvo])
    if st.button("Weiter", key="s1_next", disabled=not ready):
        st.session_state.step = 2
        st.rerun()
    if not ready:
        st.caption(u"Bitte alle Felder ausf\u00fcllen und Einwilligungen erteilen.")

# ── Step 2 ───────────────────────────────────────────────────────────────────
def page_step2():
    if not st.session_state.ki_done:
        st.markdown('<div class="card"><h3>KI analysiert Ihre Kontodaten...</h3></div>', unsafe_allow_html=True)
        bar = st.progress(0, text="Transaktionen der letzten 24 Monate werden analysiert...")
        for i in range(100):
            time.sleep(0.02)
            bar.progress(i + 1, text="NLP-Analyse l\u00e4uft... " + str(i+1) + "%")
        st.session_state.ki_done = True
        time.sleep(0.3)
        st.rerun()

    st.markdown('<div class="card"><h3>Schritt 2 &mdash; KI-Analyse der Kontobewegungen</h3>', unsafe_allow_html=True)
    st.markdown("""<div class="info-box">Durchschnittlicher Kunde hat 23 Zahlungspartner &mdash;
        kennt aber nur 12-15 bewusst. Unsere KI erkennt alle.</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Gabi warning banner
    if st.session_state.active_persona == "gabi":
        st.markdown(
            '<div class="warning-banner"><strong>Kritische Zahlungen erkannt</strong> '
            '&mdash; diese werden bevorzugt behandelt und zuerst umgestellt.</div>',
            unsafe_allow_html=True)

    st.markdown('<p class="section-heading">Automatisch erkannte Zahlungspartner:</p>', unsafe_allow_html=True)
    partners = st.session_state.partners
    for i, p in enumerate(partners):
        rhythm_label = RHYTHM_LABELS.get(p["rhythm"], p["rhythm"])
        sign = "+" if p["category"] == "gehalt" else ""
        dot_html = conf_dot(p["confidence"])

        col_cb, col_info = st.columns([0.05, 0.95])
        with col_cb:
            sel = st.checkbox("Auswahl", value=p["selected"], key="p_cb_" + str(i),
                              label_visibility="collapsed")
            partners[i]["selected"] = sel
        with col_info:
            st.markdown(
                '<div class="ki-card">'
                '<span><strong>' + p["name"] + '</strong><br>'
                '<span class="sub">' + sign + str(format(p["amount"], ".2f")) + ' EUR / ' + rhythm_label + ' &middot; SEPA: ' + p["sepa_ref"] + '</span></span>'
                + dot_html +
                '</div>', unsafe_allow_html=True)

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

    # Manual add via tabs
    st.markdown('<p class="section-heading">Zahlungspartner manuell hinzuf\u00fcgen:</p>', unsafe_allow_html=True)
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
    tasks = _build_tasks()
    col_left, col_right = st.columns([1.2, 1])
    progress = st.progress(0, text="Starte \u00dcbertragung...")
    with col_right:
        log_area = st.empty()
    with col_left:
        task_area = st.empty()
    log_entries = []
    base_time = datetime.now()

    for idx, desc in enumerate(tasks):
        frac = (idx + 1) / len(tasks)
        rows = ""
        for j, d in enumerate(tasks):
            if j < idx:
                rows += '<div class="task-row task-done"><span class="badge-ok">OK</span> ' + d + '</div>'
            elif j == idx:
                rows += '<div class="task-row task-running"><span class="badge-wait">L\u00e4uft...</span> ' + d + '</div>'
            else:
                rows += '<div class="task-row task-pending"><span style="color:#ccc;">Ausstehend</span> ' + d + '</div>'
        task_area.markdown('<div class="card">' + rows + '</div>', unsafe_allow_html=True)

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

    rows = "".join('<div class="task-row task-done"><span class="badge-ok">OK</span> ' + d + '</div>' for d in tasks)
    task_area.markdown('<div class="card">' + rows + '</div>', unsafe_allow_html=True)
    progress.progress(1.0, text="Alle Aufgaben abgeschlossen")

def _show_sim_done():
    tasks = _build_tasks()
    st.markdown('<div class="success-box">Alle \u00dcbertragungen erfolgreich abgeschlossen.</div>', unsafe_allow_html=True)
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

    st.button("Zum GFS Online-Banking", disabled=True, help="In der Produktivversion verf\u00fcgbar", key="s5_banking_btn")

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

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    init_state()
    render_header()
    render_timer()
    render_steps(st.session_state.step)
    render_sidebar()
    {1: page_step1, 2: page_step2, 3: page_step3, 4: page_step4, 5: page_step5}[st.session_state.step]()
    render_footer()

if __name__ == "__main__":
    main()
