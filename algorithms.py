from collections import deque


def fifo_steps(pages, capacity):
    memory = []
    queue = deque()
    steps = []
    faults = 0

    for page in pages:
        hit = page in memory
        if not hit:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
                queue.append(page)
            else:
                removed = queue.popleft()
                memory.remove(removed)
                memory.append(page)
                queue.append(page)
        steps.append((page, memory.copy(), "Hit" if hit else "Fault"))

    return steps, faults


def lru_steps(pages, capacity):
    memory = []
    steps = []
    faults = 0

    for i, page in enumerate(pages):
        hit = page in memory

        if not hit:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                lru_page = min(
                    memory,
                    key=lambda p: max(j for j in range(i) if pages[j] == p)
                )
                memory.remove(lru_page)
                memory.append(page)
        else:
            memory.remove(page)
            memory.append(page)

        steps.append((page, memory.copy(), "Hit" if hit else "Fault"))

    return steps, faults


def optimal_steps(pages, capacity):
    """Optimal (OPT) page replacement - evicts page used furthest in future."""
    memory = []
    steps = []
    faults = 0

    for i, page in enumerate(pages):
        hit = page in memory

        if not hit:
            faults += 1
            if len(memory) < capacity:
                memory.append(page)
            else:
                future_use = {}
                for p in memory:
                    future = [j for j in range(i + 1, len(pages)) if pages[j] == p]
                    future_use[p] = future[0] if future else float('inf')
                evict = max(future_use, key=future_use.get)
                memory.remove(evict)
                memory.append(page)

        steps.append((page, memory.copy(), "Hit" if hit else "Fault"))

    return steps, faults
