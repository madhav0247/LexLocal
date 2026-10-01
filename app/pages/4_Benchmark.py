import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pandas as pd

st.title("Benchmark")
st.markdown("This page compares Hierarchical vs Naive chunking using the evaluation set.")

eval_results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../eval/results/metrics.csv'))

if os.path.exists(eval_results_path):
    st.subheader("Evaluation Results")
    df = pd.read_csv(eval_results_path)
    st.dataframe(df)
else:
    st.warning("No evaluation results found. Run `python eval/run_eval.py` to generate metrics.")
