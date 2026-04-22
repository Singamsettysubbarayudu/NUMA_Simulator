# 🧠 MeMora — Memory Management Visualizer

A web-based simulator that shows how operating systems manage memory using paging, segmentation, virtual memory, and page replacement algorithms (FIFO, LRU & OPT).

🔗 **Live Demo:** [Click Here](https://memoravisualizer01-exrhopjlcsfprqizeapptv.streamlit.app/)

---

## What is this?

MeMora helps you understand how an OS handles memory. You give it a reference string and frame count — it shows you step by step what happens when pages are loaded, replaced, or hit in memory. No more tracing algorithms by hand.

---

## Features

- FIFO, LRU, and OPT page replacement algorithms
- Enter your own page reference strings
- Adjustable memory frame count
- See memory frames, page tables, hit/fault rates visually
- Step through each memory access one by one
- Compare all three algorithms side by side
- Translate logical (segment, offset) to physical addresses
- Generate random reference strings with one click

---

## How to Use

1. Enter a reference string (example: `7 0 1 2 0 3 0 4`)
2. Set the number of frames
3. Click **Apply**
4. Select a module — Paging, Virtual Memory, or Segmentation
5. Browse the tabs to explore

---

## Tech Stack

- Python + Streamlit
- Plotly for charts
- Pandas for data tables

---

## Run Locally

```bash
pip install streamlit plotly pandas
streamlit run app.py
