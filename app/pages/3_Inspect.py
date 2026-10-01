import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.storage.trees import load_tree
from src.config import settings

st.title("Inspect Document Hierarchy")

data_dir = settings.paths.data_dir
trees_dir = os.path.join(data_dir, "trees")

if not os.path.exists(trees_dir):
    st.warning("No documents ingested yet.")
else:
    docs = [f.split(".")[0] for f in os.listdir(trees_dir) if f.endswith(".json")]
    if not docs:
        st.warning("No documents found in trees folder.")
    else:
        selected_doc = st.selectbox("Select a document", docs)
        
        if selected_doc:
            nodes = load_tree(selected_doc)
            
            def render_node(node_id, depth=0):
                node = next((n for n in nodes if n.node_id == node_id), None)
                if not node:
                    return
                    
                label = f"{node.node_type.name.capitalize()} {node.label} {node.heading or ''}".strip()
                if not label:
                    label = "Unlabeled Node"
                    
                with st.expander(label):
                    st.write(node.text)
                    st.markdown(f"**Node ID:** `{node.node_id}` | **Level:** {node.level} | **Page:** {node.page_start}")
                    if node.xrefs_raw:
                        st.markdown("**Cross References:**")
                        st.write(node.xrefs_raw)
                        st.write("Resolved to:", node.xrefs_resolved)
                
                # Render children
                for child_id in node.children_ids:
                    render_node(child_id, depth + 1)
                    
            root_node = next((n for n in nodes if n.level == 0), None)
            if root_node:
                render_node(root_node.node_id)
            else:
                st.error("No root node found.")
