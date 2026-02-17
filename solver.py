from data_models import MaterialOrder
from typing import List


class UsedBar:
    def __init__(self, total_length: int):
        self.total_length = total_length
        self.cuts = []
        self.remainder = total_length


class CuttingResult:
    def __init__(self):
        self.bars: List[UsedBar] = []
        self.total_waste_mm = 0
        self.cutting_instructions = []

def calculate_cutting_plan(order: MaterialOrder, kerf_width_mm: int) -> CuttingResult:
    all_cuts = []
    for item in order.pieces:
        for _ in range(item.count):
            all_cuts.append(item.length_mm)

    all_cuts.sort(reverse=True)

    # Safety check: If AI returned empty list of lengths (shouldn't happen due to prompt, but just in case)
    if not order.stock_lengths_mm:
        stock_lengths = [6000]
    else:
        stock_lengths = sorted(order.stock_lengths_mm)

    used_bars: List[UsedBar] = []

    for cut in all_cuts:
        placed = False

        # A) First Fit on used bars
        for bar in used_bars:
            needed_space = cut
            if len(bar.cuts) > 0:
                needed_space += kerf_width_mm  # Use argument

            if bar.remainder >= needed_space:
                bar.cuts.append(cut)
                bar.remainder -= needed_space
                placed = True
                break

        # B) Best Fit on new bars
        if not placed:
            selected_length = None
            for stock_length in stock_lengths:
                if stock_length >= cut:
                    selected_length = stock_length
                    break

            if selected_length:
                new_bar = UsedBar(selected_length)
                new_bar.cuts.append(cut)
                new_bar.remainder -= cut
                used_bars.append(new_bar)
            else:
                pass  # Doesn't fit even on the largest bar

    result = CuttingResult()
    result.bars = used_bars
    result.total_waste_mm = sum(b.remainder for b in used_bars)

    for i, bar in enumerate(used_bars):
        stock = bar.total_length
        remainder = bar.remainder
        utilization_percent = ((stock - remainder) / stock) * 100

        cut_count = max(0, len(bar.cuts) - 1)
        total_kerf = cut_count * kerf_width_mm

        description = f"Bar {i + 1} ({stock}mm): {bar.cuts} | Kerf: {total_kerf}mm | Remainder: {remainder}mm"
        result.cutting_instructions.append((description, utilization_percent))

    return result