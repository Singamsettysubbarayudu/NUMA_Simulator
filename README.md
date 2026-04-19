# NUMA Memory Management Simulator

**Live Demo:** https://numa-simulatorpy-i5bh3saktfrqyd49mewxru.streamlit.app/

## What is this?

A web-based simulator that shows how operating systems manage memory using paging, virtual memory, and page replacement algorithms (FIFO & LRU).

## Features

- Choose memory size and page size
- Enter custom page reference strings
- Switch between FIFO and LRU algorithms
- See memory frames, page tables, and fault rates visually
- Step through each memory access

## How to use

1. Set memory size and page size in the sidebar
2. Enter page numbers (example: 7,0,1,2,0,3)
3. Click Run Simulation
4. Check the tabs for different views

## Tech stack

- Python + Streamlit
- Matplotlib for visualizations
- Pandas for data tables

## Run locally

```bash
pip install streamlit pandas matplotlib numpy
streamlit run Numa-Simulator.py
