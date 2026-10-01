import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.retrieval.hybrid import hybrid_search, search_dense
from src.retrieval.context_assembler import assemble_context
from src.retrieval.context_assembler import assemble_context
from src.retrieval.prompt_builder import build_prompt
from src.indexing.vector_store import get_db
from src.audit.logger import log_event
from src.config import settings
from src.storage.trees import load_tree
import pandas as pd
import base64

st.title("Ask a Question")

trees_dir = os.path.join(settings.paths.data_dir, "trees")
available_docs = []
if os.path.exists(trees_dir):
    available_docs = [f.replace('.json', '') for f in os.listdir(trees_dir) if f.endswith('.json')]

col_main, col_right = st.columns([2, 1])

with col_right:
    st.subheader("Document Pool")
    if not available_docs:
        st.info("No documents available.")
        selected_docs = None
    else:
        selected_docs = st.multiselect("Filter search by documents (leave empty to search all):", available_docs)

with col_main:
    query = st.text_input("Enter your query:")
    mode = st.radio("Retrieval Mode", options=["Hierarchical", "Naive"])
    top_k = st.slider("Top K Hits", min_value=1, max_value=20, value=5)

    if st.button("Search"):
        if query:
            with st.spinner("Searching..."):
                doc_filter = selected_docs if selected_docs else None
                
                if mode == "Hierarchical":
                    hits = hybrid_search(query, doc_ids=doc_filter)[:top_k]
                    if hits:
                        st.write(f"Found {len(hits)} hits.")
                        bundle = assemble_context(query, hits, mode="hierarchical")
                        prompt = build_prompt(bundle)
                        
                        st.subheader("Results")
                        for item in bundle.items:
                            st.markdown(f"**Citation**: `{item.citation_str}`")
                            
                            breadcrumb = ""
                            if item.parent_chain:
                                path_parts = [p.heading or p.label for p in item.parent_chain]
                                breadcrumb = " > ".join(filter(None, path_parts))
                                st.markdown(f"**Path**: {breadcrumb}")
                                
                            st.markdown(f"> {item.clause.text}")
                            st.divider()
                            
                        with st.expander("Prompt that would be sent to the LLM"):
                            st.text(prompt)
                            
                        log_event("query", {"query": query, "mode": mode, "hits": len(hits)})
                    else:
                        st.warning("No results found.")
                else:
                    # Naive mode
                    hits = search_dense(query, doc_ids=doc_filter, table_name="naive_chunks")[:top_k]
                    if hits:
                        db = get_db()
                        table = db.open_table("naive_chunks")
                        df = table.to_pandas()
                        
                        st.write(f"Found {len(hits)} naive chunk hits.")
                        for hit in hits:
                            chunk_row = df[df["chunk_id"] == hit.node_id].iloc[0]
                            st.markdown(f"**Document**: `{chunk_row['doc_id']}` (Page {chunk_row['page_start']})")
                            st.markdown(f"> {chunk_row['text']}")
                            st.divider()
                            
                        log_event("query", {"query": query, "mode": mode, "hits": len(hits)})
                    else:
                        st.warning("No results found in naive_chunks. Did you ingest with naive chunker?")

