import tkinter as tk
import time
import json

class SplitTimerApp:
    def __init__(self, root, splits):
        self.root = root
        self.splits = splits
        self.split_times = [0.0] * len(splits)
        self.current_split = None
        self.start_time = None
        self.total_time = 0.0

        self.labels = []
        self.time_labels = []
        
        self.total_label = tk.Label(root, text="Total: 00:00.0", font=("Arial", 16, "bold"))
        self.total_label.grid(row=0, column=0, columnspan=2, pady=10)

        for i, split in enumerate(splits):
            lbl = tk.Label(root, text=f"{split}:", font=("Arial", 14))
            lbl.grid(row=i+1, column=0, padx=10, pady=5)
            lbl.bind("<Button-1>", lambda e, idx=i: self.switch_split(idx))  # Make label clickable
            
            self.labels.append(lbl)

            time_lbl = tk.Label(root, text="00:00.0", font=("Arial", 14))
            time_lbl.grid(row=i+1, column=1, padx=10, pady=5)
            self.time_labels.append(time_lbl)

        self.next_btn = tk.Button(root, text="Start Split", command=self.next_split, font=("Arial", 14))
        self.next_btn.grid(row=len(splits)+1, column=0, columnspan=2, pady=10)
        
        self.pause_btn = tk.Button(root, text="Pause", command=self.pause_timer, font=("Arial", 14))
        self.pause_btn.grid(row=len(splits)+2, column=0, columnspan=2, pady=5)

        self.update_timer()

    def next_split(self):
        now = time.time()
        if self.start_time is None:
            self.current_split = 0
            self.start_time = now
            self.next_btn.config(text="Split")
        else:
            elapsed = now - self.start_time
            self.split_times[self.current_split] += elapsed  # Use +=
            self.time_labels[self.current_split].config(text=self.format_mmss(self.split_times[self.current_split]))
            self.total_time = sum(self.split_times)
            self.total_label.config(text=f"Total: {self.format_mmss(self.total_time)}")
            self.current_split += 1
            if self.current_split >= len(self.splits):
                self.next_btn.config(state=tk.DISABLED, text="Done")
                self.start_time = None
            else:
                self.start_time = now
                
    def switch_split(self, idx):
        now = time.time()
        if self.current_split is not None and self.start_time is not None:
            # Pause current split
            elapsed = now - self.start_time
            self.split_times[self.current_split] += elapsed
            self.time_labels[self.current_split].config(text=self.format_mmss(self.split_times[self.current_split]))

        # Resume selected split
        self.current_split = idx
        self.start_time = now

    def update_timer(self):
        if self.start_time is not None and self.current_split is not None and self.current_split < len(self.splits):
            elapsed = time.time() - self.start_time + self.split_times[self.current_split]
            self.time_labels[self.current_split].config(text=f"{self.format_mmss(elapsed)} (running)")
            # Calculate running total including current split
            running_total = sum(self.split_times) - self.split_times[self.current_split] + elapsed
            self.total_label.config(text=f"Total: {self.format_mmss(running_total)} (running)")
        else:
            self.total_label.config(text=f"Total: {self.format_mmss(sum(self.split_times))}")
        self.root.after(100, self.update_timer)
        
    def pause_timer(self):
        if self.current_split is not None and self.start_time is not None:
            elapsed = time.time() - self.start_time
            self.split_times[self.current_split] += elapsed
            self.time_labels[self.current_split].config(text=self.format_mmss(self.split_times[self.current_split]))
            self.start_time = None  # Stop timing
    
    def format_mmss(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 10)
        return f"{minutes:02}:{secs:02}.{millis}"

if __name__ == "__main__":
    with open("order.json","r") as f:
        splits_data = json.load(f)
    splits = [split['name'] for split in splits_data['splits']]
    root = tk.Tk()
    root.title(splits_data['name'])
    root.attributes("-topmost", True)  # Keep the window on top
    app = SplitTimerApp(root, splits)
    root.mainloop()