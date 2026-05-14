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
    "HypoVereinsbank", "Targobank",
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
