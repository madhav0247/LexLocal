import streamlit as st
import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.config import settings

st.title("Audit Log")

db_path = os.path.join(settings.paths.data_dir, "meta.sqlite")
if not os.path.exists(db_path):
    st.warning("No audit database found.")
else:
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY ts DESC LIMIT 100", conn)
        if df.empty:
            st.info("Audit log is empty.")
        else:
            st.dataframe(df)
    except Exception as e:
        st.error(f"Failed to read audit log: {e}")
    finally:
        conn.close()
