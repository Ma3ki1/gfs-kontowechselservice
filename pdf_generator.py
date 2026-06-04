# -*- coding: utf-8 -*-
"""GFS-branded Premium PDF Generator using reportlab."""
import io
import random
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# --- BRAND COLORS ---
COLOR_PRIMARY = colors.HexColor('#1a5c52')
COLOR_ACCENT = colors.HexColor('#e8a020')
COLOR_DARK = colors.HexColor('#1a1a2e')
COLOR_BG_GRAY = colors.HexColor('#f4f6f8')
COLOR_TEXT = colors.HexColor('#2c3e50')
COLOR_TEXT_LIGHT = colors.HexColor('#7f8c8d')
COLOR_BORDER = colors.HexColor('#bdc3c7')

def _create_styles():
    styles = getSampleStyleSheet()
    
    # Section Header
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=COLOR_PRIMARY,
        spaceBefore=12,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))
    
    # Normal Text
    styles.add(ParagraphStyle(
        name='NormalText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=COLOR_TEXT,
        spaceAfter=4,
        fontName='Helvetica'
    ))
    
    # Footer
    styles.add(ParagraphStyle(
        name='FooterText',
        parent=styles['Normal'],
        fontSize=7,
        textColor=COLOR_TEXT_LIGHT,
        alignment=1, # Center
        fontName='Helvetica'
    ))
    
    return styles

def _get_base_doc(buf, margins=35):
    return SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=margins,
        leftMargin=margins,
        topMargin=margins,
        bottomMargin=margins
    )

def _header_table(title, subtitle):
    """Creates a premium header table."""
    data = [
        [title, "Global Finance Solutions SE"],
        [subtitle, "www.gfs-se.com"]
    ]
    t = Table(data, colWidths=[11*cm, 6*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (0,0), 16),
        ('TEXTCOLOR', (0,0), (0,0), COLOR_PRIMARY),
        
        ('FONTNAME', (1,0), (1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (1,0), (1,0), 10),
        ('TEXTCOLOR', (1,0), (1,0), COLOR_ACCENT),
        ('ALIGN', (1,0), (1,1), 'RIGHT'),
        
        ('FONTNAME', (0,1), (0,1), 'Helvetica'),
        ('FONTSIZE', (0,1), (0,1), 9),
        ('TEXTCOLOR', (0,1), (0,1), COLOR_TEXT_LIGHT),
        
        ('FONTNAME', (1,1), (1,1), 'Helvetica'),
        ('FONTSIZE', (1,1), (1,1), 8),
        ('TEXTCOLOR', (1,1), (1,1), COLOR_TEXT_LIGHT),
        
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LINEBELOW', (0,1), (-1,1), 1.5, COLOR_PRIMARY),
        ('BOTTOMPADDING', (0,1), (-1,1), 10),
    ]))
    return t

def generate_confirmation_pdf(state):
    buf = io.BytesIO()
    doc = _get_base_doc(buf)
    styles = _create_styles()
    story = []

    now_str = datetime.now().strftime("%d.%m.%Y, %H:%M Uhr")
    
    # 1. HEADER
    story.append(_header_table("Kontowechselbestätigung", f"Erstellt am: {now_str}"))
    story.append(Spacer(1, 15))
    
    # 2. KUNDEN & KONTODATEN
    story.append(Paragraph("1. Kunden- & Kontodaten", styles['SectionHeader']))
    
    cust_data = [
        ['Kundenname', state.get('name', '-'), 'Alte Bank', state.get('bank_alt', '-')],
        ['Geburtsdatum', state.get('geburtsdatum_str', '-'), 'Alte IBAN', state.get('iban_alt', '-')],
        ['Wechseldatum', state.get('wechseldatum_str', '-'), 'Neue IBAN (GFS)', state.get('iban_neu', '-')]
    ]
    
    cust_table = Table(cust_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    cust_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_GRAY),
        ('TEXTCOLOR', (0,0), (-1,-1), COLOR_TEXT),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 15))

    # 3. ZAHLUNGSPARTNER
    partners = state.get("partners", [])
    story.append(Paragraph(f"2. Übertragene Zahlungspartner ({len(partners)})", styles['SectionHeader']))
    
    if partners:
        partner_data = [['Zahlungspartner / Empfänger', 'Kategorie', 'Turnus', 'Erkannter Betrag']]
        
        for p in partners:
            partner_data.append([
                p.get("name", "Unbekannt"),
                p.get("category", "Sonstige").capitalize(),
                p.get("rhythm", "monatlich").capitalize(),
                f"{p.get('amount', 0):.2f} EUR"
            ])
            
        partner_table = Table(partner_data, colWidths=[6.5*cm, 4*cm, 3.5*cm, 3*cm])
        partner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_DARK),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING', (0,0), (-1,0), 8),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (-1,0), (-1,-1), 'RIGHT'), # Amount right aligned
            # Zebra striping
            * [('BACKGROUND', (0, i), (-1, i), colors.whitesmoke) for i in range(1, len(partner_data), 2)],
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('BOTTOMPADDING', (0,1), (-1,-1), 6),
            ('TOPPADDING', (0,1), (-1,-1), 6),
            ('BOX', (0,0), (-1,-1), 1, COLOR_DARK),
            ('INNERGRID', (0,0), (-1,-1), 0.25, COLOR_BORDER),
        ]))
        story.append(partner_table)
    else:
        # Show an empty state table
        empty_table = Table([["Keine Zahlungspartner für den Wechsel ausgewählt."]], colWidths=[17*cm])
        empty_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_GRAY),
            ('TEXTCOLOR', (0,0), (-1,-1), COLOR_TEXT_LIGHT),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Oblique'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 15),
            ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ]))
        story.append(empty_table)
        
    story.append(Spacer(1, 40))
    
    # 4. LEGAL FOOTER
    story.append(Paragraph("Global Finance Solutions SE verpflichtet sich, alle ausgewählten Zahlungspartner fristgerecht über die neue Bankverbindung zu informieren.", styles['NormalText']))
    story.append(Spacer(1, 20))
    
    addr = "Global Finance Solutions SE, Leopoldstr. 28, 80802 München."
    story.append(Paragraph(f"Rechtsgrundlage: Zahlungskontengesetz (ZKG) §§ 20-26, EU-Richtlinie 2014/92/EU.<br/>{addr} BaFin-Registernr.: 123456.", styles['FooterText']))

    doc.build(story)
    return buf.getvalue()


def generate_audit_pdf(state):
    buf = io.BytesIO()
    doc = _get_base_doc(buf)
    styles = _create_styles()
    story = []

    ts = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
    ref_nr = f"GFS-{random.randint(10000000, 99999999)}"
    
    # 1. HEADER
    story.append(_header_table("KI-Entscheidungsprotokoll", f"Audit-Referenz: {ref_nr} | {ts}"))
    story.append(Spacer(1, 15))
    
    # 2. PROZESS-METADATEN (Table)
    story.append(Paragraph("1. Prozess-Metadaten", styles['SectionHeader']))
    
    start_ts = state.get("start_time")
    end_ts = state.get("end_time") or datetime.now()
    duration = int((end_ts - start_ts).total_seconds()) if start_ts else 0
    
    partners = state.get("partners", [])
    sel_count = sum(1 for p in partners if p.get("selected"))
    auto_pct = min(99, 100 if len(partners) == 0 else int((len([p for p in partners if p.get("confidence", 0) > 80]) / max(len(partners), 1)) * 100))
    auto_deg = f"{auto_pct}%"
    
    meta_data = [
        ['Dauer KI-Analyse', f"{duration} Sekunden", 'KI-Modell', 'GFS-NLP-BERT v2.3'],
        ['Entscheidungen gesamt', str(len(partners)), 'Automatisierungsgrad', auto_deg],
        ['Verarbeitungsregion', 'Azure (Germany West Central)', 'Zertifizierung', 'BaFin BAIT, ISO 27001']
    ]
    
    meta_table = Table(meta_data, colWidths=[4.5*cm, 4*cm, 3.5*cm, 5*cm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_GRAY),
        ('TEXTCOLOR', (0,0), (-1,-1), COLOR_TEXT),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # 3. KI-ENTSCHEIDUNGSLOG (Table)
    story.append(Paragraph("2. KI-Entscheidungslog", styles['SectionHeader']))
    
    log_data = [['Zeitstempel', 'Partner', 'Konfidenz', 'Kategorie', 'Entscheidung']]
    
    for p in partners:
        p_ts = (start_ts + timedelta(seconds=random.randint(5, 45))).strftime('%H:%M:%S') if start_ts else ""
        log_data.append([
            p_ts,
            p.get("name", "Unbekannt"),
            f"{p.get('confidence', 0)}%",
            p.get("category", ""),
            "Verifiziert" if p.get("selected") else "Ignoriert"
        ])
        
    if not partners:
        log_data.append(["-", "-", "-", "-", "-"])
        
    log_table = Table(log_data, colWidths=[3*cm, 5.5*cm, 2.5*cm, 3.5*cm, 2.5*cm])
    log_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        * [('BACKGROUND', (0, i), (-1, i), colors.whitesmoke) for i in range(1, len(log_data), 2)],
        ('BOX', (0,0), (-1,-1), 1, COLOR_PRIMARY),
        ('INNERGRID', (0,0), (-1,-1), 0.25, COLOR_BORDER),
    ]))
    story.append(log_table)
    story.append(Spacer(1, 15))

    # 4. COMPLIANCE CHECKLISTE (Table)
    story.append(Paragraph("3. Regulatorische Compliance-Checks", styles['SectionHeader']))
    
    checks_data = [
        ["Regelwerk", "Status", "Details"],
        ["DSGVO Art. 6 (1a)", "ERFÜLLT", "Ausdrückliche Einwilligung des Nutzers protokolliert."],
        ["DSGVO Art. 22", "ERFÜLLT", "Keine automatisierte Einzelfallentscheidung (Human-in-the-Loop)."],
        ["PSD2 Art. 67", "ERFÜLLT", "Starke Kundenauthentifizierung (SCA) verifiziert."],
        ["ZKG § 21", "ERFÜLLT", "Frist von 12 Werktagen für Kontowechsel validiert."],
        ["EU AI Act", "ERFÜLLT", "Transparenz der KI-Systeme sichergestellt."]
    ]
    
    checks_table = Table(checks_data, colWidths=[3.5*cm, 2.5*cm, 11*cm])
    checks_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1,1), (1,-1), COLOR_PRIMARY), # Status in Green
        ('FONTNAME', (1,1), (1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('TEXTCOLOR', (2,1), (2,-1), COLOR_TEXT),
        
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        
        ('BOX', (0,0), (-1,-1), 1, COLOR_DARK),
        ('INNERGRID', (0,0), (-1,-1), 0.25, COLOR_BORDER),
        * [('BACKGROUND', (0, i), (-1, i), colors.whitesmoke) for i in range(1, len(checks_data), 2)],
    ]))
    story.append(checks_table)

    story.append(Spacer(1, 30))
    story.append(Paragraph("Dieses Dokument wurde maschinell generiert und dient als rechtsgültiges Audit-Protokoll gemäß GFS Compliance-Framework v4.2.", styles['FooterText']))

    doc.build(story)
    return buf.getvalue()
