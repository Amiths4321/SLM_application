
import json

from src.llm.ollama_client import generate_response
from src.intelligence.privacy_filter import mask_sensitive_information


def analyze_inspection(inspection):
    ocr_items = inspection.get("ocr", {}).get("extracted_text", [])

    raw_text = "\n".join(
        item.get("text", "")
        for item in ocr_items
    )

    safe_ocr_text = mask_sensitive_information(raw_text)

    detection = inspection.get("object_detection", {})

    safe_detection = {
        "total_objects": detection.get("total_objects", 0),
        "object_counts": detection.get("object_counts", {}),
        "detections": [
            {
                "object": item.get("object"),
                "confidence": item.get("confidence"),
                "bbox": item.get("bbox"),
            }
            for item in detection.get("detections", [])
        ],
    }

    prompt = f"""
You are an AI warehouse receiving inspection assistant.

Analyze the following evidence.

OBJECT DETECTION:
{json.dumps(safe_detection, indent=2)}

OCR TEXT (PERSONAL INFORMATION MASKED):
{safe_ocr_text}

Return valid JSON with these fields:
- summary
- shipping_label
- observations (array)
- verification_required (boolean)
- inspection_status

Use REVIEW_REQUIRED when evidence is incomplete or uncertain.
Do not invent missing information.
Do not claim packages or quantities are verified without evidence.
"""

    response = generate_response(prompt)

    try:
        report = json.loads(response)

        if not isinstance(report, dict):
            raise ValueError("Expected a JSON object.")

    except (json.JSONDecodeError, ValueError):
        report = {
            "summary": "AI response could not be parsed reliably.",
            "shipping_label": "",
            "observations": ["Manual inspection required."],
            "verification_required": True,
            "inspection_status": "REVIEW_REQUIRED",
        }

    return report


if __name__ == "__main__":
    sample_inspection = {
        "object_detection": {
            "total_objects": 1,
            "object_counts": {"person": 1},
            "detections": [
                {
                    "object": "person",
                    "confidence": 0.95,
                    "bbox": [10, 20, 100, 200],
                }
            ],
        },
        "ocr": {
            "extracted_text": [
                {"text": "Name: John Doe", "confidence": 0.99},
                {"text": "Phone: (555) 123-4567", "confidence": 0.98},
                {"text": "Email: john.doe@example.com", "confidence": 0.99},
                {"text": "PRIORITY MAIL", "confidence": 0.99},
            ]
        },
    }

    print("Testing privacy-protected Qwen analysis...")

    result = analyze_inspection(sample_inspection)

    print(json.dumps(result, indent=4))
