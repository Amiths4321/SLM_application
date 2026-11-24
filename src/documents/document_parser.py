
import pymupdf
from pathlib import Path


def extract_document_text(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        document = pymupdf.open(file_path)
        text = "\n".join(
            page.get_text() for page in document
        )
        document.close()
        return text

    elif suffix == ".txt":
        return file_path.read_text(encoding="utf-8")

    else:
        raise ValueError("Only PDF and TXT documents are supported.")


if __name__ == "__main__":
    path = input("Enter invoice or delivery note path: ").strip().strip('"')

    text = extract_document_text(path)

    print("\nExtracted Document Text")
    print("=" * 50)
    print(text)
