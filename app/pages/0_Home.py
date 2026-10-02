import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st

st.markdown("""
<div class="lex-hero">
    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span class="lex-badge lex-badge-sky">Local-First</span>
        <span class="lex-badge lex-badge-indigo">Air-Gapped RAG</span>
        <span class="lex-badge lex-badge-emerald">Phase A Active</span>
    </div>
    <div style="font-size: 2.1rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.025em; line-height: 1.2;">
        LexLocal Legal Intelligence Core
    </div>
    <div style="color: #94a3b8; font-size: 1rem; margin-top: 0.65rem; max-width: 780px; line-height: 1.6;">
        Deterministic, privacy-preserving retrieval engine tailored for high-stakes legal contracts, policies, and statutory frameworks. Recovers document tree hierarchies and cross-references with zero external network dependencies.
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.6, 1])

with col1:
    st.markdown("""
    <div class="lex-card">
        <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 0.85rem;">
            Core Architectural Capabilities
        </div>
        <div style="display: grid; gap: 0.85rem;">
            <div style="background: rgba(15, 23, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 0.85rem 1rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;">
                    <div style="font-weight: 600; color: #e2e8f0; font-size: 0.92rem;">Local & Air-Gapped Execution</div>
                    <span class="lex-badge lex-badge-emerald">Confidential</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.84rem; line-height: 1.5;">
                    Documents are parsed, indexed, and embedded entirely on local hardware. No telemetry, no API tokens, and zero outbound network calls.
                </div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 0.85rem 1rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;">
                    <div style="font-weight: 600; color: #e2e8f0; font-size: 0.92rem;">Hierarchical Structural Trees</div>
                    <span class="lex-badge lex-badge-indigo">Context-Aware</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.84rem; line-height: 1.5;">
                    Recovers exact legal structure (Act -> Chapter -> Section -> Subsection -> Clause). Retrieved clauses include full parent breadcrumbs and cross-reference graphs.
                </div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.45); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 0.85rem 1rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.25rem;">
                    <div style="font-weight: 600; color: #e2e8f0; font-size: 0.92rem;">Hybrid Fusion Search</div>
                    <span class="lex-badge lex-badge-sky">RRF Fusion</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.84rem; line-height: 1.5;">
                    Combines dense semantic vector retrieval (LanceDB + FastEmbed) with sparse exact keyword matching (BM25) via Reciprocal Rank Fusion.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("**Workflow Guide**: Upload statutory texts or contracts under **Ingest**, query clauses with parent breadcrumbs on **Ask**, and visually navigate the tree under **Inspect**.")

with col2:
    st.markdown("""
    <div class="lex-card">
        <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 0.85rem;">
            System Specifications
        </div>
        <div style="display: grid; gap: 0.6rem; font-size: 0.85rem;">
            <div style="display: flex; justify-content: space-between; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                <span style="color: #94a3b8;">Embedding Engine:</span>
                <span style="color: #f1f5f9; font-weight: 600; font-family: 'JetBrains Mono', monospace;">bge-small-en-v1.5</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                <span style="color: #94a3b8;">Vector Storage:</span>
                <span style="color: #f1f5f9; font-weight: 600; font-family: 'JetBrains Mono', monospace;">LanceDB Embedded</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                <span style="color: #94a3b8;">Keyword Index:</span>
                <span style="color: #f1f5f9; font-weight: 600; font-family: 'JetBrains Mono', monospace;">Rank-BM25</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #94a3b8;">Compute Tier:</span>
                <span style="color: #6ee7b7; font-weight: 600; font-family: 'JetBrains Mono', monospace;">CPU-Only / Local</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if os.path.exists("app/assets/law.jpg"):
        st.markdown('<div style="border-radius: 10px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 0.75rem;">', unsafe_allow_html=True)
        st.image("app/assets/law.jpg", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    if os.path.exists("app/assets/policy.jpg"):
        st.markdown('<div style="border-radius: 10px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.08);">', unsafe_allow_html=True)
        st.image("app/assets/policy.jpg", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
