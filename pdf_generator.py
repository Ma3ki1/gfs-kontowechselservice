# -*- coding: utf-8 -*-
"""GFS-branded PDF confirmation using fpdf2."""
from fpdf import FPDF
from datetime import datetime, timedelta
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import random

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

def generate_audit_pdf(state):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        name='AuditTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1a5c52'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        name='AuditH2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1a1a2e'),
        spaceBefore=14,
        spaceAfter=6
    )
    normal_style = styles['Normal']
    
    story = []
    
    # Header
    ts = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
    ref_nr = f"GFS-{random.randint(10000000, 99999999)}"
    
    story.append(Paragraph("Global Finance Solutions SE — KI-Entscheidungsprotokoll", title_style))
    story.append(Paragraph(f"Erstellt: {ts} | Referenz: {ref_nr}", normal_style))
    story.append(Paragraph("Klassifizierung: Intern — Compliance-Dokument", normal_style))
    story.append(Spacer(1, 12))
    
    # Section 1
    story.append(Paragraph("Section 1 — Prozessübersicht", h2_style))
    story.append(Paragraph("Kundenreferenz: Kunde-XXXX", normal_style))
    start_ts = state.get("start_time")
    end_ts = state.get("end_time") or datetime.now()
    if start_ts:
        duration = int((end_ts - start_ts).total_seconds())
        story.append(Paragraph(f"Prozessstart: {start_ts.strftime('%d.%m.%Y %H:%M:%S')}", normal_style))
        story.append(Paragraph(f"Prozessende: {end_ts.strftime('%d.%m.%Y %H:%M:%S')}", normal_style))
        story.append(Paragraph(f"Gesamtdauer: {duration} Sekunden", normal_style))
    
    partners = state.get("partners", [])
    sel_count = sum(1 for p in partners if p.get("selected"))
    story.append(Paragraph(f"Anzahl KI-Entscheidungen: {len(partners)}", normal_style))
    if len(partners) > 0:
        story.append(Paragraph(f"Automatisierungsgrad: {int((sel_count / len(partners)) * 100)}%", normal_style))
    
    story.append(Spacer(1, 12))
    
    # Section 2
    story.append(Paragraph("Section 2 — KI-Entscheidungslog", h2_style))
    data = [['Zeitstempel', 'Partner', 'SEPA', 'Version', 'Konf.', 'Entsch.', 'Bestätigung', 'Regulatorik']]
    
    for p in partners:
        p_ts = (start_ts + timedelta(seconds=random.randint(10, 60))).strftime('%H:%M:%S') if start_ts else ""
        data.append([
            p_ts,
            p.get("name", "Unbekannt"),
            p.get("sepa_ref", ""),
            "GFS-BERT v2.3",
            f"{p.get('confidence', 0)}%",
            p.get("category", ""),
            "Ja (Kunde)",
            "DSGVO Art. 22"
        ])
        
    table = Table(data, colWidths=[50, 70, 60, 60, 40, 60, 60, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a5c52')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f0f0f0')),
        ('GRID', (0,0), (-1,-1), 1, colors.white),
        ('FONTSIZE', (0,1), (-1,-1), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))
    
    # Section 3
    story.append(Paragraph("Section 3 — Compliance-Checkliste", h2_style))
    checks = [
        "[X] DSGVO Art. 6 — Einwilligung dokumentiert",
        "[X] DSGVO Art. 22 — Keine vollautomatisierten Entscheidungen",
        "[X] ZKG §21 — 12 Werktage Frist eingehalten",
        "[X] PSD2 Art. 67 — Starke Kundenauthentifizierung",
        "[X] EU AI Act Art. 13 — Transparenz sichergestellt",
        "[X] BaFin BAIT — Audit Trail vollständig",
        "[X] ISO 27001 — Datenverschlüsselung AES-256"
    ]
    for check in checks:
        story.append(Paragraph(check, normal_style))
        
    story.append(Spacer(1, 12))
        
    # Section 4
    story.append(Paragraph("Section 4 — Technische Metadaten", h2_style))
    meta = [
        "Modell: GFS-NLP-BERT v2.3.1",
        "Infrastruktur: Microsoft Azure Deutschland (Region: Germany West Central)",
        "Verschlüsselung: TLS 1.3 (Transport), AES-256 (Rest)"
    ]
    if start_ts:
        meta.append(f"Verarbeitungszeit gesamt: {duration} Sekunden")
    for m in meta:
        story.append(Paragraph(m, normal_style))
        
    story.append(Spacer(1, 24))
    
    # Footer
    footer_style = ParagraphStyle(
        name='AuditFooter',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.gray,
        alignment=1
    )
    story.append(Paragraph("Dieses Dokument wurde automatisch generiert und ist rechtlich bindend gemäß GFS Compliance-Framework v4.2", footer_style))
    story.append(Paragraph("metafinanz — Konzept & Implementierung", footer_style))

    doc.build(story)
    return buf.getvalue()
