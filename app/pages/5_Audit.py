import streamlit as st
import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config import settings

st.markdown("""
<div class="lex-hero">
    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span class="lex-badge lex-badge-indigo">Compliance Trail</span>
        <span class="lex-badge lex-badge-emerald">Local SQLite Log</span>
    </div>
    <div style="font-size: 1.85rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.02em;">
        Security & Audit Log
    </div>
    <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem; max-width: 760px; line-height: 1.5;">
        Complete trace of document ingestions, query executions, and document deletions recorded into local SQLite metadata storage.
    </div>
</div>
""", unsafe_allow_html=True)

db_path = os.path.join(settings.paths.data_dir, "meta.sqlite")
if not os.path.exists(db_path):
    st.info("No audit database found yet. Ingest documents or run queries to generate audit events.")
else:
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY ts DESC LIMIT 200", conn)
        if df.empty:
            st.info("Audit log is currently empty.")
        else:
            total_events = len(df)
            ingest_count = len(df[df['event_type'] == 'ingest']) if 'event_type' in df.columns else 0
            query_count = len(df[df['event_type'] == 'query']) if 'event_type' in df.columns else 0
            delete_count = len(df[df['event_type'] == 'delete']) if 'event_type' in df.columns else 0
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="lex-card" style="text-align: center; padding: 1rem;">
                    <div class="lex-stat-val">{total_events}</div>
                    <div class="lex-stat-label">Total Events</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="lex-card" style="text-align: center; padding: 1rem;">
                    <div class="lex-stat-val">{ingest_count}</div>
                    <div class="lex-stat-label">Ingest Operations</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="lex-card" style="text-align: center; padding: 1rem;">
                    <div class="lex-stat-val">{query_count}</div>
                    <div class="lex-stat-label">Query Operations</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div class="lex-card" style="text-align: center; padding: 1rem;">
                    <div class="lex-stat-val">{delete_count}</div>
                    <div class="lex-stat-label">Delete Operations</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('<div class="lex-card">', unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 0.75rem;">
                Event Records (Recent 200 Entries)
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to read audit log: {e}")
    finally:
        conn.close()
