import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.retrieval.hybrid import hybrid_search, search_dense
from src.retrieval.context_assembler import assemble_context
from src.retrieval.prompt_builder import build_prompt
from src.indexing.vector_store import get_db
from src.audit.logger import log_event
from src.config import settings
from src.storage.trees import load_tree
import pandas as pd

st.markdown("""
<div class="lex-hero">
    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span class="lex-badge lex-badge-indigo">Research Console</span>
        <span class="lex-badge lex-badge-sky">Hybrid Retrieval</span>
    </div>
    <div style="font-size: 1.85rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.02em;">
        Ask & Retrieve Legal Context
    </div>
    <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem; max-width: 760px; line-height: 1.5;">
        Query across ingested statutes, policies, and contracts. LexLocal fuses dense embeddings with keyword matching and reconstructs full parent hierarchy chains and citations.
    </div>
</div>
""", unsafe_allow_html=True)

trees_dir = os.path.join(settings.paths.data_dir, "trees")
available_docs = []
if os.path.exists(trees_dir):
    available_docs = [f.replace('.json', '') for f in os.listdir(trees_dir) if f.endswith('.json')]

col_main, col_right = st.columns([1.8, 1])

with col_right:
    st.markdown("""
    <div class="lex-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div style="font-size: 1.02rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif;">
                Document Pool
            </div>
            <span class="lex-badge lex-badge-emerald">""" + f"{len(available_docs)} Active" + """</span>
        </div>
        <div style="font-size: 0.82rem; color: #94a3b8; margin-bottom: 0.85rem; line-height: 1.4;">
            Filter your search scope to specific instruments, or search across all indexed documents simultaneously.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not available_docs:
        st.info("No documents indexed yet. Ingest documents to populate the pool.")
        selected_docs = None
    else:
        selected_docs = st.multiselect(
            "Filter search by documents (leave empty for all):",
            available_docs,
            placeholder="Select documents..."
        )

with col_main:
    st.markdown('<div class="lex-card">', unsafe_allow_html=True)
    query = st.text_input(
        "Search Query",
        placeholder="e.g. What are the requirements for data fiduciary under Section 8 or termination grounds?"
    )
    
    c1, c2 = st.columns([1.2, 1])
    with c1:
        mode = st.radio("Retrieval Mode", options=["Hierarchical", "Naive"], horizontal=True)
    with c2:
        top_k = st.slider("Top Results (K)", min_value=1, max_value=20, value=5)
        
    search_clicked = st.button("Execute Retrieval", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if search_clicked:
        if query:
            with st.spinner("Executing hybrid fusion search across legal corpus..."):
                doc_filter = selected_docs if selected_docs else None
                
                if mode == "Hierarchical":
                    hits = hybrid_search(query, doc_ids=doc_filter)[:top_k]
                    if hits:
                        bundle = assemble_context(query, hits, mode="hierarchical")
                        prompt = build_prompt(bundle)
                        
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin: 1.5rem 0 1rem 0;">
                            <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif;">
                                Retrieved Context & Structural Hierarchy
                            </div>
                            <span class="lex-badge lex-badge-sky">{len(hits)} Hits Recovered</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for idx, item in enumerate(bundle.items, 1):
                            st.markdown(f"""
                            <div class="lex-card" style="margin-bottom: 1.25rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 0.5rem;">
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <span class="lex-badge lex-badge-indigo">#{idx}</span>
                                        <span class="lex-badge lex-badge-slate">{item.citation_str}</span>
                                    </div>
                                    <span class="lex-badge lex-badge-emerald">Clause Level {item.clause.level}</span>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            if item.parent_chain:
                                path_parts = [p.heading or p.label for p in item.parent_chain]
                                clean_parts = list(filter(None, path_parts))
                                breadcrumb = " &rarr; ".join(clean_parts)
                                st.markdown(f"""
                                <div class="lex-breadcrumb-bar">
                                    <span style="color: #64748b;">Hierarchy:</span> {breadcrumb}
                                </div>
                                """, unsafe_allow_html=True)
                                
                            st.markdown(f"""
                            <div class="lex-result-box">
                                {item.clause.text}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        with st.expander("Inspect Assembled LLM Context Bundle (Phase A Hook)"):
                            st.code(prompt, language="markdown")
                            
                        log_event("query", {"query": query, "mode": mode, "hits": len(hits)})
                    else:
                        st.warning("No matching clauses found for the given query.")
                else:
                    # Naive mode
                    hits = search_dense(query, doc_ids=doc_filter, table_name="naive_chunks")[:top_k]
                    if hits:
                        db = get_db()
                        table = db.open_table("naive_chunks")
                        df = table.to_pandas()
                        
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin: 1.5rem 0 1rem 0;">
                            <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif;">
                                Naive Chunk Results (Baseline)
                            </div>
                            <span class="lex-badge lex-badge-slate">{len(hits)} Chunks</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        for idx, hit in enumerate(hits, 1):
                            chunk_row = df[df["chunk_id"] == hit.node_id].iloc[0]
                            st.markdown(f"""
                            <div class="lex-card" style="margin-bottom: 1.25rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <span class="lex-badge lex-badge-slate">#{idx}</span>
                                        <span class="lex-badge lex-badge-indigo">{chunk_row['doc_id']}</span>
                                    </div>
                                    <span class="lex-badge lex-badge-sky">Page {chunk_row['page_start']}</span>
                                </div>
                                <div class="lex-result-box">
                                    {chunk_row['text']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        log_event("query", {"query": query, "mode": mode, "hits": len(hits)})
                    else:
                        st.warning("No results found in naive_chunks table.")
