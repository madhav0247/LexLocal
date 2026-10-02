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

st.markdown("""
<div class="lex-hero">
    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span class="lex-badge lex-badge-indigo">Ingestion Engine</span>
        <span class="lex-badge lex-badge-sky">Hierarchical Parser</span>
    </div>
    <div style="font-size: 1.85rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.02em;">
        Document Ingestion & Pipeline
    </div>
    <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem; max-width: 720px; line-height: 1.5;">
        Upload legal instruments to automatically extract font hierarchies, construct clause tree graphs, extract cross-references, and index into LanceDB and BM25.
    </div>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown("""
    <div class="lex-card">
        <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 0.85rem;">
            Upload Legal Document
        </div>
        <div style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">
            Supported formats: PDF (with font bounding boxes), DOCX (structured paragraphs), and plain TXT.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Select document to process", type=["pdf", "docx", "txt"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        default_id = os.path.splitext(uploaded_file.name)[0].lower().replace(" ", "_")
        
        st.markdown('<div class="lex-card" style="margin-top: 1rem;">', unsafe_allow_html=True)
        col_id, col_t = st.columns(2)
        with col_id:
            doc_id = st.text_input("Document Identifier", value=default_id)
        with col_t:
            title = st.text_input("Document Display Title", value=uploaded_file.name)
            
        process_btn = st.button("Start Ingestion Pipeline", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if process_btn:
            with st.spinner("Processing document through legal hierarchy pipeline..."):
                raw_dir = os.path.join(settings.paths.data_dir, "raw")
                os.makedirs(raw_dir, exist_ok=True)
                ext = uploaded_file.name.split('.')[-1]
                saved_path = os.path.join(raw_dir, f"{doc_id}.{ext}")
                with open(saved_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                    
                try:
                    status_container = st.container()
                    with status_container:
                        st.markdown('<div class="lex-card">', unsafe_allow_html=True)
                        st.markdown("**1. Text & Layout Extraction**...")
                        lines = load_document(saved_path)
                        
                        st.markdown("**2. Constructing Structural Hierarchy Tree**...")
                        nodes = build_tree(doc_id, title, lines)
                        
                        st.markdown("**3. Metadata Encoding & Cross-Reference Resolution**...")
                        encode_metadata(saved_path, nodes)
                        detect_xrefs(nodes)
                        resolve_xrefs(nodes)
                        
                        st.markdown("**4. Persisting Tree Graph**...")
                        save_tree(doc_id, nodes)
                        
                        st.markdown("**5. Dense Vector Embedding (FastEmbed -> LanceDB)**...")
                        ingest_clauses(nodes)
                        
                        st.markdown("**6. Compiling Global BM25 Inverted Index**...")
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
                        
                        st.markdown("**7. Generating Naive Baseline Chunks**...")
                        naive_chunks = generate_naive_chunks(doc_id, lines)
                        ingest_naive_chunks(naive_chunks)
                        
                        log_event("ingest", {"doc_id": doc_id, "title": title, "nodes_count": len(nodes)})
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    st.success(f"Document '{title}' successfully indexed into LanceDB and BM25 ({len(nodes)} clauses recovered).")
                except Exception as e:
                    st.error(f"Error during ingestion pipeline: {e}")

with col_right:
    st.markdown("""
    <div class="lex-card">
        <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 0.85rem;">
            Pipeline Architecture
        </div>
        <div style="display: grid; gap: 0.75rem; font-size: 0.83rem;">
            <div style="padding: 0.6rem 0.8rem; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px;">
                <div style="font-weight: 600; color: #a5b4fc; font-size: 0.85rem;">Stage 1: Structural Parser</div>
                <div style="color: #94a3b8; font-size: 0.78rem; margin-top: 0.2rem;">Recovers Acts, Chapters, Sections, Subsections, and Clauses with exact typography and bbox positioning.</div>
            </div>
            <div style="padding: 0.6rem 0.8rem; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px;">
                <div style="font-weight: 600; color: #7dd3fc; font-size: 0.85rem;">Stage 2: Cross-Reference Graph</div>
                <div style="color: #94a3b8; font-size: 0.78rem; margin-top: 0.2rem;">Resolves internal clause references (e.g., 'pursuant to section 4(2)') into exact node target links.</div>
            </div>
            <div style="padding: 0.6rem 0.8rem; background: rgba(15, 23, 42, 0.5); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px;">
                <div style="font-weight: 600; color: #6ee7b7; font-size: 0.85rem;">Stage 3: Hybrid Indexes</div>
                <div style="color: #94a3b8; font-size: 0.78rem; margin-top: 0.2rem;">Dense 384-dim embeddings saved to LanceDB table 'clauses' + global BM25 token index.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
