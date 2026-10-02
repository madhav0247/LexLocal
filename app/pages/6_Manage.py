import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config import settings
from src.indexing.vector_store import get_db
from src.indexing.bm25_index import build_bm25, get_bm25_path
from src.storage.trees import load_tree
from src.audit.logger import log_event

st.markdown("""
<div class="lex-hero">
    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span class="lex-badge lex-badge-indigo">Administration</span>
        <span class="lex-badge lex-badge-emerald">Document Lifecycle</span>
    </div>
    <div style="font-size: 1.85rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.02em;">
        Manage Document Repository
    </div>
    <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem; max-width: 760px; line-height: 1.5;">
        Audit, inspect, and safely remove indexed documents from vector tables, structural tree stores, and inverted token indexes.
    </div>
</div>
""", unsafe_allow_html=True)

trees_dir = os.path.join(settings.paths.data_dir, "trees")
if not os.path.exists(trees_dir):
    st.info("No documents have been ingested yet.")
    st.stop()

files = [f for f in os.listdir(trees_dir) if f.endswith('.json')]
if not files:
    st.info("No documents currently stored in the system.")
    st.stop()

doc_ids = [f.replace(".json", "") for f in files]

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
    <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif;">
        Active Ingested Documents
    </div>
    <span class="lex-badge lex-badge-emerald">{len(doc_ids)} Registered</span>
</div>
""", unsafe_allow_html=True)

for doc_id in doc_ids:
    with st.expander(f"Document: {doc_id}"):
        col1, col2 = st.columns([3, 1])
        with col1:
            try:
                nodes = load_tree(doc_id)
                roots = [n.heading or n.label for n in nodes if n.level == 0]
                root_preview = ", ".join(roots[:3]) + ("..." if len(roots) > 3 else "")
                
                st.markdown(f"""
                <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 0.5rem;">
                    <span class="lex-badge lex-badge-indigo">{doc_id}</span>
                    <span class="lex-badge lex-badge-sky">{len(nodes)} Clauses</span>
                </div>
                <div style="font-size: 0.84rem; color: #94a3b8; margin-top: 0.25rem;">
                    <strong>Root Elements:</strong> {root_preview if root_preview else 'None'}
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"<div style='color: #f87171;'>Error loading tree: {e}</div>", unsafe_allow_html=True)
                
        with col2:
            if st.button("Delete Document", key=f"del_{doc_id}", use_container_width=True):
                with st.spinner("Purging vectors, tree, and rebuilding BM25 index..."):
                    db = get_db()
                    if "clauses" in db.table_names():
                        table = db.open_table("clauses")
                        table.delete(f"doc_id = '{doc_id}'")
                        
                    if "naive_chunks" in db.table_names():
                        n_table = db.open_table("naive_chunks")
                        n_table.delete(f"doc_id = '{doc_id}'")
                        
                    tree_path = os.path.join(trees_dir, f"{doc_id}.json")
                    if os.path.exists(tree_path):
                        os.remove(tree_path)
                        
                    remaining = [f.replace(".json", "") for f in os.listdir(trees_dir) if f.endswith('.json')]
                    all_remaining_nodes = []
                    for r_doc in remaining:
                        all_remaining_nodes.extend(load_tree(r_doc))
                    
                    if all_remaining_nodes:
                        build_bm25(all_remaining_nodes)
                    else:
                        bm25_path = get_bm25_path()
                        if os.path.exists(bm25_path):
                            os.remove(bm25_path)
                            
                    log_event("delete", {"doc_id": doc_id})
                    st.success(f"Purged document '{doc_id}'.")
                    st.rerun()

st.markdown("""
<div class="lex-card" style="margin-top: 1.5rem;">
    <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 0.5rem;">
        Updating Existing Documents
    </div>
    <div style="color: #94a3b8; font-size: 0.88rem; line-height: 1.5;">
        To overwrite or re-index a document with a newer revision, simply navigate to the <strong>Ingest</strong> page and upload the file with the same <strong>Document Identifier</strong>. The pipeline will automatically overwrite existing vector embeddings and rebuild the structural tree.
    </div>
</div>
""", unsafe_allow_html=True)
