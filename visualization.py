import streamlit as st
import pandas as pd
import plotly.graph_objects as go


THEME = {
    "bg":        "#0D0F0E",
    "surface":   "#141714",
    "border":    "#2A3B2D",
    "primary":   "#7FD99A",   
    "accent":    "#F5C542",  
    "danger":    "#E05C5C",   
    "text":      "#D4E8D8",
    "subtext":   "#6B8F71",
    "plotly_template": "plotly_dark",
}

PLOTLY_LAYOUT = dict(
    template=THEME["plotly_template"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'JetBrains Mono', monospace", color=THEME["text"]),
    xaxis=dict(gridcolor=THEME["border"], linecolor=THEME["border"]),
    yaxis=dict(gridcolor=THEME["border"], linecolor=THEME["border"]),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=40, r=20, t=50, b=40),
)



def faults_graph(steps):
    faults  = [1 if s[2] == "Fault" else 0 for s in steps]
    pages   = [s[0] for s in steps]
    df = pd.DataFrame({"Access": range(len(faults)), "Fault": faults, "Page": pages})
    df["Rolling"] = df["Fault"].rolling(window=3, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Access"], y=df["Rolling"],
        mode="lines", name="Rolling Avg (w=3)",
        line=dict(color=THEME["accent"], width=2.5, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=df[df["Fault"] == 1]["Access"],
        y=df[df["Fault"] == 1]["Fault"],
        mode="markers", name="Page Fault",
        marker=dict(size=10, color=THEME["danger"], symbol="x"),
    ))
    fig.add_trace(go.Scatter(
        x=df[df["Fault"] == 0]["Access"],
        y=df[df["Fault"] == 0]["Fault"],
        mode="markers", name="Hit",
        marker=dict(size=8, color=THEME["primary"], symbol="circle"),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Page Faults Over Time",
                      xaxis_title="Access #", yaxis_title="Fault (1=yes)")
    st.plotly_chart(fig, use_container_width=True)


def memory_blocks(memory, capacity):
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    cols_per_row = 8
    rows = (capacity + cols_per_row - 1) // cols_per_row
    idx = 0
    for _ in range(rows):
        cols = st.columns(cols_per_row, gap="small")
        for col in cols:
            if idx < capacity:
                if idx < len(memory):
                    col.markdown(
                        f"""<div style="
                            height:80px; border-radius:8px;
                            background:linear-gradient(145deg,#1A2E1E,#0F1A12);
                            box-shadow:0 0 12px rgba(127,217,154,0.25),inset 0 0 6px rgba(127,217,154,0.1);
                            border:1px solid {THEME['primary']};
                            display:flex; align-items:center; justify-content:center;
                            color:{THEME['primary']}; font-size:20px; font-weight:700;
                            font-family:'JetBrains Mono',monospace;
                        ">{memory[idx]}</div>""",
                        unsafe_allow_html=True,
                    )
                else:
                    col.markdown(
                        f"""<div style="
                            height:80px; border-radius:8px;
                            background:#0D0F0E; border:1px dashed {THEME['border']};
                            display:flex; align-items:center; justify-content:center;
                            color:{THEME['subtext']}; font-size:13px;
                            font-family:'JetBrains Mono',monospace;
                        ">free</div>""",
                        unsafe_allow_html=True,
                    )
                idx += 1
    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)



def execution_table(steps):
    data = []
    for i, (page, frames, status) in enumerate(steps):
        data.append({
            "Step":   i + 1,
            "Page":   page,
            "Frames": str(frames),
            "Status": "✅ Hit" if status == "Hit" else "❌ Fault",
        })
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, height=320)



def frame_details(memory, capacity):
    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
    data = []
    for i in range(capacity):
        if i < len(memory):
            data.append({"Frame": i, "Page": memory[i], "Status": "Occupied"})
        else:
            data.append({"Frame": i, "Page": "—", "Status": "Free"})
    df = pd.DataFrame(data)
    st.table(df)



def hit_fault_pie(faults, total):
    hits = total - faults
    fig = go.Figure(data=[go.Pie(
        labels=["Hits", "Faults"],
        values=[hits, faults],
        hole=0.45,
        marker=dict(colors=[THEME["primary"], THEME["danger"]]),
        textfont=dict(family="'JetBrains Mono', monospace"),
    )])
    fig.update_layout(**PLOTLY_LAYOUT, title="Hit vs Fault Distribution")
    st.plotly_chart(fig, use_container_width=True)



def faults_vs_frames(pages, algo_func, max_frames, selected_frames=None):
    results = []
    for f in range(1, max_frames + 1):
        _, faults = algo_func(pages, f)
        results.append(faults)

    df = pd.DataFrame({"Frames": list(range(1, max_frames + 1)), "Faults": results})


    current_f = min(selected_frames, max_frames) if selected_frames else max_frames

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Frames"], y=df["Faults"],
        mode="lines+markers", name="Faults",
        line=dict(color=THEME["accent"], width=2.5),
        marker=dict(size=7, color=THEME["accent"]),
    ))
    fig.add_trace(go.Scatter(
        x=[current_f], y=[results[current_f - 1]],
        mode="markers", name=f"Selected ({current_f} frames)",
        marker=dict(size=14, color=THEME["danger"], symbol="star"),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Faults vs Number of Frames",
        xaxis_title="Frames", yaxis_title="Page Faults",
    )
    st.plotly_chart(fig, use_container_width=True)


def step_memory_view(steps, capacity):
    if not steps:
        return
    step_idx = st.slider("🔍 Step Through Simulation", 0, len(steps) - 1, len(steps) - 1)
    page, mem, status = steps[step_idx]
    badge = (
        f"<span style='background:{THEME['primary']};color:#0D0F0E;"
        f"padding:3px 10px;border-radius:4px;font-weight:700;'>HIT</span>"
        if status == "Hit" else
        f"<span style='background:{THEME['danger']};color:#fff;"
        f"padding:3px 10px;border-radius:4px;font-weight:700;'>FAULT</span>"
    )
    st.markdown(
        f"<p style='font-family:JetBrains Mono,monospace;color:{THEME['text']};'>"
        f"Step <b>{step_idx + 1}</b> — Page <b>{page}</b> &nbsp;{badge}</p>",
        unsafe_allow_html=True,
    )
    memory_blocks(mem, capacity)
    frame_details(mem, capacity)
