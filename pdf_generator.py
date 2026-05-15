# -*- coding: utf-8 -*-
"""GFS-branded PDF confirmation using fpdf2."""
from fpdf import FPDF
from datetime import datetime
import io


def generate_confirmation_pdf(state):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Header bar
    pdf.set_fill_color(26, 26, 46)
    pdf.rect(0, 0, 210, 38, "F")
    pdf.set_fill_color(26, 92, 82)
    pdf.rect(0, 38, 210, 3, "F")

    pdf.set_text_color(232, 160, 32)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(15, 10)
    pdf.cell(0, 10, "Global Finance Solutions SE", ln=True)

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_xy(15, 22)
    titel = "Kontowechselbest" + chr(228) + "tigung"
    pdf.cell(0, 8, titel, ln=True)

    # Body
    pdf.set_y(50)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 10)
    now_str = datetime.now().strftime("%d.%m.%Y, %H:%M Uhr")
    pdf.cell(0, 8, "Erstellt am: " + now_str, ln=True)
    pdf.ln(4)

    _section(pdf, "Kundendaten")
    _row(pdf, "Kundenname", state.get("name", "-"))
    _row(pdf, "Geburtsdatum", state.get("geburtsdatum_str", "-"))
    pdf.ln(4)

    _section(pdf, "Kontoinformationen")
    _row(pdf, "Alte Bank", state.get("bank_alt", "-"))
    _row(pdf, "Alte IBAN", state.get("iban_alt", "-"))
    _row(pdf, "Neue IBAN (GFS)", state.get("iban_neu", "-"))
    _row(pdf, "Kontomodell", "GFS Premium-Konto")
    _row(pdf, "Wechseldatum", state.get("wechseldatum_str", "-"))
    pdf.ln(4)

    # Partners
    partners = state.get("partners", [])
    section_title = chr(220) + "bertragene Zahlungspartner (" + str(len(partners)) + ")"
    _section(pdf, section_title)
    for p in partners:
        name = p.get("name", "?")
        amount = p.get("amount", 0)
        rhythm = p.get("rhythm", "monatlich")
        pdf.set_font("Helvetica", "", 9)
        line = "  - " + name + "  |  " + format(amount, ".2f") + " EUR  |  " + rhythm
        pdf.cell(0, 6, line, ln=True)

    if not partners:
        pdf.set_font("Helvetica", "I", 9)
        no_partners = "  Keine Zahlungspartner " + chr(252) + "bertragen."
        pdf.cell(0, 6, no_partners, ln=True)

    pdf.ln(8)

    # Legal footer
    pdf.set_draw_color(200, 200, 200)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(120, 120, 120)
    addr = "Global Finance Solutions SE, Leopoldstr. 28, 80802 M" + chr(252) + "nchen. "
    pdf.multi_cell(0, 4,
        "Rechtsgrundlage: Zahlungskontengesetz (ZKG) " + chr(167) + chr(167) + " 20-26, "
        "EU-Richtlinie 2014/92/EU.\n"
        + addr +
        "BaFin-Registernr.: 123456.\n"
        "Konzept & Prototyp: metafinanz Informationssysteme GmbH (Allianz Gruppe)."
    )

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def _section(pdf, title):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 92, 82)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_text_color(30, 30, 30)


def _row(pdf, label, value):
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(55, 6, label)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, str(value), ln=True)
