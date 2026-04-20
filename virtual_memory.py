import streamlit as st
import pandas as pd
from algorithms import fifo_steps, lru_steps, optimal_steps
from visualization import hit_fault_pie, faults_graph, execution_table, faults_vs_frames
from utils import get_unique_pages


def vm_ui():
    st.markdown("### 💾 Virtual Memory Analysis")

    pages_input = st.session_state.get("pages", "").strip()
    frames      = st.session_state.get("frames", 3)

    if not pages_input:
        st.warning("⚠️ Please enter a reference string in the sidebar first.")
        return

    pages  = list(map(int, pages_input.split()))
    unique = get_unique_pages(pages)

    algo = st.selectbox("Replacement Algorithm", ["FIFO", "LRU", "OPT (Optimal)"], key="vm_algo")

    algo_map = {
        "FIFO":          fifo_steps,
        "LRU":           lru_steps,
        "OPT (Optimal)": optimal_steps,
    }
    algo_func     = algo_map[algo]
    steps, faults = algo_func(pages, frames)
    hits          = len(pages) - faults
    hit_ratio     = round(hits / len(pages) * 100, 1)
    fault_rate    = round(faults / len(pages) * 100, 1)

    st.markdown("#### 📊 Performance Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Page Faults", faults)
    c2.metric("Page Hits",   hits)
    c3.metric("Hit Ratio",   f"{hit_ratio}%")
    c4.metric("Fault Rate",  f"{fault_rate}%")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🥧 Hit/Fault Breakdown", "📈 Fault Timeline", "📊 Frame Analysis"])

    with tab1:
        col_l, col_r = st.columns(2)
        with col_l:
            hit_fault_pie(faults, len(pages))
        with col_r:
            st.markdown("#### 📋 Execution Log")
            execution_table(steps)

        st.markdown("#### 🔬 Algorithm Comparison (same frames)")
        comp_rows = []
        for name, fn in algo_map.items():
            _, f = fn(pages, frames)
            h = len(pages) - f
            comp_rows.append({
                "Algorithm": name,
                "Faults":    f,
                "Hits":      h,
                "Hit Ratio": f"{round(h/len(pages)*100,1)}%",
            })
        st.table(pd.DataFrame(comp_rows))

    with tab2:
        faults_graph(steps)
        st.markdown(
            "> **Belady's Anomaly** (FIFO only): Adding more frames can *increase* faults "
            "for certain reference strings. Switch to LRU or OPT to avoid this.",
        )

    with tab3:
        st.markdown("#### How Frame Count Affects Page Faults")


        max_possible = len(pages)
        max_frames_to_test = st.slider(
            "Show faults up to how many frames?",
            min_value=2,
            max_value=max_possible,
            value=min(frames + 4, max_possible),
            step=1,
            help="Drag to expand or shrink the frame range shown on the graph"
        )

        faults_vs_frames(pages, algo_func, max_frames_to_test, frames)

        st.caption(
            "⭐ Star marks your currently selected frame count. "
            "Drag the slider above to explore more of the curve.\n\n"
            "- **FIFO** may show Belady's Anomaly (faults increase with more frames)\n"
            "- **LRU** and **OPT** show monotonically decreasing faults\n"
            "- **OPT** provides the theoretical lower bound"
        )
