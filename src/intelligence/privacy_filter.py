
import re


def mask_sensitive_information(text):
    patterns = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "phone": r"(?<!\w)\+?\s*\(?\d[\d\s().-]{6,}\d(?!\w)",
        "zip_code": r"\b\d{5}(?:-\d{4})?\b",
    }

    for label, pattern in patterns.items():
        text = re.sub(
            pattern,
            f"[REDACTED_{label.upper()}]",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(
        r"(?im)^\s*(Name|Address)\s*:\s*.*$",
        lambda match: f"{match.group(1)}: [REDACTED]",
        text,
    )

    return text


if __name__ == "__main__":
    sample = """
    Name: John Doe
    Address: 1234 Elm Street
    Phone: (555) 123-4567
    Email: john.doe@example.com
    """

    print(mask_sensitive_information(sample))
