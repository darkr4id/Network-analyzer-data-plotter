import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, StringVar

def load_saw_csv(path, skiprows=3):
    """Load SAW-style CSV, skipping first `skiprows` lines."""
    with open(path, 'r') as f:
        lines = f.readlines()
    data_lines = lines[skiprows:]
    parsed = [ln.strip().strip('"').split(',') for ln in data_lines if ln.strip()]
    df = pd.DataFrame(parsed, columns=['Frequency','dB','Extra'])
    df['Frequency'] = df['Frequency'].astype(float)
    df['dB']        = df['dB'].astype(float)
    df['MHz']       = df['Frequency'] / 1e6
    return df

def plot():
    path = file_path.get()
    if not path:
        return
    df = load_saw_csv(path)
    fig.clear()
    ax = fig.add_subplot(111)
    ax.plot(df['MHz'], df['dB'], color='orange')

    # Title
    title = title_var.get().strip()
    if title:
        ax.set_title(title)

    # Axis labels
    xlabel = xlabel_var.get().strip()
    ylabel = ylabel_var.get().strip()
    ax.set_xlabel(xlabel if xlabel else 'Frequency (MHz)')
    ax.set_ylabel(ylabel if ylabel else 'dB')

    # X limits
    try:
        xmin = float(xmin_var.get())
        xmax = float(xmax_var.get())
        ax.set_xlim(xmin, xmax)
    except ValueError:
        ax.set_xlim(df['MHz'].min(), df['MHz'].max())

    # Y limits
    try:
        ymin = float(ymin_var.get())
        ymax = float(ymax_var.get())
        ax.set_ylim(ymin, ymax)
    except ValueError:
        ax.set_ylim(df['dB'].min(), 0)

    # 0 dB line
    ax.axhline(0, linestyle='--', color='gray', linewidth=1)
    ax.grid(True, which='both', linestyle=':', linewidth=0.5)
    canvas.draw()

def browse_file():
    path = filedialog.askopenfilename(
        filetypes=[("CSV Files","*.csv"),("All files","*.*")])
    if path:
        file_path.set(path)

# Build UI
root = tk.Tk()
root.title("SAW CSV Plotter")

file_path  = StringVar()
title_var  = StringVar()
xlabel_var = StringVar()
ylabel_var = StringVar()
xmin_var   = StringVar()
xmax_var   = StringVar()
ymin_var   = StringVar()
ymax_var   = StringVar()

tk.Label(root, text="CSV File:").grid(row=0, column=0, sticky='e')
tk.Entry(root, textvariable=file_path, width=40).grid(row=0, column=1)
tk.Button(root, text="Browse...", command=browse_file).grid(row=0, column=2)

tk.Label(root, text="Title:").grid(row=1, column=0, sticky='e')
tk.Entry(root, textvariable=title_var, width=40).grid(row=1, column=1, columnspan=2)

tk.Label(root, text="X Label:").grid(row=2, column=0, sticky='e')
tk.Entry(root, textvariable=xlabel_var, width=20).grid(row=2, column=1, sticky='w')
tk.Label(root, text="Y Label:").grid(row=2, column=2, sticky='e')
tk.Entry(root, textvariable=ylabel_var, width=20).grid(row=2, column=3, sticky='w')

tk.Label(root, text="X Min (MHz):").grid(row=3, column=0, sticky='e')
tk.Entry(root, textvariable=xmin_var, width=10).grid(row=3, column=1, sticky='w')
tk.Label(root, text="X Max (MHz):").grid(row=3, column=2, sticky='e')
tk.Entry(root, textvariable=xmax_var, width=10).grid(row=3, column=3, sticky='w')

tk.Label(root, text="Y Min (dB):").grid(row=4, column=0, sticky='e')
tk.Entry(root, textvariable=ymin_var, width=10).grid(row=4, column=1, sticky='w')
tk.Label(root, text="Y Max (dB):").grid(row=4, column=2, sticky='e')
tk.Entry(root, textvariable=ymax_var, width=10).grid(row=4, column=3, sticky='w')

tk.Button(root, text="Plot", command=plot).grid(row=5, column=0, columnspan=4, pady=5)

# Matplotlib figure embedded in Tk
fig = Figure(figsize=(8,5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=6, column=0, columnspan=4)

root.mainloop()
