import streamlit as st
import random
from paging import paging_ui
from segmentation import segmentation_ui
from virtual_memory import vm_ui


st.set_page_config(
    page_title="Memora — Memory Management Visualizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;600;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    background-color: #0D0F0E !important;
    color: #D4E8D8 !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0A0C0B !important;
    border-right: 1px solid #1E2E21 !important;
}
section[data-testid="stSidebar"] * { color: #D4E8D8 !important; }

/* ── Inputs ── */
textarea, input[type="text"], input[type="number"] {
    background: #111411 !important;
    border: 1px solid #2A3B2D !important;
    color: #D4E8D8 !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
textarea:focus, input:focus {
    border-color: #7FD99A !important;
    box-shadow: 0 0 0 2px rgba(127,217,154,0.15) !important;
}

/* ── Buttons ── */
button[kind="primary"], .stButton > button {
    background: linear-gradient(135deg, #7FD99A, #5BBF7A) !important;
    color: #0D0F0E !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #F5C542, #E0A820) !important;
    color: #0D0F0E !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(245,197,66,0.3) !important;
}

/* ── Selectbox ── */
div[data-baseweb="select"] > div {
    background: #111411 !important;
    border: 1px solid #2A3B2D !important;
    border-radius: 6px !important;
}

/* ── Tabs ── */
button[data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    color: #6B8F71 !important;
    border-bottom: 2px solid transparent !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #7FD99A !important;
    border-bottom: 2px solid #7FD99A !important;
}

/* ── Metrics ── */
div[data-testid="metric-container"] {
    background: #111714 !important;
    border: 1px solid #2A3B2D !important;
    border-radius: 8px !important;
    padding: 14px 18px !important;
}
div[data-testid="metric-container"] label {
    color: #6B8F71 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #F5C542 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 26px !important;
    font-weight: 800 !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] {
    border: 1px solid #2A3B2D !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* ── Divider ── */
hr { border-color: #1E2E21 !important; }

/* ── Info / Warning boxes ── */
div[data-testid="stAlert"] {
    background: #111a12 !important;
    border: 1px solid #2A3B2D !important;
    border-radius: 8px !important;
    color: #D4E8D8 !important;
}

/* ── Slider ── */
div[data-testid="stSlider"] div[role="slider"] {
    background: #7FD99A !important;
    border: 2px solid #5BBF7A !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0D0F0E; }
::-webkit-scrollbar-thumb { background: #2A3B2D; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #7FD99A; }
</style>
""", unsafe_allow_html=True)


if "pages" not in st.session_state:
    st.session_state["pages"] = "7 0 1 2 0 3 0 4 2 3 0 3 2"
if "frames" not in st.session_state:
    st.session_state["frames"] = 4


st.sidebar.markdown(
    "<h2 style='font-family:Syne,sans-serif;color:#7FD99A;"
    "letter-spacing:0.05em;margin-bottom:4px;'>⚙️ Configuration</h2>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    "<p style='font-family:JetBrains Mono,monospace;font-size:11px;"
    "color:#6B8F71;margin-bottom:18px;'>Memora v2.0</p>",
    unsafe_allow_html=True,
)

pages_input = st.sidebar.text_area(
    "Reference String",
    value=st.session_state["pages"],
    help="Space-separated page numbers, e.g. 7 0 1 2 0 3"
)
frames_input = st.sidebar.number_input(
    "Number of Frames",
    min_value=1, max_value=20,
    value=st.session_state["frames"],
)

col_a, col_b = st.sidebar.columns(2)

with col_a:
    if st.button("Apply", use_container_width=True):
        try:
            parsed = list(map(int, pages_input.split()))
            if not parsed:
                raise ValueError
            st.session_state["pages"]  = pages_input.strip()
            st.session_state["frames"] = int(frames_input)
            st.session_state["_applied"] = True
            st.rerun()
        except ValueError:
            st.sidebar.error("⚠️ Invalid reference string. Use space-separated integers.")

if st.session_state.get("_applied"):
    st.sidebar.success("✓ Configuration applied!")
    st.session_state["_applied"] = False

with col_b:
    if st.button("Random", use_container_width=True):
        rand = [random.randint(0, 7) for _ in range(14)]
        st.session_state["pages"]  = " ".join(map(str, rand))
        st.session_state["frames"] = random.randint(3, 5)
        st.rerun()

st.sidebar.markdown("---")
module = st.sidebar.selectbox(
    "Module",
    ["Paging", "Virtual Memory", "Segmentation"],
    key="module",
    help="Choose the memory management module to simulate"
)


st.sidebar.markdown("#### 📝 Current Reference String")
pages_preview = st.session_state["pages"].split()
badges = " ".join(
    f"<span style='display:inline-block;background:#1A2E1E;color:#7FD99A;"
    f"border:1px solid #2A3B2D;border-radius:4px;padding:1px 7px;"
    f"font-family:JetBrains Mono,monospace;font-size:13px;margin:2px;'>{p}</span>"
    for p in pages_preview
)
st.sidebar.markdown(
    f"<div style='line-height:2;'>{badges}</div>",
    unsafe_allow_html=True
)
st.sidebar.markdown(
    f"<p style='font-family:JetBrains Mono,monospace;font-size:11px;"
    f"color:#6B8F71;margin-top:8px;'>"
    f"{len(pages_preview)} refs · {len(set(pages_preview))} unique · "
    f"{st.session_state['frames']} frames</p>",
    unsafe_allow_html=True
)


st.markdown("""
<div style='
    padding: 32px 0 20px 0;
    border-bottom: 1px solid #1E2E21;
    margin-bottom: 28px;
'>
    <span style='
        font-family: Syne, sans-serif;
        font-size: 36px;
        font-weight: 800;
        color: #7FD99A;
        letter-spacing: -0.02em;
    '>Me</span><span style='
        font-family: Syne, sans-serif;
        font-size: 36px;
        font-weight: 800;
        color: #F5C542;
        letter-spacing: -0.02em;
    '>Mora</span>
    <span style='
        font-family: JetBrains Mono, monospace;
        font-size: 13px;
        color: #6B8F71;
        margin-left: 16px;
        vertical-align: middle;
    '>Dynamic Memory Management Visualizer</span>
</div>
""", unsafe_allow_html=True)


if module == "Paging":
    paging_ui()
elif module == "Virtual Memory":
    vm_ui()
else:
    segmentation_ui()


st.markdown("""
<div style='
    margin-top: 60px;
    padding-top: 18px;
    border-top: 1px solid #1E2E21;
    font-family: JetBrains Mono, monospace;
    font-size: 11px;
    color: #3A5A3E;
    text-align: center;
'>
    Memora v2.0 · FIFO · LRU · OPT · Paging · Segmentation · Virtual Memory
</div>
""", unsafe_allow_html=True)
