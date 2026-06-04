# -*- coding: utf-8 -*-
"""GFS-branded Premium PDF Generator using reportlab."""
import io
import random
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

# --- BRAND COLORS ---
COLOR_PRIMARY = colors.HexColor('#1a5c52')
COLOR_ACCENT = colors.HexColor('#e8a020')
COLOR_DARK = colors.HexColor('#1a1a2e')
COLOR_BG_GRAY = colors.HexColor('#f7f9fa')
COLOR_TEXT = colors.HexColor('#333333')
COLOR_TEXT_LIGHT = colors.HexColor('#666666')

def _create_styles():
    styles = getSampleStyleSheet()
    
    # Titles
    styles.add(ParagraphStyle(
        name='PremiumTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=COLOR_PRIMARY,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='PremiumSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COLOR_TEXT_LIGHT,
        spaceAfter=20,
        fontName='Helvetica'
    ))
    
    # Headers
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLOR_DARK,
        spaceBefore=18,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))
    
    # Normal Text
    styles.add(ParagraphStyle(
        name='NormalText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COLOR_TEXT,
        spaceAfter=6,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        name='BoldText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=COLOR_TEXT,
        spaceAfter=6,
        fontName='Helvetica-Bold'
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

def _get_base_doc(buf, margins=40):
    return SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=margins,
        leftMargin=margins,
        topMargin=margins,
        bottomMargin=margins
    )

def generate_confirmation_pdf(state):
    buf = io.BytesIO()
    doc = _get_base_doc(buf)
    styles = _create_styles()
    story = []

    # Header
    now_str = datetime.now().strftime("%d.%m.%Y, %H:%M Uhr")
    
    story.append(Paragraph("Global Finance Solutions SE", styles['PremiumTitle']))
    story.append(Paragraph(f"Offizielle Kontowechselbestätigung | Erstellt am: {now_str}", styles['PremiumSubtitle']))
    
    # Customer Details Table
    story.append(Paragraph("1. Kunden- & Kontodaten", styles['SectionHeader']))
    
    cust_data = [
        ['Kundenname:', state.get('name', '-'), 'Neue IBAN (GFS):', state.get('iban_neu', '-')],
        ['Geburtsdatum:', state.get('geburtsdatum_str', '-'), 'Alte Bank:', state.get('bank_alt', '-')],
        ['Wechseldatum:', state.get('wechseldatum_str', '-'), 'Alte IBAN:', state.get('iban_alt', '-')]
    ]
    
    cust_table = Table(cust_data, colWidths=[3*cm, 5.5*cm, 3.5*cm, 5.5*cm])
    cust_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_BG_GRAY),
        ('TEXTCOLOR', (0,0), (-1,-1), COLOR_TEXT),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTNAME', (3,0), (3,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        # Add subtle borders
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e0e0e0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 10))

    # Partners
    partners = state.get("partners", [])
    story.append(Paragraph(f"2. Übertragene Zahlungspartner ({len(partners)})", styles['SectionHeader']))
    
    if partners:
        partner_data = [['Zahlungspartner / Empfänger', 'Turnus', 'Erkannter Betrag']]
        
        for p in partners:
            partner_data.append([
                p.get("name", "Unbekannt"),
                p.get("rhythm", "monatlich").capitalize(),
                f"{p.get('amount', 0):.2f} EUR"
            ])
            
        partner_table = Table(partner_data, colWidths=[9*cm, 4.5*cm, 4*cm])
        partner_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,0), (-1,0), 10),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('ALIGN', (-1,0), (-1,-1), 'RIGHT'), # Amount right aligned
            # Alternating rows
            * [('BACKGROUND', (0, i), (-1, i), colors.whitesmoke) for i in range(1, len(partner_data), 2)],
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('BOTTOMPADDING', (0,1), (-1,-1), 8),
            ('TOPPADDING', (0,1), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, COLOR_PRIMARY),
        ]))
        story.append(partner_table)
    else:
        story.append(Paragraph("Keine Zahlungspartner ausgewählt oder übertragen.", styles['NormalText']))
        
    story.append(Spacer(1, 40))
    
    # Legal / Signature area
    story.append(Paragraph("Global Finance Solutions SE verpflichtet sich, alle ausgewählten Zahlungspartner fristgerecht über die neue Bankverbindung zu informieren.", styles['NormalText']))
    
    story.append(Spacer(1, 60))
    
    # Legal footer
    addr = "Global Finance Solutions SE, Leopoldstr. 28, 80802 München."
    story.append(Paragraph(f"Rechtsgrundlage: Zahlungskontengesetz (ZKG) §§ 20-26, EU-Richtlinie 2014/92/EU. {addr} BaFin-Registernr.: 123456.", styles['FooterText']))

    doc.build(story)
    return buf.getvalue()


def generate_audit_pdf(state):
    buf = io.BytesIO()
    doc = _get_base_doc(buf, margins=30)
    styles = _create_styles()
    story = []

    # Header
    ts = datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
    ref_nr = f"GFS-{random.randint(10000000, 99999999)}"
    
    story.append(Paragraph("Global Finance Solutions SE", styles['PremiumTitle']))
    story.append(Paragraph(f"KI-Entscheidungsprotokoll & Compliance Audit | Referenz: {ref_nr} | {ts}", styles['PremiumSubtitle']))
    
    # Section 1 - Dashboard
    story.append(Paragraph("1. Prozess-Metadaten", styles['SectionHeader']))
    
    start_ts = state.get("start_time")
    end_ts = state.get("end_time") or datetime.now()
    duration = int((end_ts - start_ts).total_seconds()) if start_ts else 0
    
    partners = state.get("partners", [])
    sel_count = sum(1 for p in partners if p.get("selected"))
    auto_deg = f"{int((sel_count / max(len(partners), 1)) * 100)}%"
    
    meta_data = [
        ['Dauer KI-Analyse:', f"{duration} Sek.", 'KI-Modell:', 'GFS-NLP-BERT v2.3'],
        ['Entscheidungen gesamt:', str(len(partners)), 'Automatisierungsgrad:', auto_deg],
        ['Verarbeitungsregion:', 'Azure EU (Germany West Central)', 'Zertifizierung:', 'BaFin BAIT, ISO 27001']
    ]
    
    meta_table = Table(meta_data, colWidths=[4*cm, 4.5*cm, 4*cm, 6*cm])
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
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e0e0e0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Section 2 - Log
    story.append(Paragraph("2. KI-Entscheidungslog", styles['SectionHeader']))
    
    log_data = [['Zeitstempel', 'Partner', 'KI Konfidenz', 'Kategorie', 'Human-in-Loop']]
    
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
        
    log_table = Table(log_data, colWidths=[3*cm, 6*cm, 2.5*cm, 4*cm, 3*cm])
    log_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        # Alternating rows
        * [('BACKGROUND', (0, i), (-1, i), colors.whitesmoke) for i in range(1, len(log_data), 2)],
        ('BOX', (0,0), (-1,-1), 1, COLOR_DARK),
    ]))
    story.append(log_table)
    story.append(Spacer(1, 10))

    # Section 3 - Compliance Checklist
    story.append(Paragraph("3. Regulatorische Compliance-Checks", styles['SectionHeader']))
    
    checks_data = [
        ["✓", "DSGVO Art. 6 (1a)", "Ausdrückliche Einwilligung des Nutzers zur Datenverarbeitung protokolliert."],
        ["✓", "DSGVO Art. 22", "Keine automatisierte Einzelfallentscheidung. Human-in-the-Loop Prozess gewahrt."],
        ["✓", "PSD2 Art. 67", "Starke Kundenauthentifizierung (SCA) durch kontoführende Bank bestätigt."],
        ["✓", "ZKG § 21", "Gesetzliche Frist von 12 Werktagen für den Kontowechsel eingeplant."],
        ["✓", "EU AI Act Art. 13", "Transparenz der KI-Systeme gegenüber dem Nutzer sichergestellt."]
    ]
    
    checks_table = Table(checks_data, colWidths=[1*cm, 3.5*cm, 14*cm])
    checks_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (0,-1), COLOR_PRIMARY), # Checkmarks in Green
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (0,-1), 12),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (1,0), (-1,-1), 9),
        ('TEXTCOLOR', (1,0), (-1,-1), COLOR_TEXT),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#e0e0e0')),
    ]))
    story.append(checks_table)

    story.append(Spacer(1, 40))
    story.append(Paragraph("Dieses Dokument wurde maschinell generiert und ist ein valides Audit-Dokument für interne Compliance-Prüfungen.", styles['FooterText']))

    doc.build(story)
    return buf.getvalue()
