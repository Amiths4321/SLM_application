import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.documents.document_parser import extract_document_text
from src.intelligence.quantity_checker import compare_quantities
from src.database import (
    get_inspections,
    initialize_database,
    save_inspection,
)
from src.intelligence.inspection_engine import WarehouseInspectionEngine
from src.intelligence.slm_inspector import analyze_inspection


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="WarehouseIQ | Inspection Copilot",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM STYLING (bright theme)
# --------------------------------------------------

st.markdown("""
<style>
    :root {
        --bg: #f3f8ff;
        --surface: #ffffff;
        --border: #c9defa;
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --accent: #06b6d4;
        --text: #1e293b;
        --heading: #0b1f4d;
        --muted: #5b6b82;
    }

    .stApp {
        background: linear-gradient(180deg, #eaf3ff 0%, #f8fbff 60%, #ffffff 100%);
        color: var(--text);
    }

    /* ---------- Global text colours ---------- */
    .stApp p,
    .stApp li,
    .stApp label,
    .stApp span,
    .stApp div[data-testid="stMarkdownContainer"] {
        color: var(--text);
    }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {
        color: var(--heading);
    }

    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stCaptionContainer"] * {
        color: var(--muted);
    }

    /* ---------- Sidebar ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #e9f2ff 100%);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: #1e3a6e;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--primary-dark);
    }

    [data-testid="stHeader"] {
        background-color: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* ---------- Hero ---------- */
    .hero {
        background: linear-gradient(115deg, #2563eb 0%, #0ea5e9 55%, #06d6c4 100%);
        padding: 30px;
        border-radius: 18px;
        box-shadow: 0 10px 28px rgba(37, 99, 235, 0.28);
        margin-bottom: 25px;
    }

    .hero h1 {
        color: #ffffff !important;
        font-size: 32px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #eaf6ff !important;
        font-size: 15px;
        margin-bottom: 0;
    }

    /* ---------- Section headings ---------- */
    .section-heading {
        font-size: 21px;
        font-weight: 700;
        color: var(--heading);
        margin: 12px 0 15px 0;
        padding-left: 12px;
        border-left: 5px solid var(--accent);
    }

    .small-muted {
        color: var(--muted);
        font-size: 13px;
    }

    /* ---------- Metrics ---------- */
    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-top: 4px solid var(--primary);
        padding: 17px;
        border-radius: 13px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.10);
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] * {
        color: var(--muted) !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
        color: var(--primary-dark) !important;
    }

    /* ---------- Tabs ---------- */
    div[data-testid="stTabs"] button,
    div[data-testid="stTabs"] button * {
        color: #4a5f80 !important;
        font-weight: 600;
    }

    div[data-testid="stTabs"] button[aria-selected="true"],
    div[data-testid="stTabs"] button[aria-selected="true"] * {
        color: var(--primary) !important;
    }

    /* ---------- File uploader ---------- */
    div[data-testid="stFileUploader"] {
        background: var(--surface);
        border: 2px dashed #60a5fa;
        border-radius: 12px;
        padding: 12px;
    }

    div[data-testid="stFileUploader"] section {
        background: #f0f7ff;
        border-radius: 10px;
    }

    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] span {
        color: var(--muted) !important;
    }

    /* ---------- Buttons ---------- */
    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(90deg, #2563eb, #0ea5e9);
        color: #ffffff !important;
        border: none;
        border-radius: 9px;
        font-weight: 600;
        padding: 9px 18px;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(90deg, #1d4ed8, #0284c7);
        color: #ffffff !important;
        border: none;
    }

    .stButton > button p,
    .stDownloadButton > button p {
        color: #ffffff !important;
    }

    /* ---------- Inputs, expanders, tables ---------- */
    textarea {
        background-color: #ffffff !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
    }

    div[data-testid="stExpander"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 10px;
        overflow: hidden;
        background: var(--surface);
    }

    hr {
        border-color: var(--border);
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# INITIALIZATION
# --------------------------------------------------

initialize_database()

if "inspection_result" not in st.session_state:
    st.session_state.inspection_result = None

if "ai_report" not in st.session_state:
    st.session_state.ai_report = None

if "quantity_results" not in st.session_state:
    st.session_state.quantity_results = None


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def save_upload(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()

    with tempfile.NamedTemporaryFile(
        suffix=suffix,
        delete=False,
    ) as temp:
        temp.write(uploaded_file.getvalue())
        return Path(temp.name)


def status_label(status):
    if status == "MATCHED":
        return "🟢 MATCHED"
    if status == "SHORTAGE":
        return "🔴 SHORTAGE"
    if status == "EXCESS":
        return "🟠 EXCESS"
    return status


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 📦 WarehouseIQ")
    st.caption("AI Receiving & Inspection Platform")
    st.divider()

    st.markdown("### Navigation")
    st.markdown("""
    **🔍 Image Inspection**

    **📄 Document Intelligence**

    **⚖️ Quantity Verification**

    **📊 Inspection History**
    """)

    st.divider()

    st.markdown("### Technology")
    st.caption("YOLO26 · PaddleOCR")
    st.caption("Qwen · Ollama")
    st.caption("FastAPI · SQLite · Streamlit")

    st.divider()
    st.caption("WarehouseIQ | Prototype v1.0")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>📦 Warehouse Receiving Copilot</h1>
    <p>
        Intelligent receiving, document extraction, quantity reconciliation
        and AI-assisted warehouse inspection.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# TOP-LEVEL METRICS
# --------------------------------------------------

try:
    history_data = get_inspections(limit=50)
    total_inspections = len(history_data) if history_data else 0
except Exception:
    history_data = []
    total_inspections = 0

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("Total Inspections", total_inspections)

with m2:
    st.metric("AI Engine", "Qwen", "Remote Ollama")

with m3:
    st.metric("Vision Engine", "YOLO26", "Local inference")

st.divider()


# --------------------------------------------------
# MAIN TABS
# --------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Image Inspection",
    "📄 Document Intelligence",
    "⚖️ Quantity Verification",
    "📊 Inspection History",
])


# ==================================================
# TAB 1: IMAGE INSPECTION
# ==================================================

with tab1:
    st.markdown(
        '<div class="section-heading">Visual Goods Inspection</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Upload a warehouse image to detect visible objects "
        "and extract printed text."
    )

    image_file = st.file_uploader(
        "Choose an inspection image",
        type=["jpg", "jpeg", "png"],
        key="inspection_image",
    )

    if image_file:
        left, right = st.columns([1, 1])

        with left:
            st.image(
                image_file,
                caption="Uploaded inspection image",
                use_container_width=True,
            )

        with right:
            st.markdown("#### Inspection Controls")
            st.write("Run local object detection and OCR.")

            if st.button(
                "🚀 Run Image Inspection",
                key="run_inspection",
                use_container_width=True,
            ):
                image_path = save_upload(image_file)

                try:
                    with st.spinner(
                        "Running YOLO26 and PaddleOCR..."
                    ):
                        engine = WarehouseInspectionEngine()
                        result = engine.inspect(image_path)

                    result["image"] = image_file.name
                    inspection_id = save_inspection(result)
                    result["inspection_id"] = inspection_id

                    st.session_state.inspection_result = result
                    st.session_state.ai_report = None

                    st.success(
                        f"Inspection completed · ID {inspection_id}"
                    )

                except Exception as error:
                    st.error(f"Inspection failed: {error}")

                finally:
                    image_path.unlink(missing_ok=True)

    result = st.session_state.inspection_result

    if result:
        st.divider()
        st.markdown("#### Inspection Results")

        col1, col2, col3 = st.columns(3)

        detections = result.get("detections", [])
        ocr_data = result.get("ocr", [])

        col1.metric("Detected Objects", len(detections))
        col2.metric("OCR Text Regions", len(ocr_data))
        col3.metric(
            "Inspection ID",
            result.get("inspection_id", "N/A"),
        )

        with st.expander("View Full Inspection Data"):
            st.json(result)

        if st.button(
            "🤖 Generate AI Inspection Report",
            key="generate_ai",
        ):
            try:
                with st.spinner("Qwen is analyzing inspection evidence..."):
                    report = analyze_inspection(result)

                st.session_state.ai_report = report
                save_inspection(result, report)

            except Exception as error:
                st.error(f"AI analysis failed: {error}")

        if st.session_state.ai_report:
            st.markdown("#### AI Inspection Report")
            st.json(st.session_state.ai_report)


# ==================================================
# TAB 2: DOCUMENT INTELLIGENCE
# ==================================================

with tab2:
    st.markdown(
        '<div class="section-heading">Document Intelligence</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Extract text from purchase orders, invoices and delivery notes."
    )

    document = st.file_uploader(
        "Upload a PDF or TXT document",
        type=["pdf", "txt"],
        key="document_upload",
    )

    if document:
        st.info(f"Selected document: **{document.name}**")

        if st.button(
            "📄 Extract Document Information",
            key="extract_document",
        ):
            document_path = save_upload(document)

            try:
                with st.spinner("Extracting document text..."):
                    extracted_text = extract_document_text(
                        document_path
                    )

                st.session_state.extracted_document_text = extracted_text
                st.success("Document extraction completed.")

            except Exception as error:
                st.error(f"Document extraction failed: {error}")

            finally:
                document_path.unlink(missing_ok=True)

    if st.session_state.get("extracted_document_text"):
        st.markdown("#### Extracted Content")

        st.text_area(
            "Document text",
            st.session_state.extracted_document_text,
            height=300,
        )


# ==================================================
# TAB 3: QUANTITY VERIFICATION
# ==================================================

with tab3:
    st.markdown(
        '<div class="section-heading">Quantity Reconciliation</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Compare purchase order quantities against received quantities."
    )

    st.info(
        "Supported item format: "
        "`1. Cardboard Boxes - Quantity: 100`"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📋 Purchase Order")
        ordered_file = st.file_uploader(
            "Upload ordered quantities",
            type=["pdf", "txt"],
            key="ordered_document",
        )

    with col2:
        st.markdown("#### 📦 Received Delivery Note")
        received_file = st.file_uploader(
            "Upload received quantities",
            type=["pdf", "txt"],
            key="received_document",
        )

    if st.button(
        "⚖️ Compare Quantities",
        key="compare_quantities",
        use_container_width=True,
    ):
        if not ordered_file or not received_file:
            st.warning("Upload both documents before comparing.")
        else:
            ordered_path = save_upload(ordered_file)
            received_path = save_upload(received_file)

            try:
                with st.spinner("Reconciling item quantities..."):
                    ordered_text = extract_document_text(ordered_path)
                    received_text = extract_document_text(received_path)

                    results = compare_quantities(
                        ordered_text,
                        received_text,
                    )

                st.session_state.quantity_results = results

                if not results:
                    st.warning(
                        "No item quantities found. "
                        "Please check the document format."
                    )

            except Exception as error:
                st.error(f"Comparison failed: {error}")

            finally:
                ordered_path.unlink(missing_ok=True)
                received_path.unlink(missing_ok=True)

    results = st.session_state.quantity_results

    if results:
        st.divider()
        st.markdown("#### Reconciliation Summary")

        matched = sum(
            item["status"] == "MATCHED" for item in results
        )
        shortage = sum(
            item["status"] == "SHORTAGE" for item in results
        )
        excess = sum(
            item["status"] == "EXCESS" for item in results
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("🟢 Matched", matched)
        c2.metric("🔴 Shortages", shortage)
        c3.metric("🟠 Excess", excess)

        display_results = [
            {
                "Item": item["item"].title(),
                "Ordered": item["ordered_quantity"],
                "Received": item["received_quantity"],
                "Difference": item["difference"],
                "Status": status_label(item["status"]),
            }
            for item in results
        ]

        st.dataframe(
            pd.DataFrame(display_results),
            use_container_width=True,
            hide_index=True,
        )

        if shortage:
            st.error(
                f"{shortage} item(s) have shortages. "
                "Manual verification is required."
            )
        elif excess:
            st.warning(
                f"{excess} item(s) have excess quantities. "
                "Please verify the delivery."
            )
        else:
            st.success("All quantities match the purchase order.")

        st.download_button(
            "⬇️ Download Reconciliation Report",
            data=json.dumps(results, indent=4),
            file_name="warehouse_reconciliation.json",
            mime="application/json",
            use_container_width=True,
        )


# ==================================================
# TAB 4: INSPECTION HISTORY
# ==================================================

with tab4:
    st.markdown(
        '<div class="section-heading">Inspection History</div>',
        unsafe_allow_html=True,
    )

    st.caption("Review previously saved warehouse inspections.")

    if st.button("🔄 Refresh History"):
        st.rerun()

    try:
        history = get_inspections(limit=50)

        if history:
            st.dataframe(
                pd.DataFrame(history),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No inspection records available yet.")

    except Exception as error:
        st.error(f"Unable to load inspection history: {error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "WarehouseIQ · AI-assisted warehouse receiving and inspection · "
    "Prototype — human verification required for operational decisions."
)