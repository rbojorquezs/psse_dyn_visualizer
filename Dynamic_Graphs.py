# DynTools and Matplotlib Graphs.py
# Ing. José Roberto Bojórquez Sánchez

# Este script permite cargar archivos .out de PSSE y extraer datos utilizando la biblioteca DyTools.
# Se utiliza Tkinter para crear una interfaz gráfica simple que permite al usuario seleccionar un archivo .out.
# El script muestra los datos de la simulación dinamica en gráficos utilizando Matplotlib.
# Se desarrolla una ventana para la personalizacion completa de la gráfica, incluyendo la selección de variables y el rango de tiempo.
# Requiere la instalación de las bibliotecas DyTools y Matplotlib. (Ver archivo requirements.txt)

# Importar las bibliotecas necesarias
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import OrderedDict
from tkinter import font as tkFont

# Initialize PSSE V_36
pssepy_PATH = r"C:\Program Files\PTI\PSSE36\36.1\PSSPY311"
sys.path.append(pssepy_PATH)
import psse36  # type: ignore
import psspy  # type: ignore
psspy.psseinit()
import dyntools # type: ignore

class DynamicGraphApp:

    def __init__(self, root):
        self.root = root
        self.root.title("PSSE Dynamic Simulation Grapher")
        self.root.geometry("1000x700")
        
        # Data variables
        self.chnfobj = None
        self.chanid = OrderedDict()
        self.chandata = {}
        self.y_vars = []  # Stores multiple Y variables
        self.y_combos = []  # Stores combo boxes for Y variables
        self.line_colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # Colors for multiple lines
        
        # Initialize font list
        try:
            self.fonts = sorted(list(tkFont.families()))
        except:
            # Fallback fonts if system fonts can't be retrieved
            self.fonts = ['Arial', 'Times New Roman', 'Courier New', 'Verdana', 'Helvetica']

        
        # Default plot settings
        self.plot_settings = {
            'title': "Dynamic Simulation Results",
            'xlabel': "",
            'ylabel': "Value",
            'xlim_min': "",
            'xlim_max': "",
            'ylim_min': "",
            'ylim_max': "",
            'font_family': "Arial",
            'font_size': 10,
            'grid': True
        }

        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File section
        file_frame = ttk.LabelFrame(main_frame, text="Output File", padding="10")
        file_frame.pack(fill=tk.X, pady=5)
        
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(file_frame, text="Load .out File", command=self.load_file).pack(side=tk.RIGHT, padx=5)
        
        # Split main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Variable selection (40% width)
        left_frame = ttk.Frame(content_frame, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Right panel - Plot customization (60% width)
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Variable selection section
        var_frame = ttk.LabelFrame(left_frame, text="Variable Selection", padding="10")
        var_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        
        # X variable selection
        ttk.Label(var_frame, text="X-axis Variable:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.combo_x = ttk.Combobox(var_frame, state="readonly", width=30)
        self.combo_x.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Y variables section
        self.y_frame = ttk.Frame(var_frame)
        self.y_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Default Y variable
        self.add_y_variable()
        
        # Button to add more Y variables
        ttk.Button(var_frame, text="Add Y Variable", command=self.add_y_variable).grid(row=2, column=1, sticky=tk.E, pady=5)
        
        # Plot customization section
        custom_frame = ttk.LabelFrame(right_frame, text="Plot Customization", padding="10")
        custom_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        
        # Plot title
        ttk.Label(custom_frame, text="Title:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.title_entry = ttk.Entry(custom_frame)
        self.title_entry.insert(0, self.plot_settings['title'])
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        
        # X-axis label
        ttk.Label(custom_frame, text="X-axis Label:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.xlabel_entry = ttk.Entry(custom_frame)
        self.xlabel_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        
        # Y-axis label
        ttk.Label(custom_frame, text="Y-axis Label:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.ylabel_entry = ttk.Entry(custom_frame)
        self.ylabel_entry.insert(0, self.plot_settings['ylabel'])
        self.ylabel_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.EW)
        
        # X-axis limits
        ttk.Label(custom_frame, text="X-axis Limits:").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        limit_frame = ttk.Frame(custom_frame)
        limit_frame.grid(row=3, column=1, sticky=tk.EW)
        
        ttk.Label(limit_frame, text="Min:").pack(side=tk.LEFT)
        self.xlim_min_entry = ttk.Entry(limit_frame, width=8)
        self.xlim_min_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(limit_frame, text="Max:").pack(side=tk.LEFT)
        self.xlim_max_entry = ttk.Entry(limit_frame, width=8)
        self.xlim_max_entry.pack(side=tk.LEFT, padx=2)
        
        # Y-axis limits
        ttk.Label(custom_frame, text="Y-axis Limits:").grid(row=4, column=0, padx=5, pady=2, sticky=tk.W)
        ylimit_frame = ttk.Frame(custom_frame)
        ylimit_frame.grid(row=4, column=1, sticky=tk.EW)
        
        ttk.Label(ylimit_frame, text="Min:").pack(side=tk.LEFT)
        self.ylim_min_entry = ttk.Entry(ylimit_frame, width=8)
        self.ylim_min_entry.pack(side=tk.LEFT, padx=2)
        
        ttk.Label(ylimit_frame, text="Max:").pack(side=tk.LEFT)
        self.ylim_max_entry = ttk.Entry(ylimit_frame, width=8)
        self.ylim_max_entry.pack(side=tk.LEFT, padx=2)
        
        # Font selection
        ttk.Label(custom_frame, text="Font Family:").grid(row=5, column=0, padx=5, pady=2, sticky=tk.W)
        self.font_combo = ttk.Combobox(custom_frame, values=self.fonts, state="readonly")
        self.font_combo.set(self.plot_settings['font_family'])
        self.font_combo.grid(row=5, column=1, padx=5, pady=2, sticky=tk.EW)
        
        ttk.Label(custom_frame, text="Font Size:").grid(row=6, column=0, padx=5, pady=2, sticky=tk.W)
        self.font_size_entry = ttk.Entry(custom_frame, width=8)
        self.font_size_entry.insert(0, str(self.plot_settings['font_size']))
        self.font_size_entry.grid(row=6, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Grid checkbox
        self.grid_var = tk.BooleanVar(value=self.plot_settings['grid'])
        ttk.Checkbutton(custom_frame, text="Show Grid", variable=self.grid_var).grid(row=7, column=0, columnspan=2, sticky=tk.W)
        
        # Plot button
        ttk.Button(right_frame, text="Generate Plot", command=self.generate_plot).pack(pady=10)
        
        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Configure grid expansion
        var_frame.columnconfigure(1, weight=1)
        custom_frame.columnconfigure(1, weight=1)

    def load_file(self):
        outfile = filedialog.askopenfilename(filetypes=[("PSSE Output Files", "*.out")])
        if outfile:
            try:
                self.chnfobj = dyntools.CHNF(outfile)
                short_title, chanid_dict, self.chandata = self.chnfobj.get_data()
                
                # Store channel information (excluding time since we handle it separately)
                self.chanid = OrderedDict()
                for chan_num, chan_desc in chanid_dict.items():
                    # Skip if this is the time channel (often has specific numbering)
                    if not chan_desc.lower().startswith('time'):
                        self.chanid[chan_num] = f"{chan_num}: {chan_desc}"
                    
                self.file_label.config(text=f"File: {outfile}")
                self.update_comboboxes()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
    
    def update_comboboxes(self):
        # Create list of available variables (just 'time' and our channels)
        variables = ["time"] + list(self.chanid.values())
        
        # Update X-axis combobox
        self.combo_x['values'] = variables
        if variables:
            self.combo_x.current(0)  # Select 'time' by default
        
        # Update all Y-axis comboboxes
        for combo in self.y_combos:
            combo['values'] = variables
            if variables:
                # Select first channel (skip 'time' for Y unless it's the only option)
                if len(variables) > 1:
                    combo.current(1)
                else:
                    combo.current(0)
    
    def add_y_variable(self):
        # Create new Y variable selection
        frame = ttk.Frame(self.y_frame)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=f"Y-axis Variable {len(self.y_combos)+1}:").pack(side=tk.LEFT, padx=5)
        
        combo = ttk.Combobox(frame, state="readonly", width=40)
        combo.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Add delete button
        ttk.Button(frame, text="×", width=2, 
                  command=lambda c=combo: self.remove_y_variable(c)).pack(side=tk.RIGHT, padx=5)
        
        # Initialize if we have data
        if self.chanid:
            combo['values'] = list(self.chanid.values())
            # Select next available channel
            combo.current(len(self.y_combos)+1 if len(self.y_combos)+1 < len(self.chanid) else 0)
        
        self.y_combos.append(combo)
    
    def remove_y_variable(self, combo):
        if len(self.y_combos) <= 1:
            messagebox.showwarning("Warning", "You need at least one Y variable")
            return
            
        idx = self.y_combos.index(combo)
        self.y_combos.pop(idx)
        combo.master.destroy()  # Destroy the containing frame
    
    def generate_plot(self):
        # Get selected X variable
        x_selection = self.combo_x.get()
        if not x_selection:
            messagebox.showerror("Error", "Please select an X-axis variable")
            return
        
        # Get selected Y variables
        y_selections = []
        for combo in self.y_combos:
            selection = combo.get()
            if selection:
                y_selections.append(selection)
        
        if not y_selections:
            messagebox.showerror("Error", "Please select at least one Y-axis variable")
            return
        
        try:
            # Clear previous plot
            self.ax.clear()
            
            # Initialize min/max trackers
            x_min, x_max = float('inf'), float('-inf')
            y_min, y_max = float('inf'), float('-inf')
            
            # Get X-axis data
            if x_selection == "time":
                x_data = self.chandata['time']
                x_label = "Time (seconds)"
            else:
                x_chan = int(x_selection.split(':')[0])
                x_data = self.chandata.get(x_chan)
                x_label = x_selection.split(': ')[1] if ': ' in x_selection else x_selection
            
            if x_data is None:
                messagebox.showerror("Error", f"Data not available for X variable: {x_selection}")
                return
            
            # Update x limits
            x_min, x_max = min(x_data), max(x_data)
            
            # Plot each Y variable and track y limits
            for i, y_sel in enumerate(y_selections):
                if y_sel == "time":
                    y_data = self.chandata['time']
                    y_label = "Time (seconds)"
                else:
                    y_chan = int(y_sel.split(':')[0])
                    y_data = self.chandata.get(y_chan)
                    y_label = y_sel.split(': ')[1] if ': ' in y_sel else y_sel
                
                if y_data is None:
                    messagebox.showerror("Error", f"Data not available for Y variable: {y_sel}")
                    return
                
                # Update y limits
                y_min = min(y_min, min(y_data))
                y_max = max(y_max, max(y_data))
                
                color = self.line_colors[i % len(self.line_colors)]
                self.ax.plot(x_data, y_data, color=color, label=y_label)
            
            # Set default axis limits with 5% padding
            x_padding = (x_max - x_min) * 0.05
            y_padding = (y_max - y_min) * 0.05
            
            self.ax.set_xlim(x_min - x_padding, x_max + x_padding)
            self.ax.set_ylim(y_min - y_padding, y_max + y_padding)
            
            # Update limit entry fields with calculated values
            self.xlim_min_entry.delete(0, tk.END)
            self.xlim_min_entry.insert(0, f"{x_min - x_padding:.2f}")
            self.xlim_max_entry.delete(0, tk.END)
            self.xlim_max_entry.insert(0, f"{x_max + x_padding:.2f}")
            
            self.ylim_min_entry.delete(0, tk.END)
            self.ylim_min_entry.insert(0, f"{y_min - y_padding:.2f}")
            self.ylim_max_entry.delete(0, tk.END)
            self.ylim_max_entry.insert(0, f"{y_max + y_padding:.2f}")
            
            # Apply plot settings (title, labels, fonts etc.)
            self.apply_plot_settings(x_label)
            
            # Redraw canvas
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot:\n{str(e)}")

    def apply_plot_settings(self, x_label):
        """Apply all the plot customization settings"""
        # Get plot settings from UI
        self.plot_settings = {
            'title': self.title_entry.get(),
            'xlabel': self.xlabel_entry.get(),
            'ylabel': self.ylabel_entry.get(),
            'xlim_min': self.xlim_min_entry.get(),
            'xlim_max': self.xlim_max_entry.get(),
            'ylim_min': self.ylim_min_entry.get(),
            'ylim_max': self.ylim_max_entry.get(),
            'font_family': self.font_combo.get(),
            'font_size': int(self.font_size_entry.get()),
            'grid': self.grid_var.get()
        }
        
        # Apply title and labels
        self.ax.set_title(self.plot_settings['title'], 
                        fontfamily=self.plot_settings['font_family'],
                        fontsize=self.plot_settings['font_size'])
        
        xlabel = self.plot_settings['xlabel'] if self.plot_settings['xlabel'] else x_label
        self.ax.set_xlabel(xlabel,
                        fontfamily=self.plot_settings['font_family'],
                        fontsize=self.plot_settings['font_size'])
        
        self.ax.set_ylabel(self.plot_settings['ylabel'],
                        fontfamily=self.plot_settings['font_family'],
                        fontsize=self.plot_settings['font_size'])
        
        # Apply custom limits if they're specified and valid
        try:
            if self.plot_settings['xlim_min'] and self.plot_settings['xlim_max']:
                self.ax.set_xlim(float(self.plot_settings['xlim_min']), 
                                float(self.plot_settings['xlim_max']))
            if self.plot_settings['ylim_min'] and self.plot_settings['ylim_max']:
                self.ax.set_ylim(float(self.plot_settings['ylim_min']), 
                                float(self.plot_settings['ylim_max']))
        except ValueError:
            pass  # Keep auto-scaled limits if custom ones are invalid
        
        # Set grid
        self.ax.grid(self.plot_settings['grid'])
        
        # Apply font to all text elements
        for item in ([self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label] +
                    self.ax.get_xticklabels() + self.ax.get_yticklabels()):
            item.set_fontfamily(self.plot_settings['font_family'])
            item.set_fontsize(self.plot_settings['font_size'])

if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicGraphApp(root)
    root.mainloop()