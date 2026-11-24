
import re
from src.documents.document_parser import extract_document_text


def extract_items(text):
    pattern = (
        r"\d+\.\s*(.*?)\s*-\s*Quantity:\s*(\d+)"
    )

    matches = re.findall(pattern, text, re.IGNORECASE)

    return {
        name.strip().lower(): int(quantity)
        for name, quantity in matches
    }


def compare_documents(ordered_text, received_text):
    ordered = extract_items(ordered_text)
    received = extract_items(received_text)

    all_items = sorted(set(ordered) | set(received))
    results = []

    for item in all_items:
        expected = ordered.get(item, 0)
        actual = received.get(item, 0)
        difference = actual - expected

        if difference == 0:
            status = "MATCHED"
        elif difference < 0:
            status = "SHORTAGE"
        else:
            status = "EXCESS"

        results.append({
            "item": item,
            "ordered": expected,
            "received": actual,
            "difference": difference,
            "status": status
        })

    return results


if __name__ == "__main__":
    ordered = extract_document_text(
        "data/samples/delivery_note.txt"
    )

    received = """
    1. Cardboard Boxes - Quantity: 100
    2. Bubble Wrap Rolls - Quantity: 18
    3. Packing Tape - Quantity: 55
    """

    print(compare_documents(ordered, received))
