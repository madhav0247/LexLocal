import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

st.set_page_config(page_title="LexLocal", layout="wide")

def inject_custom_css():
    st.markdown("""
    <style>
    /* Global Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide the top right toolbar (Deploy, Record, etc) */
    [data-testid="stToolbar"], .stAppHeader, [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Sleek background gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    /* Glassmorphism for sidebar */
    [data-testid="stSidebar"] {
        background: rgba(30, 41, 59, 0.4) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Header customization */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
        background: -webkit-linear-gradient(45deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0.5rem;
    }
    
    h2, h3 {
        font-weight: 600 !important;
        color: #e2e8f0 !important;
        letter-spacing: -0.01em !important;
    }

    /* Buttons with glowing hover */
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6, #6366f1) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.2) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4) !important;
    }

    /* Input fields and selectboxes */
    .stTextInput>div>div>input, .stSelectbox>div>div, .stTextArea>div>div>textarea {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: white !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput>div>div>input:focus, .stSelectbox>div>div:focus-within, .stTextArea>div>div>textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Expanders styling */
    [data-testid="stExpander"] {
        background: rgba(30, 41, 59, 0.3);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        overflow: hidden;
    }
    
    [data-testid="stExpander"] summary {
        background: rgba(255, 255, 255, 0.02) !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* Info banners */
    .stAlert {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        backdrop-filter: blur(8px);
        border-radius: 10px !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a; 
    }
    ::-webkit-scrollbar-thumb {
        background: #334155; 
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569; 
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("LexLocal Login")
        st.markdown("Please authenticate to access the platform.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
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
    st.markdown(f"**Logged in as:** `{st.session_state.role}`")
    if st.button("Logout"):
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
