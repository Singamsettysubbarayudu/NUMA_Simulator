import streamlit as st
from algorithms import fifo_steps, lru_steps, optimal_steps
from visualization import (
    faults_graph, step_memory_view, execution_table, hit_fault_pie
)
from utils import get_unique_pages


def paging_ui():
    pages  = list(map(int, st.session_state["pages"].split()))
    frames = st.session_state["frames"]

    st.markdown("### ⚙️ Algorithm Configuration")
    algo = st.selectbox("Replacement Algorithm", ["FIFO", "LRU", "OPT (Optimal)"], key="paging_algo")

    if algo == "FIFO":
        steps, faults = fifo_steps(pages, frames)
    elif algo == "LRU":
        steps, faults = lru_steps(pages, frames)
    else:
        steps, faults = optimal_steps(pages, frames)

    hits      = len(pages) - faults
    hit_ratio = round(hits / len(pages) * 100, 1)

    st.markdown("### 📊 Simulation Summary")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Algorithm",   algo.split()[0])
    c2.metric("Total Refs",  len(pages))
    c3.metric("Page Faults", faults)
    c4.metric("Hits",        hits)
    c5.metric("Hit Ratio",   f"{hit_ratio}%")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(
        ["📈 Fault Timeline", "🗂️ Execution Table", "🧠 Memory View"]
    )

    with tab1:
        faults_graph(steps)
        st.markdown("#### Hit/Fault Distribution")
        hit_fault_pie(faults, len(pages))

    with tab2:
        execution_table(steps)

    with tab3:
        st.markdown("#### Step-by-Step Memory State")
        step_memory_view(steps, frames)
