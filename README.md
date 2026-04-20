MeMora — Memory Management Visualizer
A web-based simulator that shows how operating systems manage memory using paging, segmentation, virtual memory, and page replacement algorithms (FIFO, LRU & OPT).
🔗 Live Demo: https://numa-simulatorpy-i5bh3saktfrqyd49mewxru.streamlit.app/

What is this?
MeMora helps you understand how an operating system handles memory. You give it a reference string and a frame count, and it shows you — step by step — what happens when pages are loaded, replaced, or hit in memory. No more tracing algorithms by hand.

Features

Choose between FIFO, LRU, and OPT (Optimal) page replacement algorithms
Enter your own page reference strings
Set memory frame count from the sidebar
See memory frames, page tables, hit/fault rates visually
Step through each memory access one at a time
Compare all three algorithms side by side on the same input
Translate logical segment,offset addresses to physical addresses (Segmentation module)
Generate a random reference string with one click


How to Use

Enter a reference string in the sidebar (example: 7 0 1 2 0 3 0 4)
Set the number of frames
Click Apply
Select a module — Paging, Virtual Memory, or Segmentation
Browse the tabs to explore fault timelines, memory views, and comparison tables


Tech Stack

Python + Streamlit
Plotly for interactive charts
Pandas for data tables


Run Locally
bashpip install streamlit plotly pandas
streamlit run app.py

Project Structure
MeMora/
├── app.py              # Main entry point
├── algorithms.py       # FIFO, LRU, OPT logic
├── paging.py           # Paging module
├── virtual_memory.py   # Virtual memory analysis
├── segmentation.py     # Segmentation address translation
├── visualization.py    # All charts and visual components
└── utils.py            # Input parsing and helpers
