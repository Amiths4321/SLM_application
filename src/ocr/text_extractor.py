
from paddleocr import PaddleOCR
from pathlib import Path

class WarehouseOCR:

    def __init__(self):
        print("Loading PaddleOCR...")
        self.ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False
        )
        print("PaddleOCR loaded successfully.")

    def extract_text(self, image_path):
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        results = self.ocr.predict(str(image_path))

        extracted = []

        for result in results:
            data = result.json
            if isinstance(data, dict):
                data = data.get("res", data)

            texts = data.get("rec_texts", [])
            scores = data.get("rec_scores", [])

            for text, score in zip(texts, scores):
                extracted.append({
                    "text": text,
                    "confidence": round(float(score), 4)
                })

        return extracted


if __name__ == "__main__":
    ocr = WarehouseOCR()

    path = input("Enter image path: ").strip().strip('"')
    results = ocr.extract_text(path)

    print("\nExtracted Text")
    print("=" * 40)

    for item in results:
        print(item["text"], "| Confidence:", item["confidence"])
