import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config import settings
from src.indexing.vector_store import get_db
from src.indexing.bm25_index import build_bm25, get_bm25_path
from src.storage.trees import load_tree
from src.audit.logger import log_event

st.title("Manage Documents (Admin)")
st.markdown("Create, Read, Update, and Delete documents from the system.")

trees_dir = os.path.join(settings.paths.data_dir, "trees")
if not os.path.exists(trees_dir):
    st.info("No documents have been ingested yet.")
    st.stop()

# READ
files = [f for f in os.listdir(trees_dir) if f.endswith('.json')]
if not files:
    st.info("No documents currently in the system.")
    st.stop()

st.subheader("Ingested Documents")
doc_ids = [f.replace(".json", "") for f in files]

for doc_id in doc_ids:
    with st.expander(f"Document: {doc_id}"):
        col1, col2 = st.columns([3, 1])
        with col1:
            try:
                nodes = load_tree(doc_id)
                st.write(f"**Total Clauses:** {len(nodes)}")
                roots = [n.heading or n.label for n in nodes if n.level == 0]
                st.write(f"**Root Elements:** {roots[:3]}..." if len(roots) > 3 else f"**Root Elements:** {roots}")
            except Exception as e:
                st.write("**Total Clauses:** Error loading")
                
        with col2:
            if st.button("Delete Document", key=f"del_{doc_id}"):
                with st.spinner("Deleting..."):
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
                    st.success(f"Deleted {doc_id}")
                    st.rerun()

st.divider()
st.subheader("Update / Re-ingest")
st.markdown("To **Update** a document, simply go to the **Ingest** page and upload it again with the same Document ID. The system will automatically overwrite the old vectors and rebuild the tree.")
