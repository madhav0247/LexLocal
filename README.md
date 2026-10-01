# LexLocal

LexLocal is a local-first, privacy-preserving Retrieval-Augmented Generation (RAG) system for large legal documents (contracts, agreements, policies, statutes). 

## Features
- Ingests PDF, DOCX, and TXT files locally.
- Recovers the legal structure (Act -> Chapter -> Section) to build a clause tree.
- Hybrid Retrieval using BM25 and dense vectors (LanceDB + FastEmbed) with Reciprocal Rank Fusion (RRF).
- Complete offline capability, keeping all data securely on your local machine.

## Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the UI
```bash
streamlit run app/main.py
```

### 3. Usage
- **Ingest:** Upload your documents in the Ingest page.
- **Ask:** Ask questions and receive citations and hierarchical context.
- **Inspect:** View the raw document tree in the Inspect page.
- **Benchmark:** Compare Hierarchical retrieval against Naive Chunking.

## Known Limitations
- Scanned PDFs require OCR, which is not yet enabled in this phase.
- DOCX files do not natively supply reliable page numbers, so citations default to line/paragraph numbers.
- Parent summaries are currently extractive until an LLM backend is integrated.
- Cross-references resolve only within the boundaries of a single document.
