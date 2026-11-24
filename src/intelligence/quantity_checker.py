
import re
import json


def extract_items(text):
    pattern = (
        r"\d+\.\s*(.*?)\s*-\s*Quantity:\s*(\d+)"
    )

    matches = re.findall(pattern, text, re.IGNORECASE)

    return {
        name.strip().lower(): int(quantity)
        for name, quantity in matches
    }


def compare_quantities(ordered_text, received_text):

    ordered = extract_items(ordered_text)
    received = extract_items(received_text)

    all_items = sorted(set(ordered) | set(received))

    results = []

    for item in all_items:
        ordered_qty = ordered.get(item, 0)
        received_qty = received.get(item, 0)

        difference = received_qty - ordered_qty

        if difference == 0:
            status = "MATCHED"
        elif difference < 0:
            status = "SHORTAGE"
        else:
            status = "EXCESS"

        results.append({
            "item": item,
            "ordered_quantity": ordered_qty,
            "received_quantity": received_qty,
            "difference": difference,
            "status": status
        })

    return results


if __name__ == "__main__":

    ordered_text = """
    1. Cardboard Boxes - Quantity: 100
    2. Bubble Wrap Rolls - Quantity: 20
    3. Packing Tape - Quantity: 50
    """

    received_text = """
    1. Cardboard Boxes - Quantity: 100
    2. Bubble Wrap Rolls - Quantity: 18
    3. Packing Tape - Quantity: 55
    """

    results = compare_quantities(ordered_text, received_text)

    print(json.dumps(results, indent=4))
