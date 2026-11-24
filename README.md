
# WarehouseIQ — AI Warehouse Receiving & Inspection Copilot

An AI-assisted warehouse receiving and inspection application combining computer vision, OCR, local document processing, quantity reconciliation, and remote Small Language Model (SLM) inference.

## Overview

WarehouseIQ helps warehouse teams inspect incoming goods, extract information from delivery documents, compare ordered and received quantities, and generate AI-assisted inspection reports.

## Features

- **Object Detection:** YOLO26-based image detection.
- **OCR:** PaddleOCR 3.x text extraction.
- **Document Intelligence:** Extract text from PDF and TXT documents.
- **Quantity Reconciliation:** Identify matched quantities, shortages, and excess.
- **SLM Analysis:** Qwen inference through a remote Ollama server.
- **Privacy Filtering:** Basic masking of names, addresses, phone numbers, and email addresses before LLM inference.
- **Database:** SQLite inspection history.
- **Web Dashboard:** Streamlit interface.
- **REST API:** FastAPI endpoints for image inspection and AI analysis.

## Architecture

```text
Warehouse Image / Documents
          |
          v
    Streamlit Dashboard
          |
     +----+------+
     |           |
     v           v
  YOLO26      PaddleOCR
     |           |
     +-----+-----+
           |
           v
    Inspection Engine
           |
           v
     Privacy Filter
           |
           v
   Remote Ollama / Qwen
           |
           v
    AI Inspection Report
           |
           v
       SQLite DB
```

Document processing and quantity reconciliation are handled through separate modules.

## Technology Stack

| Component | Technology |
|---|---|
| Programming | Python |
| Object Detection | Ultralytics YOLO26 |
| OCR | PaddleOCR |
| Document Processing | PyMuPDF |
| AI Model | Qwen through Ollama |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| Data Processing | Pandas |
| Environment | Python virtual environment |

## Project Structure

```text
SLM application/
├── app.py
├── dashboard.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
├── models/
├── reports/
├── src/
│   ├── api.py
│   ├── database.py
│   ├── vision/
│   ├── ocr/
│   ├── documents/
│   ├── llm/
│   └── intelligence/
└── tests/
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Ollama

Copy `.env.example` to `.env`.

Update the private Ollama server URL and model name in `.env`.

Ensure the remote Ollama server is running and accessible from your machine.

## Run the Application

### Streamlit Dashboard

```bash
streamlit run dashboard.py
```

### FastAPI Backend

```bash
uvicorn app:app --reload --port 8001
```

API documentation:

```text
http://127.0.0.1:8001/docs
```

Health endpoint:

```text
http://127.0.0.1:8001/health
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/inspect` | Image inspection |
| POST | `/analyze` | AI-assisted inspection |
| GET | `/history` | Inspection history |

## Quantity Reconciliation

The application compares purchase order and delivery note quantities.

Example:

| Item | Ordered | Received | Result |
|---|---:|---:|---|
| Cardboard Boxes | 100 | 100 | MATCHED |
| Bubble Wrap Rolls | 20 | 18 | SHORTAGE |
| Packing Tape | 50 | 55 | EXCESS |

The current parser expects numbered item lines in the format:

`1. Item Name - Quantity: 100`

## Important Limitations

- The generic pretrained YOLO26 model is not specifically trained for warehouse package detection.
- Package-specific detection requires a suitable custom-trained model and dataset.
- OCR quality depends on image quality and document layout.
- Quantity reconciliation currently supports a specific text format.
- Privacy filtering is basic and does not guarantee complete removal of personal information.
- AI-generated reports require human verification.

## Privacy and Security

- Never commit `.env` or private credentials.
- Use synthetic or anonymized documents for public demonstrations.
- Do not publish customer documents, inspection images, or local databases.
- Review OCR data before sending it to a remote inference server.

## Project Status

Portfolio prototype — core image inspection, OCR, document extraction, quantity comparison, AI analysis, dashboard, and API workflows have been implemented and tested.

## Disclaimer

This application is a decision-support prototype. It does not replace professional warehouse inspection or independent verification of received goods.
