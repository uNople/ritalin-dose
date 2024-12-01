import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ritalin_concentration import RitalinModel
import json
import os
import sys

class RitalinUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ritalin Concentration Calculator")
        self.model = RitalinModel()
        self.settings_file = 'ritalin_settings.json'
        
        # Add window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main frames
        self.control_frame = ttk.Frame(root, padding="10")
        self.control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.graph_frame = ttk.Frame(root, padding="10")
        self.graph_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create notebook for LA+IR and IR-only tabs
        self.notebook = ttk.Notebook(self.control_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # LA+IR tab
        self.la_ir_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.la_ir_frame, text="LA + IR")
        
        # IR-only tab
        self.ir_only_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.ir_only_frame, text="IR Only")
        
        # Initialize variables
        self.init_variables()
        
        # Create input fields
        self.create_la_ir_inputs()
        self.create_ir_only_inputs()
        
        # Create plot
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 10))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        
        # Update button
        ttk.Button(self.control_frame, text="Update Graphs", 
                  command=self.update_graphs).grid(row=1, column=0, pady=10)
        
        # Initial plot
        self.update_graphs()

    def init_variables(self):
        # Create the variables
        self.la_morning_dose = tk.StringVar()
        self.la_morning_time = tk.StringVar()
        self.la_afternoon_dose = tk.StringVar()
        self.la_afternoon_time = tk.StringVar()
        self.ir_evening_dose = tk.StringVar()
        self.ir_evening_time = tk.StringVar()
        
        self.ir_doses = [tk.StringVar() for _ in range(4)]
        self.ir_times = [tk.StringVar() for _ in range(4)]
        
        # Load saved values or set defaults
        self.load_saved_settings()

    def load_saved_settings(self):
        """Load the last used settings from JSON file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                # LA+IR settings
                self.la_morning_dose.set(settings.get('la_morning_dose', "30"))
                self.la_morning_time.set(settings.get('la_morning_time', "8"))
                self.la_afternoon_dose.set(settings.get('la_afternoon_dose', "30"))
                self.la_afternoon_time.set(settings.get('la_afternoon_time', "16"))
                self.ir_evening_dose.set(settings.get('ir_evening_dose', "0"))
                self.ir_evening_time.set(settings.get('ir_evening_time', "20"))
                
                # IR-only settings
                for i, (dose, time) in enumerate(zip(
                    settings.get('ir_doses', ["20"]*4),
                    settings.get('ir_times', ["8", "13", "18", "23"])
                )):
                    self.ir_doses[i].set(dose)
                    self.ir_times[i].set(time)
            except:
                self.init_default_variables()
        else:
            self.init_default_variables()

    def save_settings(self):
        """Save current settings to JSON file"""
        settings = {
            'la_morning_dose': self.la_morning_dose.get(),
            'la_morning_time': self.la_morning_time.get(),
            'la_afternoon_dose': self.la_afternoon_dose.get(),
            'la_afternoon_time': self.la_afternoon_time.get(),
            'ir_evening_dose': self.ir_evening_dose.get(),
            'ir_evening_time': self.ir_evening_time.get(),
            'ir_doses': [var.get() for var in self.ir_doses],
            'ir_times': [var.get() for var in self.ir_times]
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)

    def init_default_variables(self):
        """Set default values for all variables"""
        self.la_morning_dose.set("30")
        self.la_morning_time.set("8")
        self.la_afternoon_dose.set("30")
        self.la_afternoon_time.set("16")
        self.ir_evening_dose.set("0")
        self.ir_evening_time.set("20")
        
        for dose_var in self.ir_doses:
            dose_var.set("20")
        
        for time_var, time in zip(self.ir_times, [8, 13, 18, 23]):
            time_var.set(str(time))

    def create_la_ir_inputs(self):
        # Morning LA inputs
        ttk.Label(self.la_ir_frame, text="Morning LA Dose (mg):").grid(row=0, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.la_morning_dose).grid(row=0, column=1, pady=5)
        ttk.Label(self.la_ir_frame, text="Morning LA Time (hour):").grid(row=1, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.la_morning_time).grid(row=1, column=1, pady=5)
        
        # Afternoon LA inputs
        ttk.Label(self.la_ir_frame, text="Afternoon LA Dose (mg):").grid(row=2, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.la_afternoon_dose).grid(row=2, column=1, pady=5)
        ttk.Label(self.la_ir_frame, text="Afternoon LA Time (hour):").grid(row=3, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.la_afternoon_time).grid(row=3, column=1, pady=5)
        
        # IR evening inputs
        ttk.Label(self.la_ir_frame, text="IR Evening Dose (mg):").grid(row=4, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.ir_evening_dose).grid(row=4, column=1, pady=5)
        ttk.Label(self.la_ir_frame, text="IR Evening Time (hour):").grid(row=5, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.ir_evening_time).grid(row=5, column=1, pady=5)

    def create_ir_only_inputs(self):
        times = ["Morning", "Noon", "Afternoon", "Evening"]
        for i, time_label in enumerate(times):
            ttk.Label(self.ir_only_frame, text=f"IR {time_label} Dose (mg):").grid(row=i*2, column=0, pady=5)
            ttk.Entry(self.ir_only_frame, textvariable=self.ir_doses[i]).grid(row=i*2, column=1, pady=5)
            ttk.Label(self.ir_only_frame, text=f"IR {time_label} Time (hour):").grid(row=i*2+1, column=0, pady=5)
            ttk.Entry(self.ir_only_frame, textvariable=self.ir_times[i]).grid(row=i*2+1, column=1, pady=5)

    def update_graphs(self):
        self.ax1.clear()
        self.ax2.clear()
        
        t = np.linspace(0, 24, 289)
        
        # Update LA+IR plot
        try:
            la_morning_dose = float(self.la_morning_dose.get())
            la_morning_time = float(self.la_morning_time.get())
            la_afternoon_dose = float(self.la_afternoon_dose.get())
            la_afternoon_time = float(self.la_afternoon_time.get())
            ir_evening_dose = float(self.ir_evening_dose.get())
            ir_evening_time = float(self.ir_evening_time.get())
            
            # Calculate morning LA concentration
            la_morning_conc = self.model.la_concentration(t, la_morning_dose, la_morning_time)
            # Calculate afternoon LA concentration
            la_afternoon_conc = self.model.la_concentration(t, la_afternoon_dose, la_afternoon_time)
            # Calculate evening IR concentration
            ir_evening_conc = self.model.immediate_release_concentration(t, ir_evening_dose, ir_evening_time)
            
            # Add residuals
            la_morning_conc += self.model.la_concentration(t + 24, la_morning_dose, la_morning_time)
            la_afternoon_conc += self.model.la_concentration(t + 24, la_afternoon_dose, la_afternoon_time)
            ir_evening_conc += self.model.immediate_release_concentration(t + 24, ir_evening_dose, ir_evening_time)
            
            total_la_conc = la_morning_conc + la_afternoon_conc
            total_conc = total_la_conc + ir_evening_conc
            
            self.ax1.plot(t, total_la_conc, label=f'Total LA ({la_morning_dose}mg + {la_afternoon_dose}mg)')
            if ir_evening_dose > 0:
                self.ax1.plot(t, ir_evening_conc, label='Evening IR')
            self.ax1.plot(t, total_conc, label='Total Concentration', linestyle='--', color='red')
            
            for t0 in [la_morning_time, la_afternoon_time]:
                self.ax1.axvline(x=t0, color='gray', linestyle='--', alpha=0.5)
                self.ax1.text(t0 + 0.1, self.ax1.get_ylim()[1] * (0.95 - 0.1 * (t0/8 - 1)), 
                             f'LA Dose ({t0}:00)', rotation=90)
            
            if ir_evening_dose > 0:
                self.ax1.axvline(x=ir_evening_time, color='gray', linestyle='--', alpha=0.5)
                self.ax1.text(ir_evening_time + 0.1, self.ax1.get_ylim()[1] * 0.75, 
                             f'IR Dose ({ir_evening_time}:00)', rotation=90)
            
        except ValueError:
            self.ax1.text(0.5, 0.5, 'Invalid input values', ha='center', va='center')
        
        # Update IR-only plot
        try:
            total_conc = np.zeros_like(t)
            for dose_var, time_var in zip(self.ir_doses, self.ir_times):
                dose = float(dose_var.get())
                time = float(time_var.get())
                conc = self.model.immediate_release_concentration(t, dose, time)
                conc += self.model.immediate_release_concentration(t + 24, dose, time)
                total_conc += conc
                self.ax2.axvline(x=time, color='gray', linestyle='--', alpha=0.5)
            
            self.ax2.plot(t, total_conc, label='Total Concentration', color='red')
            
        except ValueError:
            self.ax2.text(0.5, 0.5, 'Invalid input values', ha='center', va='center')
        
        # Customize plots
        for ax in [self.ax1, self.ax2]:
            ax.set_xlabel('Time (hours)')
            ax.set_ylabel('Relative Concentration')
            ax.grid(True, alpha=0.3)
            ax.legend()
            ax.set_xticks(np.arange(0, 25, 2))
        
        self.ax1.set_title('LA + IR Combination')
        self.ax2.set_title('IR Only')
        
        # Save settings after each update
        self.save_settings()
        
        self.fig.tight_layout()
        self.canvas.draw()

    def on_closing(self):
        """Handle window closing event"""
        self.save_settings()  # Save settings before closing
        self.root.destroy()   # Destroy the window
        sys.exit(0)          # Exit Python

def main():
    root = tk.Tk()
    app = RitalinUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 