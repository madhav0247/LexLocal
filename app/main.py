import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from src.storage.sqlite_init import init_db

init_db()
st.set_page_config(page_title="LexLocal - Legal Intelligence", layout="wide", initial_sidebar_state="expanded")

def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    :root {
        --bg-main: #0b0f19;
        --surface-1: rgba(17, 24, 39, 0.7);
        --surface-2: rgba(30, 41, 59, 0.55);
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-glass-hover: rgba(99, 102, 241, 0.35);
        --accent-indigo: #6366f1;
        --accent-sky: #38bdf8;
        --text-headline: #f8fafc;
        --text-sub: #94a3b8;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    code, pre, .mono-text, .lex-citation, [data-testid="stMarkdownContainer"] code {
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Hide Deploy button and default footer while keeping menu and sidebar toggle */
    .stDeployButton, footer {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Main app sleek mesh gradient */
    .stApp {
        background-color: var(--bg-main);
        background-image: 
            radial-gradient(at 15% 15%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
            radial-gradient(at 85% 85%, rgba(56, 189, 248, 0.08) 0px, transparent 50%);
        background-attachment: fixed;
    }

    /* Glassmorphism sidebar */
    [data-testid="stSidebar"] {
        background: rgba(11, 15, 25, 0.75) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    
    /* Sleek gradient headers */
    h1 {
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
        background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem !important;
    }
    
    h2 {
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        letter-spacing: -0.02em !important;
        margin-top: 1rem !important;
    }

    h3 {
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        letter-spacing: -0.01em !important;
    }

    /* Buttons with executive micro-animation */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.35rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) !important;
    }

    /* Input controls */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div {
        background-color: rgba(15, 23, 42, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        transition: all 0.2s ease !important;
        font-size: 0.92rem !important;
    }
    
    .stTextInput>div>div>input:focus, 
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div:focus-within {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
    }

    /* Multiselect chips */
    [data-baseweb="tag"] {
        background: rgba(99, 102, 241, 0.2) !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
        border-radius: 6px !important;
    }

    /* Expanders styling */
    [data-testid="stExpander"] {
        background: rgba(17, 24, 39, 0.5) !important;
        border-radius: 10px !important;
        border: 1px solid var(--border-glass) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 0.75rem;
    }
    
    [data-testid="stExpander"]:hover {
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    
    [data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: #e2e8f0 !important;
        padding: 0.65rem 1rem !important;
    }
    
    /* Alerts and notices */
    .stAlert {
        background: rgba(17, 24, 39, 0.6) !important;
        border: 1px solid var(--border-glass) !important;
        backdrop-filter: blur(12px) !important;
        border-radius: 10px !important;
    }

    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border-glass) !important;
        border-radius: 10px !important;
        overflow: hidden;
    }

    /* Custom UI Components */
    .lex-card {
        background: rgba(17, 24, 39, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(12px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .lex-card:hover {
        border-color: rgba(99, 102, 241, 0.3);
    }

    .lex-hero {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.5rem;
    }

    .lex-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.22rem 0.65rem;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    .lex-badge-indigo {
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .lex-badge-sky {
        background: rgba(56, 189, 248, 0.15);
        color: #7dd3fc;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }

    .lex-badge-emerald {
        background: rgba(16, 185, 129, 0.15);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .lex-badge-slate {
        background: rgba(148, 163, 184, 0.12);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.22);
    }

    .lex-stat-val {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 40%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }

    .lex-stat-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    .lex-result-box {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-left: 3px solid #6366f1;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0 1.25rem 0;
        line-height: 1.6;
        color: #e2e8f0;
    }

    .lex-breadcrumb-bar {
        background: rgba(30, 41, 59, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        padding: 0.35rem 0.75rem;
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0b0f19; 
    }
    ::-webkit-scrollbar-thumb {
        background: #1e293b; 
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155; 
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    with st.sidebar:
        st.markdown("""
        <div style="padding: 1rem 0; text-align: center;">
            <div style="font-size: 1.2rem; font-weight: 800; letter-spacing: -0.02em; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif;">
                LEXLOCAL
            </div>
            <div style="font-size: 0.75rem; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.2rem;">
                Legal Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.info("Log in on the main screen to unlock the platform.")
        st.markdown("""
        <div class="lex-card" style="padding: 0.85rem; font-size: 0.82rem;">
            <div style="color: #94a3b8; margin-bottom: 0.4rem; font-weight: 600;">Access Profiles</div>
            <div style="margin-bottom: 0.3rem;"><span class="lex-badge lex-badge-indigo">Admin</span> <code>admin</code> / <code>admin</code></div>
            <div><span class="lex-badge lex-badge-slate">User</span> <code>user</code> / <code>user</code></div>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="lex-card" style="padding: 2.25rem 2rem; margin-top: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
                <div style="font-size: 1.4rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif;">
                    LexLocal Authentication
                </div>
                <span class="lex-badge lex-badge-sky">Air-Gapped</span>
            </div>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.5rem; line-height: 1.5;">
                Offline legal document intelligence platform. Ingest contracts, recover structural hierarchies, and run hybrid vector search without cloud dependencies.
            </p>
        </div>
        """, unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="admin or user")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        if st.button("Authenticate", use_container_width=True):
            if username == "admin" and password == "admin":
                st.session_state.role = "admin"
                st.rerun()
            elif username == "user" and password == "user":
                st.session_state.role = "user"
                st.rerun()
            else:
                st.error("Invalid credentials. Try admin/admin or user/user.")
    st.stop()

with st.sidebar:
    st.markdown(f"""
    <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <div style="font-size: 1.15rem; font-weight: 800; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif;">
                    LEXLOCAL
                </div>
                <div style="font-size: 0.7rem; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase;">
                    Legal Intelligence
                </div>
            </div>
            <span class="lex-badge lex-badge-emerald">Active</span>
        </div>
        <div style="margin-top: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 0.78rem; color: #94a3b8;">Role:</span>
            <span class="lex-badge {'lex-badge-indigo' if st.session_state.role == 'admin' else 'lex-badge-slate'}">{st.session_state.role}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        st.session_state.role = None
        st.rerun()

nav_pages = [
    st.Page("pages/0_Home.py", title="Home"),
    st.Page("pages/2_Ask.py", title="Ask"),
    st.Page("pages/3_Inspect.py", title="Inspect")
]

if st.session_state.role == "admin":
    nav_pages.insert(1, st.Page("pages/1_Ingest.py", title="Ingest"))
    nav_pages.insert(2, st.Page("pages/6_Manage.py", title="Manage Documents"))
    nav_pages.extend([
        st.Page("pages/4_Benchmark.py", title="Benchmark"),
        st.Page("pages/5_Audit.py", title="Audit")
    ])

pg = st.navigation(nav_pages)
pg.run()
