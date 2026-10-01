import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st

st.title("LexLocal: Local-First Legal RAG")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    Welcome to **LexLocal**, a privacy-preserving retrieval engine tailored for complex legal documents.
    
    ### How it Works
    - **Local Processing**: No data ever leaves your machine. Your documents are parsed and embedded locally.
    - **Hierarchical Context**: When you ask a question, LexLocal doesn't just retrieve isolated chunks of text. It understands the structure of your documents (Acts, Chapters, Sections) and provides the full parent chain and cross-references.
    - **Hybrid Retrieval**: We use a combination of semantic dense search (LanceDB) and keyword search (BM25) fused together to ensure the highest accuracy for legal queries.
    
    Get started by uploading your legal contracts, policies, or statutes in the **Ingest** page!
    """)
    st.info("**Phase A**: Full semantic parsing, hierarchical trees, and hybrid retrieval. LLM Generation is currently disabled.")

with col2:
    if os.path.exists("app/assets/law.jpg"):
        st.image("app/assets/law.jpg", use_container_width=True)
    if os.path.exists("app/assets/policy.jpg"):
        st.image("app/assets/policy.jpg", use_container_width=True)
