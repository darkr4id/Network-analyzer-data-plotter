import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class SAWFilterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SAW Filter Plotter")
        self.geometry("1000x600")

        # Main frames
        params = ttk.LabelFrame(self, text="Filter Parameters")
        params.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        opts = ttk.LabelFrame(self, text="Plot Options")
        opts.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=10)

        # Center frequency
        ttk.Label(params, text="Center Frequency (MHz):").grid(row=0, column=0, sticky=tk.W)
        self.f0_var = tk.DoubleVar(value=100)
        ttk.Entry(params, textvariable=self.f0_var).grid(row=0, column=1)

        # Number of fingers (physical)
        ttk.Label(params, text="Number of Fingers:").grid(row=1, column=0, sticky=tk.W)
        self.n_var = tk.IntVar(value=50)
        ttk.Entry(params, textvariable=self.n_var).grid(row=1, column=1)

        # Span
        ttk.Label(params, text="Span (fraction):").grid(row=2, column=0, sticky=tk.W)
        self.span_var = tk.DoubleVar(value=0.5)
        ttk.Entry(params, textvariable=self.span_var).grid(row=2, column=1)

        # Wavelength and Delay
        ttk.Label(params, text="Wavelength (µm):").grid(row=3, column=0, sticky=tk.W)
        self.lambda_var = tk.DoubleVar(value=48.8)
        ttk.Entry(params, textvariable=self.lambda_var).grid(row=3, column=1)
        ttk.Label(params, text="Delay Time (ms):").grid(row=4, column=0, sticky=tk.W)
        self.delay_var = tk.DoubleVar(value=0.7)
        ttk.Entry(params, textvariable=self.delay_var).grid(row=4, column=1)

        # Zero-bandwidth marker
        ttk.Label(params, text="Zero BW (MHz):").grid(row=5, column=0, sticky=tk.W)
        self.zerobw_var = tk.DoubleVar(value=0)
        ttk.Entry(params, textvariable=self.zerobw_var).grid(row=5, column=1)

        # dB scale
        ttk.Label(params, text="Scale:").grid(row=6, column=0, sticky=tk.W)
        self.scale_var = tk.StringVar(value='negative')
        ttk.Combobox(params, textvariable=self.scale_var,
                     values=['negative','positive'], state='readonly').grid(row=6, column=1)

        # Axis ranges
        ttk.Label(params, text="X Range (MHz):").grid(row=7, column=0, sticky=tk.W)
        self.xmin_var = tk.DoubleVar(value=0)
        self.xmax_var = tk.DoubleVar(value=0)
        ttk.Entry(params, textvariable=self.xmin_var, width=8).grid(row=7, column=1, sticky=tk.W)
        ttk.Entry(params, textvariable=self.xmax_var, width=8).grid(row=7, column=1, sticky=tk.E)

        ttk.Label(params, text="Y Range (dB):").grid(row=8, column=0, sticky=tk.W)
        self.ymin_var = tk.DoubleVar(value=0)
        self.ymax_var = tk.DoubleVar(value=0)
        ttk.Entry(params, textvariable=self.ymin_var, width=8).grid(row=8, column=1, sticky=tk.W)
        ttk.Entry(params, textvariable=self.ymax_var, width=8).grid(row=8, column=1, sticky=tk.E)

        # Plot title input
        ttk.Label(opts, text="Chart Title:").pack(anchor=tk.W, pady=(10,0))
        self.title_var = tk.StringVar(value="")
        ttk.Entry(opts, textvariable=self.title_var).pack(fill=tk.X, pady=(0,10))

        # Legend labels input
        ttk.Label(opts, text="Legend Labels (comma-separated):").pack(anchor=tk.W)
        self.legend_var = tk.StringVar(value="")
        ttk.Entry(opts, textvariable=self.legend_var).pack(fill=tk.X, pady=(0,10))

        # Plot options
        self.show_theo = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts, text="Theoretical", variable=self.show_theo).pack(anchor=tk.W)
        self.show_csv = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts, text="CSV Data", variable=self.show_csv).pack(anchor=tk.W)
        ttk.Button(opts, text="Load CSV...", command=self.load_csv).pack(pady=5)
        self.csv_list = tk.Listbox(opts, selectmode=tk.MULTIPLE, height=5)
        self.csv_list.pack(fill=tk.X)
        self.csv_info = {}

        # Control buttons
        ttk.Button(btn_frame, text="Plot", command=self.draw_plot).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_plot).pack(side=tk.LEFT, padx=5, pady=5)

        # Figure
        self.fig = Figure(figsize=(6,5))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def load_csv(self):
        files = filedialog.askopenfilenames(filetypes=[('CSV files','*.csv')])
        for f in files:
            try:
                df = pd.read_csv(f, header=2)
                if not any('freq' in c.lower() for c in df.columns):
                    df = pd.read_csv(f, header=0)
                df.columns = [c.strip() for c in df.columns]
                cols = list(df.columns)
                freq_cols = [c for c in cols if 'freq' in c.lower()]
                freq_col = freq_cols[0] if freq_cols else cols[0]
                amp_cols = [c for c in cols if c != freq_col]
                if not amp_cols:
                    raise ValueError("No amplitude column")
                name = os.path.basename(f)
                self.csv_info[name] = {'df': df, 'freq_col': freq_col, 'amp_cols': amp_cols}
                if name not in self.csv_list.get(0, tk.END):
                    self.csv_list.insert(tk.END, name)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {os.path.basename(f)}: {e}")

    def draw_plot(self):
        self.ax.clear()
        handles = []

        # Theoretical (split-finger) response
        if self.show_theo.get():
            f0 = self.f0_var.get() * 1e6
            N_pairs = self.n_var.get() / 2.0
            span = self.span_var.get()

            f = np.linspace(f0*(1-span), f0*(1+span), 1000)
            x = N_pairs * np.pi * (f - f0) / f0
            H0 = np.sinc(x/np.pi)
            delta_f = span * f0
            mod = np.cos(0.5 * np.pi * (f - f0) / delta_f)
            H = H0 * mod

            if self.scale_var.get() == 'negative':
                dB = 20 * np.log10(np.abs(H) + 1e-12)
            else:
                dB = -20 * np.log10(np.abs(H) + 1e-12)

            line, = self.ax.plot(f/1e6, dB, label='Theoretical (split-finger)')
            handles.append(line)

            # zero-BW markers
            bw0 = self.zerobw_var.get()
            if bw0 > 0:
                f0_mhz = f0 / 1e6
                l1 = self.ax.axvline(f0_mhz - bw0/2, linestyle='--', label='BW start')
                l2 = self.ax.axvline(f0_mhz + bw0/2, linestyle='--', label='BW end')
                handles += [l1, l2]

            # annotate λ & τ
            self.ax.text(0.05, 0.95,
                         f"λ={self.lambda_var.get():.1f} µm, τ={self.delay_var.get():.2f} ms",
                         transform=self.ax.transAxes, va='top')

        # CSV data
        if self.show_csv.get():
            for idx in self.csv_list.curselection():
                name = self.csv_list.get(idx)
                info = self.csv_info[name]
                df = info['df']
                freq_mhz = df[info['freq_col']].astype(float) / 1e6
                for col in info['amp_cols']:
                    line, = self.ax.plot(freq_mhz, df[col], label=f"{name}:{col}")
                    handles.append(line)

        # always draw center-frequency marker
        f0_mhz = self.f0_var.get()
        vline = self.ax.axvline(f0_mhz, color='gray', linestyle=':', label='Center f₀')
        handles.append(vline)

        # axes labels & limits
        xmin, xmax = self.xmin_var.get(), self.xmax_var.get()
        if xmin < xmax:
            self.ax.set_xlim(xmin, xmax)
        ymin, ymax = self.ymin_var.get(), self.ymax_var.get()
        if ymin < ymax:
            self.ax.set_ylim(ymin, ymax)

        self.ax.set_xlabel('Frequency (MHz)')
        ylabel = 'Amplitude (dB)' if self.scale_var.get()=='negative' else 'Insertion Loss (dB)'
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)

        # chart title
        title = self.title_var.get().strip()
        if title:
            self.ax.set_title(title)

        # custom legend
        custom = [lbl.strip() for lbl in self.legend_var.get().split(',') if lbl.strip()]
        if custom and len(custom) == len(handles):
            self.ax.legend(handles, custom)
        else:
            self.ax.legend()

        self.canvas.draw()

    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlabel('Frequency (MHz)')
        ylabel = 'Amplitude (dB)' if self.scale_var.get()=='negative' else 'Insertion Loss (dB)'
        self.ax.set_ylabel(ylabel)
        self.ax.grid(True)
        self.canvas.draw()

if __name__ == '__main__':
    app = SAWFilterGUI()
    app.mainloop()
