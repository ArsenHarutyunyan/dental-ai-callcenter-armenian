import re


def extract_phone(text: str):
    match = re.search(r"\+374\d{8}", text)
    return match.group() if match else None


def extract_time(text: str):
    patterns = [
        r"(վաղը\s+)?ժամը\s*\d{1,2}:\d{2}",
        r"\d{1,2}:\d{2}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()

    return None


def extract_name(text: str):
    patterns = [
        r"ես\s+([Ա-Ֆա-ֆA-Za-z]+)",
        r"իմ\s+անունը\s+([Ա-Ֆա-ֆA-Za-z]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1)
            return name.removesuffix("ն")

    return None


def extract_complaint(text: str):
    if "ցավ" in text or "ցավում" in text:
        return "Ատամի ցավ"

    if "արյուն" in text:
        return "Արյունահոսություն"

    if "ուռել" in text or "այտուց" in text:
        return "Այտուց"

    return None


def extract_patient_data(text: str):
    return {
        "patient_name": extract_name(text),
        "phone": extract_phone(text),
        "complaint": extract_complaint(text),
        "preferred_time": extract_time(text),
    }