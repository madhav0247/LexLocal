import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.storage.trees import load_tree
from src.config import settings

st.markdown("""
<div class="lex-hero">
    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span class="lex-badge lex-badge-indigo">Hierarchy Visualizer</span>
        <span class="lex-badge lex-badge-sky">Legal AST</span>
    </div>
    <div style="font-size: 1.85rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.02em;">
        Inspect Document Hierarchy
    </div>
    <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem; max-width: 760px; line-height: 1.5;">
        Explore the recovered hierarchical abstract syntax tree for any ingested document. Trace nodes from Root Acts and Chapters down to individual clauses, including cross-reference graphs.
    </div>
</div>
""", unsafe_allow_html=True)

data_dir = settings.paths.data_dir
trees_dir = os.path.join(data_dir, "trees")

if not os.path.exists(trees_dir):
    st.info("No documents have been ingested yet. Visit the Ingest page to process documents.")
else:
    docs = [f.split(".")[0] for f in os.listdir(trees_dir) if f.endswith(".json")]
    if not docs:
        st.info("No documents found in the trees directory.")
    else:
        st.markdown('<div class="lex-card">', unsafe_allow_html=True)
        col_sel, col_stats = st.columns([1.5, 2])
        with col_sel:
            selected_doc = st.selectbox("Select Document to Inspect", docs)
            
        if selected_doc:
            nodes = load_tree(selected_doc)
            total_nodes = len(nodes)
            max_level = max([n.level for n in nodes]) if nodes else 0
            xrefs_count = sum([len(n.xrefs_raw) for n in nodes if n.xrefs_raw])
            
            with col_stats:
                st.markdown(f"""
                <div style="display: flex; gap: 1.5rem; justify-content: flex-end; align-items: center; height: 100%; padding-top: 0.5rem;">
                    <div>
                        <div class="lex-stat-val" style="font-size: 1.3rem;">{total_nodes}</div>
                        <div class="lex-stat-label">Total Nodes</div>
                    </div>
                    <div>
                        <div class="lex-stat-val" style="font-size: 1.3rem;">{max_level}</div>
                        <div class="lex-stat-label">Tree Depth</div>
                    </div>
                    <div>
                        <div class="lex-stat-val" style="font-size: 1.3rem;">{xrefs_count}</div>
                        <div class="lex-stat-label">Cross-Refs</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if selected_doc and nodes:
            st.markdown(f"""
            <div style="margin: 1.25rem 0 0.75rem 0; font-size: 1.05rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif;">
                Structural Tree Navigation
            </div>
            """, unsafe_allow_html=True)
            
            badge_map = {
                "ACT": "lex-badge-indigo",
                "CHAPTER": "lex-badge-sky",
                "SECTION": "lex-badge-emerald",
                "SUBSECTION": "lex-badge-slate",
                "CLAUSE": "lex-badge-slate"
            }
            
            def render_node(node_id, depth=0):
                node = next((n for n in nodes if n.node_id == node_id), None)
                if not node:
                    return
                    
                type_name = node.node_type.name.upper()
                badge_class = badge_map.get(type_name, "lex-badge-slate")
                
                label_text = f"{node.node_type.name.capitalize()} {node.label} {node.heading or ''}".strip()
                if not label_text:
                    label_text = "Unlabeled Node"
                    
                indent_px = min(depth * 18, 120)
                
                with st.expander(f"{'  ' * depth}[{type_name}] {label_text}"):
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                        <div style="display: flex; gap: 0.4rem; align-items: center;">
                            <span class="lex-badge {badge_class}">{type_name}</span>
                            <span class="lex-badge lex-badge-slate">ID: {node.node_id}</span>
                        </div>
                        <span class="lex-badge lex-badge-sky">Page {node.page_start} | Level {node.level}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if node.text:
                        st.markdown(f"""
                        <div class="lex-result-box" style="margin: 0.5rem 0;">
                            {node.text}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    if node.xrefs_raw:
                        st.markdown(f"""
                        <div style="margin-top: 0.5rem; font-size: 0.82rem; color: #94a3b8;">
                            <strong>Cross References:</strong> <code>{', '.join(node.xrefs_raw)}</code>
                            &rarr; Resolved: <code>{', '.join(node.xrefs_resolved) if node.xrefs_resolved else 'Unresolved'}</code>
                        </div>
                        """, unsafe_allow_html=True)
                
                for child_id in node.children_ids:
                    render_node(child_id, depth + 1)
                    
            root_node = next((n for n in nodes if n.level == 0), None)
            if root_node:
                render_node(root_node.node_id)
            else:
                st.error("No root node found in this tree hierarchy.")
