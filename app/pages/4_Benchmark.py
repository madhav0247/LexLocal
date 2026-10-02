import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import pandas as pd
import subprocess

st.markdown("""
<div class="lex-hero">
    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.75rem;">
        <span class="lex-badge lex-badge-indigo">Evaluation Engine</span>
        <span class="lex-badge lex-badge-emerald">RRF vs Baseline</span>
    </div>
    <div style="font-size: 1.85rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; letter-spacing: -0.02em;">
        Retrieval Benchmark & Performance
    </div>
    <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.5rem; max-width: 760px; line-height: 1.5;">
        Quantitative evaluation comparing Hierarchical Hybrid (LanceDB + BM25) against Hierarchical Dense and Naive chunking baselines across exact clause retrieval metrics.
    </div>
</div>
""", unsafe_allow_html=True)

eval_results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../eval/results/metrics.csv'))

if os.path.exists(eval_results_path):
    df = pd.read_csv(eval_results_path)
    
    # Calculate top metrics for KPI cards
    best_row = df.loc[df['MRR'].idxmax()] if not df.empty else None
    
    if best_row is not None:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="lex-card" style="text-align: center; padding: 1rem;">
                <div class="lex-stat-val">{best_row['R@1']*100:.1f}%</div>
                <div class="lex-stat-label">Best Recall @ 1</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="lex-card" style="text-align: center; padding: 1rem;">
                <div class="lex-stat-val">{best_row['R@3']*100:.1f}%</div>
                <div class="lex-stat-label">Best Recall @ 3</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="lex-card" style="text-align: center; padding: 1rem;">
                <div class="lex-stat-val">{best_row['R@5']*100:.1f}%</div>
                <div class="lex-stat-label">Best Recall @ 5</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="lex-card" style="text-align: center; padding: 1rem;">
                <div class="lex-stat-val">{best_row['MRR']:.3f}</div>
                <div class="lex-stat-label">Mean Recip. Rank</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown('<div class="lex-card">', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size: 1.05rem; font-weight: 700; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; margin-bottom: 0.75rem;">
        Comparative Evaluation Results
    </div>
    """, unsafe_allow_html=True)
    
    display_df = df.copy()
    display_df['R@1'] = display_df['R@1'].apply(lambda x: f"{x*100:.1f}%")
    display_df['R@3'] = display_df['R@3'].apply(lambda x: f"{x*100:.1f}%")
    display_df['R@5'] = display_df['R@5'].apply(lambda x: f"{x*100:.1f}%")
    display_df['MRR'] = display_df['MRR'].apply(lambda x: f"{x:.4f}")
    
    st.dataframe(display_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="lex-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem; margin-bottom: 0.5rem;">
                Metric Definitions
            </div>
            <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.6;">
                <div><strong style="color: #cbd5e1;">Recall@K (R@1, R@3, R@5):</strong> Probability that the exact ground-truth clause is present in the top-K returned hits.</div>
                <div style="margin-top: 0.4rem;"><strong style="color: #cbd5e1;">MRR (Mean Reciprocal Rank):</strong> Evaluates rank position quality: <code>1/rank</code> of the first correct clause. An MRR of 1.0 indicates every query returned the target clause as rank #1.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="lex-card">
            <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem; margin-bottom: 0.5rem;">
                Architectural Insights
            </div>
            <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.6;">
                <div><span class="lex-badge lex-badge-emerald">Hierarchical + Hybrid</span> achieves superior accuracy because BM25 captures precise legal phrasing (section numbers and statutory keywords) while LanceDB vectors capture semantic context.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No evaluation results found. Run `python eval/run_eval.py` to generate the benchmark metrics.")
