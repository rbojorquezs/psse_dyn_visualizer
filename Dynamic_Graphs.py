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
import os
import re

# Inicializar PSSE V_36
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
        self.y_styles = []  # lista de tuplas (color_entry, style_entry, label_entry)
        self.line_colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']  # Colors for multiple lines
        
        # Initialize font list
        try:
            self.fonts = sorted(list(tkFont.families()))
        except:
            # Fallback fonts if system fonts can't be retrieved
            self.fonts = ['Arial', 'Times New Roman', 'Courier New', 'Verdana', 'Helvetica']

        
        # Default plot settings
        self.plot_settings = {
            'title': "  ",
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

        self.legend_pos = tk.StringVar(value='best')
        self.legend_frameon = tk.BooleanVar(value=True)
        self.bbox_x = tk.StringVar(value='')
        self.bbox_y = tk.StringVar(value='')

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

        # Frame contenedor para distribuir en 2 columnas
        layout_frame = ttk.Frame(custom_frame)
        layout_frame.pack(fill=tk.BOTH, expand=True)

        # ===== Estilo General =====
        style_frame = ttk.LabelFrame(layout_frame, text="Estilo General", padding=5)
        style_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Label(style_frame, text="Título:").pack(anchor="w")
        self.title_entry = ttk.Entry(style_frame)
        self.title_entry.insert(0, self.plot_settings['title'])
        self.title_entry.pack(fill=tk.X)

        ttk.Label(style_frame, text="Fuente:").pack(anchor="w", pady=(5, 0))
        self.font_combo = ttk.Combobox(style_frame, values=self.fonts, state="readonly")
        self.font_combo.set(self.plot_settings['font_family'])
        self.font_combo.pack(fill=tk.X)

        ttk.Label(style_frame, text="Tamaño fuente:").pack(anchor="w", pady=(5, 0))
        self.font_size_entry = ttk.Entry(style_frame, width=8)
        self.font_size_entry.insert(0, str(self.plot_settings['font_size']))
        self.font_size_entry.pack(fill=tk.X)

        # ===== Eje X =====
        xaxis_frame = ttk.LabelFrame(layout_frame, text="Eje X", padding=5)
        xaxis_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        ttk.Label(xaxis_frame, text="Etiqueta:").pack(anchor="w")
        self.xlabel_entry = ttk.Entry(xaxis_frame)
        self.xlabel_entry.pack(fill=tk.X)

        ttk.Label(xaxis_frame, text="Límites:").pack(anchor="w", pady=(5, 0))
        xlim_frame = ttk.Frame(xaxis_frame)
        xlim_frame.pack(fill=tk.X)
        ttk.Label(xlim_frame, text="Min:").pack(side=tk.LEFT)
        self.xlim_min_entry = ttk.Entry(xlim_frame, width=8)
        self.xlim_min_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(xlim_frame, text="Max:").pack(side=tk.LEFT)
        self.xlim_max_entry = ttk.Entry(xlim_frame, width=8)
        self.xlim_max_entry.pack(side=tk.LEFT, padx=2)

        # ===== Eje Y izquierdo =====
        yaxis_frame = ttk.LabelFrame(layout_frame, text="Eje Y izquierdo", padding=5)
        yaxis_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Label(yaxis_frame, text="Etiqueta:").pack(anchor="w")
        self.ylabel_entry = ttk.Entry(yaxis_frame)
        self.ylabel_entry.insert(0, self.plot_settings['ylabel'])
        self.ylabel_entry.pack(fill=tk.X)

        ttk.Label(yaxis_frame, text="Límites:").pack(anchor="w", pady=(5, 0))
        ylim_frame = ttk.Frame(yaxis_frame)
        ylim_frame.pack(fill=tk.X)
        ttk.Label(ylim_frame, text="Min:").pack(side=tk.LEFT)
        self.ylim_min_entry = ttk.Entry(ylim_frame, width=8)
        self.ylim_min_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(ylim_frame, text="Max:").pack(side=tk.LEFT)
        self.ylim_max_entry = ttk.Entry(ylim_frame, width=8)
        self.ylim_max_entry.pack(side=tk.LEFT, padx=2)

        # ===== Eje Y derecho =====
        y2axis_frame = ttk.LabelFrame(layout_frame, text="Eje Y derecho", padding=5)
        y2axis_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        ttk.Label(y2axis_frame, text="Límites:").pack(anchor="w")
        y2lim_frame = ttk.Frame(y2axis_frame)
        y2lim_frame.pack(fill=tk.X)
        ttk.Label(y2lim_frame, text="Min:").pack(side=tk.LEFT)
        self.y2lim_min_entry = ttk.Entry(y2lim_frame, width=8)
        self.y2lim_min_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(y2lim_frame, text="Max:").pack(side=tk.LEFT)
        self.y2lim_max_entry = ttk.Entry(y2lim_frame, width=8)
        self.y2lim_max_entry.pack(side=tk.LEFT, padx=2)

        # ===== Opciones =====
        options_frame = ttk.LabelFrame(layout_frame, text="Opciones", padding=5)
        options_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # Leyenda: posición
        ttk.Label(options_frame, text="Posición de la leyenda:").pack(anchor="w", pady=(5, 0))
        posiciones_leyenda = [
            'best', 'upper right', 'upper left', 'lower left',
            'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'
        ]
        legend_pos_combo = ttk.Combobox(options_frame, textvariable=self.legend_pos, state="readonly", values=posiciones_leyenda)
        legend_pos_combo.pack(fill=tk.X)

        # Checkbox para mostrar o no marco de la leyenda
        ttk.Checkbutton(options_frame, text="Mostrar marco en la leyenda", variable=self.legend_frameon).pack(anchor="w")

        # bbox_to_anchor
        bbox_frame = ttk.Frame(options_frame)
        bbox_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(bbox_frame, text="bbox x:").pack(side=tk.LEFT)
        bbox_x_entry = ttk.Entry(bbox_frame, textvariable=self.bbox_x, width=6)
        bbox_x_entry.pack(side=tk.LEFT, padx=(2, 8))
        ttk.Label(bbox_frame, text="y:").pack(side=tk.LEFT)
        bbox_y_entry = ttk.Entry(bbox_frame, textvariable=self.bbox_y, width=6)
        bbox_y_entry.pack(side=tk.LEFT, padx=(2, 0))


        self.grid_var = tk.BooleanVar(value=self.plot_settings['grid'])
        ttk.Checkbutton(options_frame, text="Mostrar Grid", variable=self.grid_var).pack(anchor=tk.W)


        self.save_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Guardar como imagen PNG", variable=self.save_var).pack(anchor=tk.W)

        ttk.Label(options_frame, text="Nombre del archivo (opcional):").pack(anchor=tk.W)
        self.filename_entry = ttk.Entry(options_frame)
        self.filename_entry.pack(fill=tk.X, pady=(0, 5))

        self.dual_y_var = tk.BooleanVar(value=False)
        self.dual_y_check = ttk.Checkbutton(options_frame, text="Usar segundo eje Y (derecho)", variable=self.dual_y_var)
        self.dual_y_check.pack(anchor=tk.W)
        self.dual_y_check.pack_forget()  # ocultarlo inicialmente

        # expandir columnas por igual
        layout_frame.columnconfigure(0, weight=1)
        layout_frame.columnconfigure(1, weight=1)


        
        # Plot button
        ttk.Button(right_frame, text="Generate Plot", command=self.generate_plot).pack(pady=10)

        # Reset axes button
        ttk.Button(right_frame, text="Resetear Ejes", command=self.reset_axes).pack(pady=5)


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
                self.outfile_path = outfile
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
        
                # Mostrar opción de doble eje Y si hay 2+ variables disponibles
        if len(self.chanid) >= 2:
            self.dual_y_check.pack()
        else:
            self.dual_y_var.set(False)
            self.dual_y_check.pack_forget()


        
        # Mostrar opción de doble eje Y si hay 2+ variables disponibles
        if len(self.chanid) >= 2:
            self.dual_y_check.grid()
        else:
            self.dual_y_var.set(False)
            self.dual_y_check.grid_remove()
    
    def add_y_variable(self):
        # Crear nuevo frame para el conjunto de opciones de una variable Y
        frame = ttk.Frame(self.y_frame)
        frame.pack(fill=tk.X, pady=2)

        # Etiqueta y combobox para seleccionar canal
        ttk.Label(frame, text=f"Y-axis Variable {len(self.y_combos)+1}:").pack(side=tk.LEFT, padx=5)
        combo = ttk.Combobox(frame, state="readonly", width=40)
        combo.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        # Personalización de estilo y leyenda
        color_entry = ttk.Entry(frame, width=6)
        color_entry.insert(0, 'b')  # color por defecto
        color_entry.pack(side=tk.LEFT, padx=(5, 0))

        style_entry = ttk.Entry(frame, width=6)
        style_entry.insert(0, '-')  # estilo por defecto
        style_entry.pack(side=tk.LEFT, padx=(5, 0))

        label_entry = ttk.Entry(frame, width=15)
        label_entry.insert(0, '')  # nombre personalizado de la leyenda
        label_entry.pack(side=tk.LEFT, padx=(5, 0))

        # Botón de eliminar
        ttk.Button(frame, text="×", width=2, 
                command=lambda c=combo: self.remove_y_variable(c)).pack(side=tk.RIGHT, padx=5)

        # Inicializar si ya se cargó el archivo
        if self.chanid:
            combo['values'] = list(self.chanid.values())
            if len(self.y_combos) + 1 < len(self.chanid):
                combo.current(len(self.y_combos) + 1)
            else:
                combo.current(0)

        # Guardar referencias
        self.y_combos.append(combo)
        self.y_styles.append((color_entry, style_entry, label_entry))

    
    def remove_y_variable(self, combo):
        if len(self.y_combos) <= 1:
            messagebox.showwarning("Warning", "You need at least one Y variable")
            return
            
        idx = self.y_combos.index(combo)
        self.y_combos.pop(idx)
        combo.master.destroy()  # Destroy the containing frame
    
    def generate_plot(self, save_image=True):
        x_selection = self.combo_x.get()
        if not x_selection:
            messagebox.showerror("Error", "Please select an X-axis variable")
            return

        y_selections = [combo.get() for combo in self.y_combos if combo.get()]
        if not y_selections:
            messagebox.showerror("Error", "Please select at least one Y-axis variable")
            return

        try:
            self.ax.clear()
            ax2 = None  # segundo eje


            # Obtener datos de X
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

            # Preparar límites automáticos
            x_min, x_max = min(x_data), max(x_data)
            y1_min, y1_max = float('inf'), float('-inf')
            y2_min, y2_max = float('inf'), float('-inf')

            use_dual_y = self.dual_y_var.get() and len(y_selections) >= 2

            # Paso 1: calcular rangos de todas las variables Y
            var_data_list = []
            for y_sel in y_selections:
                y_chan = int(y_sel.split(':')[0]) if y_sel != "time" else 'time'
                y_data = self.chandata.get(y_chan)
                y_label = y_sel.split(': ')[1] if ': ' in y_sel else y_sel
                y_min_val, y_max_val = min(y_data), max(y_data)
                var_range = y_max_val - y_min_val
                var_data_list.append((y_sel, y_data, y_label, var_range, y_min_val, y_max_val))

            # Paso 2: ordenar por rango
            var_data_list.sort(key=lambda x: x[3], reverse=True)  # de mayor a menor rango

            # Paso 3: asignar variables a ejes
            use_dual_y = self.dual_y_var.get() and len(var_data_list) >= 2
            y1_vars = []
            y2_vars = []

            if use_dual_y:
                # Algoritmo simple: la primera (mayor rango) al eje izquierdo, el resto se evalúan
                base_range = var_data_list[0][3]
                y1_vars.append(var_data_list[0])
                for item in var_data_list[1:]:
                    if item[3] >= 0.1 * base_range:
                        y1_vars.append(item)
                    else:
                        y2_vars.append(item)
            else:
                y1_vars = var_data_list

            # Paso 4: graficar
            y1_min, y1_max = float('inf'), float('-inf')
            y2_min, y2_max = float('inf'), float('-inf')

            for i, (y_sel, y_data, y_label, _, y_min_v, y_max_v) in enumerate(y1_vars):
                color_entry, style_entry, label_entry = self.y_styles[i]
                color = color_entry.get() or self.line_colors[i % len(self.line_colors)]
                style = style_entry.get() or '-'
                label = label_entry.get().strip() or y_label
                self.ax.plot(x_data, y_data, linestyle=style, color=color, label=label, linewidth=1.8)
                y1_min = min(y1_min, y_min_v)
                y1_max = max(y1_max, y_max_v)


            if y2_vars:
                ax2 = self.ax.twinx()
                for j, (y_sel, y_data, y_label, _, y_min_v, y_max_v) in enumerate(y2_vars):
                    i = j + len(y1_vars)
                    color_entry, style_entry, label_entry = self.y_styles[i]
                    color = color_entry.get() or self.line_colors[i % len(self.line_colors)]
                    style = style_entry.get() or '--'
                    label = label_entry.get().strip() or y_label
                    ax2.plot(x_data, y_data, linestyle=style, color=color, label=label, linewidth=1.8)
                    y2_min = min(y2_min, y_min_v)
                    y2_max = max(y2_max, y_max_v)

            else:
                ax2 = None


            # Calcular padding
            x_padding = (x_max - x_min) * 0.05
            y1_padding = (y1_max - y1_min) * 0.05 if y1_max != y1_min else 1
            y2_padding = (y2_max - y2_min) * 0.05 if y2_max != y2_min else 1

            # Establecer límites X si campos están vacíos
            if not self.xlim_min_entry.get():
                self.xlim_min_entry.insert(0, f"{x_min - x_padding:.2f}")
            if not self.xlim_max_entry.get():
                self.xlim_max_entry.insert(0, f"{x_max + x_padding:.2f}")
            # Y1
            if not self.ylim_min_entry.get():
                self.ylim_min_entry.insert(0, f"{y1_min - y1_padding:.2f}")
            if not self.ylim_max_entry.get():
                self.ylim_max_entry.insert(0, f"{y1_max + y1_padding:.2f}")

            if ax2 and y2_vars:
                if not self.y2lim_min_entry.get():
                    self.y2lim_min_entry.insert(0, f"{y2_min - y2_padding:.2f}")
                if not self.y2lim_max_entry.get():
                    self.y2lim_max_entry.insert(0, f"{y2_max + y2_padding:.2f}")


            # Aplicar configuraciones y redibujar
            legend_loc = self.legend_pos.get()
            frameon = self.legend_frameon.get()
            bbox_anchor = None

            try:
                if self.bbox_x.get() and self.bbox_y.get():
                    bbox_anchor = (float(self.bbox_x.get()), float(self.bbox_y.get()))
            except ValueError:
                pass  # si están vacíos o mal puestos, se ignora

            if self.ax.get_legend_handles_labels()[1]:
                self.ax.legend(loc=legend_loc, fontsize=10, frameon=frameon, bbox_to_anchor=bbox_anchor)

            if ax2 and ax2.get_legend_handles_labels()[1]:
                self.ax.figure.tight_layout()
                ax2.legend(loc=legend_loc, fontsize=10, frameon=frameon, bbox_to_anchor=bbox_anchor)


        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plot:\n{str(e)}")


    def apply_plot_settings(self, x_label, ax2=None):
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
            if ax2:
                try:
                    ylim2_min = self.y2lim_min_entry.get()
                    ylim2_max = self.y2lim_max_entry.get()
                    if ylim2_min and ylim2_max:
                        ax2.set_ylim(float(ylim2_min), float(ylim2_max))
                except ValueError:
                    pass  # Si hay error en la entrada, se usa el autoescalado

        except ValueError:
            pass  # Keep auto-scaled limits if custom ones are invalid
        
        # Set grid
        self.ax.grid(self.plot_settings['grid'])
        
        # Apply font to all text elements
        for item in ([self.ax.title, self.ax.xaxis.label, self.ax.yaxis.label] +
                    self.ax.get_xticklabels() + self.ax.get_yticklabels()):
            item.set_fontfamily(self.plot_settings['font_family'])
            item.set_fontsize(self.plot_settings['font_size'])

        if ax2:
            for item in ([ax2.yaxis.label] + ax2.get_yticklabels()):
                item.set_fontfamily(self.plot_settings['font_family'])
                item.set_fontsize(self.plot_settings['font_size'])


    def save_figure_as_png(self):
        if not hasattr(self, 'outfile_path') or not self.outfile_path:
            return

        try:
            # Carpeta del archivo .out
            out_dir = os.path.dirname(self.outfile_path)

            # Nombre del archivo desde entrada o título
            filename = self.filename_entry.get().strip()
            if not filename:
                filename = self.title_entry.get().strip() or "dynamic_simulation"

            # Sanitizar nombre
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", filename).replace(" ", "_")
            save_path = os.path.join(out_dir, f"{safe_title}.png")

            # Guardar
            self.fig.savefig(save_path, dpi=300, bbox_inches='tight', transparent=True)
            messagebox.showinfo("Imagen guardada", f"Gráfica guardada en:\n{save_path}")
        except Exception as e:
            messagebox.showwarning("Error al guardar imagen", str(e))

    def reset_axes(self):
        # Limpiar los campos de límites (ejes X, Y1, Y2)
        for entry in [self.xlim_min_entry, self.xlim_max_entry,
                    self.ylim_min_entry, self.ylim_max_entry,
                    self.y2lim_min_entry, self.y2lim_max_entry]:
            entry.delete(0, tk.END)

        # Regenerar completamente el gráfico SIN guardar imagen
        self.ax.clear()
        self.generate_plot(save_image=False)


if __name__ == "__main__":
    root = tk.Tk()
    app = DynamicGraphApp(root)
    root.mainloop()
