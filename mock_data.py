"""Mock data for GFS Kontowechselservice."""
from datetime import date

DEMO_CUSTOMER = {
    "name": "Julia Bergmann",
    "geburtsdatum": date(1991, 3, 22),
    "iban_alt": "DE89 3704 0044 0532 0130 00",
    "bank_alt": "Deutsche Bank",
}

BANK_SUGGESTIONS = [
    "Deutsche Bank", "Sparkasse", "Volksbank", "ING",
    "Commerzbank", "DKB", "Comdirect", "Postbank",
    "HypoVereinsbank", "Targobank", "N26",
]

AI_DETECTED_PARTNERS = [
    {"name": "Netflix Streaming", "amount": 17.99, "rhythm": "monatlich",
     "confidence": 98, "sepa_ref": "NF-FLIX", "category": "lastschrift"},
    {"name": "Spotify (via PayPal)", "amount": 11.99, "rhythm": "monatlich",
     "confidence": 94, "sepa_ref": "PPSPOTIFY", "category": "lastschrift"},
    {"name": "Telekom Deutschland", "amount": 89.00, "rhythm": "monatlich",
     "confidence": 99, "sepa_ref": "DTAG", "category": "lastschrift"},
    {"name": "Stadtwerke München", "amount": 127.50, "rhythm": "monatlich",
     "confidence": 97, "sepa_ref": "SWM-STROM", "category": "lastschrift"},
    {"name": "Amazon Prime", "amount": 8.99, "rhythm": "monatlich",
     "confidence": 96, "sepa_ref": "AMZN PMTS", "category": "lastschrift"},
    {"name": "Fitnessstudio FitX", "amount": 29.90, "rhythm": "monatlich",
     "confidence": 91, "sepa_ref": "FITX-MBR", "category": "lastschrift"},
    {"name": "Innovatech GmbH", "amount": 3200.00, "rhythm": "monatlich",
     "confidence": 100, "sepa_ref": "GEHALT", "category": "gehalt"},
    {"name": "Wohnbau GmbH", "amount": 950.00, "rhythm": "monatlich",
     "confidence": 99, "sepa_ref": "MIETE", "category": "dauerauftrag"},
    {"name": "AOK Bayern", "amount": 215.00, "rhythm": "monatlich",
     "confidence": 98, "sepa_ref": "KV-BEITRAG", "category": "lastschrift"},
    {"name": "HelloFresh", "amount": 59.90, "rhythm": "zweiwöchentlich",
     "confidence": 89, "sepa_ref": "HF-BOX", "category": "lastschrift"},
]

RHYTHM_LABELS = {
    "monatlich": "monatlich",
    "zweiwöchentlich": "alle 2 Wochen",
    "vierteljährlich": "vierteljährlich",
    "halbjährlich": "halbjährlich",
    "jährlich": "jährlich",
}

# ── Persona Profiles ─────────────────────────────────────────────────────────
PERSONA_NINA = {
    "id": "nina",
    "label": "Digital Native Nina",
    "alter": 28,
    "beruf": "Marketing Managerin",
    "bank": "N26",
    "color": "#1a5c52",
    "badge": "Komplex \u2014 15 Partner",
    "badge_color": "#1a5c52",
    "customer": {
        "name": "Nina Lehmann",
        "geburtsdatum": date(1998, 5, 14),
        "iban_alt": "DE72 1001 0010 0845 2319 07",
        "bank_alt": "N26",
    },
    "partners": [
        {"name": "Netflix Streaming", "amount": 17.99, "rhythm": "monatlich", "confidence": 98, "sepa_ref": "NF-FLIX", "category": "lastschrift"},
        {"name": "Spotify Premium", "amount": 9.99, "rhythm": "monatlich", "confidence": 96, "sepa_ref": "SPOTIFY", "category": "lastschrift"},
        {"name": "Disney+ Abo", "amount": 8.99, "rhythm": "monatlich", "confidence": 95, "sepa_ref": "DISNEY", "category": "lastschrift"},
        {"name": "Apple Music", "amount": 10.99, "rhythm": "monatlich", "confidence": 93, "sepa_ref": "APPLE-M", "category": "lastschrift"},
        {"name": "HelloFresh", "amount": 49.90, "rhythm": "zweiwöchentlich", "confidence": 88, "sepa_ref": "HF-BOX", "category": "lastschrift"},
        {"name": "Lieferando Plus", "amount": 4.99, "rhythm": "monatlich", "confidence": 87, "sepa_ref": "LIEFER", "category": "lastschrift"},
        {"name": "NordVPN", "amount": 3.49, "rhythm": "monatlich", "confidence": 92, "sepa_ref": "NORDVPN", "category": "lastschrift"},
        {"name": "Adobe Creative Cloud", "amount": 61.95, "rhythm": "monatlich", "confidence": 97, "sepa_ref": "ADOBE-CC", "category": "lastschrift"},
        {"name": "Dropbox Plus", "amount": 11.99, "rhythm": "monatlich", "confidence": 91, "sepa_ref": "DROPBOX", "category": "lastschrift"},
        {"name": "Amazon Prime", "amount": 8.99, "rhythm": "monatlich", "confidence": 96, "sepa_ref": "AMZN PMTS", "category": "lastschrift"},
        {"name": "Fitnessstudio McFit", "amount": 24.90, "rhythm": "monatlich", "confidence": 94, "sepa_ref": "MCFIT", "category": "lastschrift"},
        {"name": "Audible Abo", "amount": 9.95, "rhythm": "monatlich", "confidence": 93, "sepa_ref": "AUDIBLE", "category": "lastschrift"},
        {"name": "Wohngemeinschaft Miete", "amount": 680.00, "rhythm": "monatlich", "confidence": 99, "sepa_ref": "WG-MIETE", "category": "dauerauftrag"},
        {"name": "Kreativagentur GmbH", "amount": 2800.00, "rhythm": "monatlich", "confidence": 100, "sepa_ref": "GEHALT", "category": "gehalt"},
        {"name": "Stadtwerke Berlin", "amount": 85.00, "rhythm": "monatlich", "confidence": 97, "sepa_ref": "SW-BLN", "category": "lastschrift"},
        {"name": "Digital Services LTD Zypern", "amount": 4.99, "rhythm": "monatlich", "confidence": 99, "sepa_ref": "FRAUD-ABO", "category": "fraud"},
    ],
}

PERSONA_THOMAS = {
    "id": "thomas",
    "label": "Traditioneller Thomas",
    "alter": 52,
    "beruf": "Abteilungsleiter",
    "bank": "Sparkasse",
    "color": "#e8a020",
    "badge": "Standard \u2014 8 Partner",
    "badge_color": "#e8a020",
    "customer": {
        "name": "Thomas Müller",
        "geburtsdatum": date(1974, 8, 3),
        "iban_alt": "DE44 7005 0000 0023 4567 89",
        "bank_alt": "Sparkasse",
    },
    "partners": [
        {"name": "Telekom Deutschland", "amount": 54.95, "rhythm": "monatlich", "confidence": 99, "sepa_ref": "DTAG", "category": "lastschrift"},
        {"name": "Stadtwerke München", "amount": 142.00, "rhythm": "monatlich", "confidence": 98, "sepa_ref": "SWM", "category": "lastschrift"},
        {"name": "AOK Bayern", "amount": 385.00, "rhythm": "monatlich", "confidence": 99, "sepa_ref": "AOK-KV", "category": "lastschrift"},
        {"name": "Hausverwaltung Weber", "amount": 1250.00, "rhythm": "monatlich", "confidence": 99, "sepa_ref": "MIETE-HV", "category": "dauerauftrag"},
        {"name": "Maschinenbau AG", "amount": 4200.00, "rhythm": "monatlich", "confidence": 100, "sepa_ref": "GEHALT", "category": "gehalt"},
        {"name": "ADAC Mitgliedschaft", "amount": 59.00, "rhythm": "jährlich", "confidence": 95, "sepa_ref": "ADAC", "category": "lastschrift"},
        {"name": "Süddeutsche Zeitung", "amount": 39.90, "rhythm": "monatlich", "confidence": 94, "sepa_ref": "SZ-ABO", "category": "lastschrift"},
        {"name": "Allianz Hausratversicherung", "amount": 28.50, "rhythm": "monatlich", "confidence": 97, "sepa_ref": "ALLIANZ-HR", "category": "lastschrift"},
    ],
}

PERSONA_GABI = {
    "id": "gabi",
    "label": "Gestresste Gabi",
    "alter": 35,
    "beruf": "Alleinerziehend, Teilzeit Pflege",
    "bank": "Volksbank",
    "color": "#c0392b",
    "badge": "Kritisch \u2014 maximale Sicherheit",
    "badge_color": "#c0392b",
    "is_critical": True,
    "customer": {
        "name": "Gabriele Fischer",
        "geburtsdatum": date(1991, 11, 27),
        "iban_alt": "DE65 6609 0800 0045 6789 01",
        "bank_alt": "Volksbank",
    },
    "partners": [
        {"name": "Wohnungsgenossenschaft Miete", "amount": 780.00, "rhythm": "monatlich", "confidence": 99, "sepa_ref": "WG-MIETE", "category": "dauerauftrag"},
        {"name": "Kita Sonnenblume Beitrag", "amount": 245.00, "rhythm": "monatlich", "confidence": 97, "sepa_ref": "KITA-SB", "category": "lastschrift"},
        {"name": "Familienkasse Kindergeld", "amount": 250.00, "rhythm": "monatlich", "confidence": 100, "sepa_ref": "KINDERGELD", "category": "gehalt"},
        {"name": "Telekom Festnetz", "amount": 39.95, "rhythm": "monatlich", "confidence": 98, "sepa_ref": "DTAG", "category": "lastschrift"},
        {"name": "E.ON Strom", "amount": 95.00, "rhythm": "monatlich", "confidence": 97, "sepa_ref": "EON-STR", "category": "lastschrift"},
        {"name": "REWE Lieferservice", "amount": 120.00, "rhythm": "monatlich", "confidence": 85, "sepa_ref": "REWE-LS", "category": "lastschrift"},
        {"name": "HUK Kinderversicherung", "amount": 18.50, "rhythm": "monatlich", "confidence": 96, "sepa_ref": "HUK-KV", "category": "lastschrift"},
        {"name": "Unterhaltszahlung Eingang", "amount": 450.00, "rhythm": "monatlich", "confidence": 100, "sepa_ref": "UNTERHALT", "category": "gehalt"},
        {"name": "Pflegedienst GmbH Gehalt", "amount": 1650.00, "rhythm": "monatlich", "confidence": 100, "sepa_ref": "GEHALT", "category": "gehalt"},
    ],
}

PERSONAS = {
    "nina": PERSONA_NINA,
    "thomas": PERSONA_THOMAS,
    "gabi": PERSONA_GABI,
}
