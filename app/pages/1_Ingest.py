import streamlit as st
import tempfile
import os
import sys

# Ensure src is accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ingest.loader import load_document
from src.hierarchy.builder import build_tree
from src.hierarchy.metadata import encode_metadata
from src.hierarchy.xref import detect_xrefs, resolve_xrefs
from src.storage.trees import save_tree, load_tree
from src.indexing.vector_store import ingest_clauses
from src.indexing.bm25_index import build_bm25
from src.baseline.naive_chunker import generate_naive_chunks, ingest_naive_chunks
from src.audit.logger import log_event
from src.config import settings

st.title("Ingest Document")

uploaded_file = st.file_uploader("Upload a PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    doc_id = st.text_input("Document ID", value=os.path.splitext(uploaded_file.name)[0])
    title = st.text_input("Document Title", value=uploaded_file.name)
    
    if st.button("Process Document"):
        with st.spinner("Processing..."):
            raw_dir = os.path.join(settings.paths.data_dir, "raw")
            os.makedirs(raw_dir, exist_ok=True)
            ext = uploaded_file.name.split('.')[-1]
            tmp_path = os.path.join(raw_dir, f"{doc_id}.{ext}")
            with open(tmp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
                
            try:
                st.write("Extracting text...")
                lines = load_document(tmp_path)
                
                st.write("Building hierarchy...")
                nodes = build_tree(doc_id, title, lines)
                
                st.write("Extracting metadata & xrefs...")
                encode_metadata(tmp_path, nodes)
                detect_xrefs(nodes)
                resolve_xrefs(nodes)
                
                st.write("Saving tree...")
                save_tree(doc_id, nodes)
                
                st.write("Embedding & Indexing (LanceDB)...")
                ingest_clauses(nodes)
                
                st.write("Building Global BM25 Index...")
                all_nodes = []
                trees_dir = os.path.join(settings.paths.data_dir, "trees")
                if os.path.exists(trees_dir):
                    for f in os.listdir(trees_dir):
                        if f.endswith('.json'):
                            all_nodes.extend(load_tree(f.replace(".json", "")))
                if all_nodes:
                    build_bm25(all_nodes)
                else:
                    build_bm25(nodes)
                
                st.write("Building Naive Baseline Chunks...")
                naive_chunks = generate_naive_chunks(doc_id, lines)
                ingest_naive_chunks(naive_chunks)
                
                log_event("ingest", {"doc_id": doc_id, "title": title, "nodes_count": len(nodes)})
                
                st.success(f"Successfully processed '{title}' ({len(nodes)} clauses).")
            except Exception as e:
                st.error(f"Error during ingestion: {e}")
            finally:
                os.remove(tmp_path)
