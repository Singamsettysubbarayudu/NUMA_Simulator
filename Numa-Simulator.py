import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict, defaultdict
import time
import numpy as np

class PageTableEntry:
    def __init__(self, vpn):
        self.vpn = vpn
        self.frame_num = -1
        self.valid = False
        self.dirty = False
        self.last_used = 0
        self.load_time = 0

class MemoryManager:
    def __init__(self, num_frames, page_size, algorithm="LRU"):
        self.num_frames = num_frames
        self.page_size = page_size
        self.algorithm = algorithm
        self.frames = [-1] * num_frames
        self.free_frames = list(range(num_frames))
        self.page_table = {}
        self.swap_space = set()
        self.page_faults = 0
        self.total_accesses = 0
        self.access_history = []
        self.fifo_queue = []
        self.lru_order = OrderedDict()
        
    def access_memory(self, vpn, write=False):
        self.total_accesses += 1
        page_fault = False
        
        if vpn not in self.page_table:
            self.page_table[vpn] = PageTableEntry(vpn)
            
        pte = self.page_table[vpn]
        
        if not pte.valid:
            page_fault = True
            self.page_faults += 1
            self.handle_page_fault(vpn, pte)
            
        if self.algorithm == "LRU":
            if vpn in self.lru_order:
                self.lru_order.move_to_end(vpn)
            else:
                self.lru_order[vpn] = None
                
        physical_address = pte.frame_num * self.page_size
        
        if write:
            pte.dirty = True
            
        self.access_history.append(1 if page_fault else 0)
        return physical_address, page_fault
    
    def handle_page_fault(self, vpn, pte):
        if self.free_frames:
            frame_num = self.free_frames.pop(0)
            self.allocate_frame(vpn, pte, frame_num)
        else:
            self.evict_page(vpn, pte)
            
    def allocate_frame(self, vpn, pte, frame_num):
        pte.frame_num = frame_num
        pte.valid = True
        pte.load_time = time.time()
        self.frames[frame_num] = vpn
        
        if self.algorithm == "FIFO":
            self.fifo_queue.append(vpn)
        elif self.algorithm == "LRU":
            self.lru_order[vpn] = None
            
        if vpn in self.swap_space:
            self.swap_space.remove(vpn)
            
    def evict_page(self, new_vpn, new_pte):
        if self.algorithm == "FIFO":
            victim_vpn = self.fifo_queue.pop(0)
        elif self.algorithm == "LRU":
            victim_vpn = next(iter(self.lru_order))
            del self.lru_order[victim_vpn]
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
            
        victim_pte = self.page_table[victim_vpn]
        frame_num = victim_pte.frame_num
        
        if victim_pte.dirty:
            self.swap_space.add(victim_vpn)
            
        victim_pte.valid = False
        victim_pte.frame_num = -1
        self.frames[frame_num] = -1
        
        self.allocate_frame(new_vpn, new_pte, frame_num)
        
    def get_statistics(self):
        hit_ratio = (self.total_accesses - self.page_faults) / self.total_accesses if self.total_accesses > 0 else 0
        return {
            "total_accesses": self.total_accesses,
            "page_faults": self.page_faults,
            "hit_ratio": hit_ratio,
            "frames_used": self.num_frames - len(self.free_frames),
            "swap_used": len(self.swap_space)
        }
    
    def reset(self):
        self.__init__(self.num_frames, self.page_size, self.algorithm)

def visualize_memory_frames(memory_manager):
    num_frames = memory_manager.num_frames
    frames = memory_manager.frames
    
    cols = min(8, num_frames)
    rows = (num_frames + cols - 1) // cols
    
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    
    for i, frame_content in enumerate(frames):
        row = i // cols
        col = i % cols
        x = col + 0.1
        y = rows - row - 0.1
        
        if frame_content == -1:
            color = 'lightgray'
            text = 'Free'
        else:
            color = 'lightblue'
            text = f'VPN {frame_content}'
            
        rect = plt.Rectangle((x, y), 0.8, 0.8, facecolor=color, edgecolor='black')
        ax.add_patch(rect)
        ax.text(x + 0.4, y + 0.4, text, ha='center', va='center', fontsize=8)
        
    ax.set_title(f'Physical Memory Frames ({num_frames} frames, {memory_manager.page_size} bytes/page)')
    ax.axis('off')
    return fig

def visualize_page_table(memory_manager):
    data = []
    for vpn, pte in memory_manager.page_table.items():
        data.append({
            "VPN": vpn,
            "Frame": pte.frame_num if pte.valid else "Disk",
            "Valid": "✓" if pte.valid else "✗",
            "Dirty": "✓" if pte.dirty else "✗"
        })
    
    if not data:
        data = [{"VPN": "-", "Frame": "-", "Valid": "-", "Dirty": "-"}]
    
    return pd.DataFrame(data)

def plot_page_faults(memory_manager):
    if not memory_manager.access_history:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 3))
    
    window = min(10, len(memory_manager.access_history))
    if window > 0:
        rolling_avg = np.convolve(memory_manager.access_history, 
                                  np.ones(window)/window, mode='valid')
        ax.plot(rolling_avg, 'b-', label=f'{window}-access rolling avg', alpha=0.7)
    
    faults = [i for i, val in enumerate(memory_manager.access_history) if val == 1]
    ax.scatter(faults, [1]*len(faults), c='red', s=20, alpha=0.6, label='Page Faults')
    
    ax.set_xlabel('Access Number')
    ax.set_ylabel('Page Fault')
    ax.set_title('Page Faults Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig

st.set_page_config(page_title="NUMA Memory Management Simulator", layout="wide")

st.title("🖥️ NUMA Memory Management Simulator")
st.markdown("### Visualizing Paging, Virtual Memory & Page Replacement Algorithms")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    memory_size = st.number_input("Physical Memory Size (KB)", min_value=16, max_value=1024, value=64, step=16)
    page_size = st.selectbox("Page Size (KB)", [1, 2, 4, 8], index=2)
    num_frames = memory_size // page_size
    
    st.info(f"**Total Frames:** {num_frames} (each {page_size} KB)")
    
    algorithm = st.selectbox("Page Replacement Algorithm", ["LRU", "FIFO"])
    
    st.header("📝 Reference String")
    reference_input = st.text_area(
        "Enter page numbers (comma or space separated)",
        value="7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1",
        help="Example: 7,0,1,2,0,3,0,4 or 7 0 1 2 0 3 0 4"
    )
    
    reference_string = []
    for token in reference_input.replace(',', ' ').split():
        try:
            reference_string.append(int(token))
        except:
            pass
    
    st.caption(f"**Length:** {len(reference_string)} references")
    
    col1, col2 = st.columns(2)
    with col1:
        run_button = st.button("▶️ Run Simulation", type="primary", use_container_width=True)
    with col2:
        reset_button = st.button("🔄 Reset", use_container_width=True)

if 'memory_manager' not in st.session_state or reset_button:
    st.session_state.memory_manager = MemoryManager(num_frames, page_size * 1024, algorithm)
    st.session_state.current_step = 0
    st.session_state.step_results = []

if run_button:
    st.session_state.memory_manager = MemoryManager(num_frames, page_size * 1024, algorithm)
    st.session_state.current_step = 0
    st.session_state.step_results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, vpn in enumerate(reference_string):
        status_text.text(f"Processing reference {i+1}/{len(reference_string)}: VPN {vpn}")
        physical_addr, fault = st.session_state.memory_manager.access_memory(vpn)
        st.session_state.step_results.append((vpn, physical_addr, fault))
        progress_bar.progress((i + 1) / len(reference_string))
    
    status_text.text("✅ Simulation complete!")
    time.sleep(0.5)
    status_text.empty()
    progress_bar.empty()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Simulation Results", "💾 Memory View", "📋 Page Table", "📈 Performance Analysis"])

with tab1:
    if st.session_state.step_results:
        stats = st.session_state.memory_manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Memory References", stats["total_accesses"])
        with col2:
            st.metric("Page Faults", stats["page_faults"], delta=f"{stats['page_faults']/stats['total_accesses']*100:.1f}%")
        with col3:
            st.metric("Hit Ratio", f"{stats['hit_ratio']*100:.1f}%")
        with col4:
            st.metric("Frames Used", f"{stats['frames_used']}/{st.session_state.memory_manager.num_frames}")
        
        st.subheader("Step-by-Step Execution")
        
        results_df = pd.DataFrame(st.session_state.step_results, 
                                  columns=["VPN", "Physical Address", "Page Fault"])
        results_df["Page Fault"] = results_df["Page Fault"].apply(lambda x: "⚠️ Fault" if x else "✓ Hit")
        
        st.dataframe(results_df, use_container_width=True)
        
        st.subheader("Step Through Simulation")
        step_index = st.slider("Step", 0, len(st.session_state.step_results)-1, 0, 
                               key="step_slider")
        
        if step_index < len(st.session_state.step_results):
            vpn, phys_addr, fault = st.session_state.step_results[step_index]
            st.info(f"**Step {step_index + 1}:** Accessing VPN {vpn} → {'Page Fault!' if fault else 'Page Hit!'} → Physical Address: {phys_addr}")
    else:
        st.info("Click 'Run Simulation' to start. The reference string will be processed and results shown here.")

with tab2:
    if st.session_state.memory_manager.total_accesses > 0:
        fig1 = visualize_memory_frames(st.session_state.memory_manager)
        st.pyplot(fig1)
        
        st.subheader("Frame Details")
        frame_data = []
        for i, vpn in enumerate(st.session_state.memory_manager.frames):
            frame_data.append({
                "Frame Number": i,
                "VPN": vpn if vpn != -1 else "Free",
                "Status": "Occupied" if vpn != -1 else "Free"
            })
        st.dataframe(pd.DataFrame(frame_data), use_container_width=True)
    else:
        st.info("Run simulation to see memory frame visualization.")

with tab3:
    if st.session_state.memory_manager.total_accesses > 0:
        st.subheader("Page Table")
        page_table_df = visualize_page_table(st.session_state.memory_manager)
        st.dataframe(page_table_df, use_container_width=True)
        
        st.subheader("Swap Space")
        if st.session_state.memory_manager.swap_space:
            st.write(f"Pages on disk: {sorted(st.session_state.memory_manager.swap_space)}")
        else:
            st.write("No pages swapped out yet.")
    else:
        st.info("Run simulation to see page table contents.")

with tab4:
    if st.session_state.memory_manager.total_accesses > 0:
        fig2 = plot_page_faults(st.session_state.memory_manager)
        if fig2:
            st.pyplot(fig2)
        
        st.subheader("Algorithm Comparison")
        st.markdown(f"""
        **Current Algorithm: {algorithm}**
        
        **FIFO (First-In-First-Out):**
        - Simple to implement
        - May suffer from Belady's anomaly
        - Doesn't consider page usage frequency
        
        **LRU (Least Recently Used):**
        - Better performance than FIFO in practice
        - Uses temporal locality
        - More overhead to track usage history
        - No Belady's anomaly
        
        **Your Results:**
        - Hit Ratio: {st.session_state.memory_manager.get_statistics()['hit_ratio']*100:.1f}%
        - Page Faults: {st.session_state.memory_manager.get_statistics()['page_faults']}
        """)
    else:
        st.info("Run simulation to see performance analysis.")

st.markdown("---")
st.markdown("""
### 📖 How to Use:
1. **Configure** memory size, page size, and replacement algorithm in the sidebar
2. **Enter a reference string** (page numbers to access)
3. **Click 'Run Simulation'** to process all references
4. **Explore tabs** to see memory visualization, page table, and performance metrics
5. **Use the step slider** to see individual memory accesses

### 🧪 Example Reference Strings:
- **Small:** `7,0,1,2,0,3,0,4`
- **Medium:** `7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7,0,1`
- **Large:** `1,2,3,4,1,2,5,1,2,3,4,5,1,2,3,4,5,6,1,2,3,4,5,6`
""")