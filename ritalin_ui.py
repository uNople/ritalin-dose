import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ritalin_concentration import RitalinModel

class RitalinUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ritalin Concentration Calculator")
        self.model = RitalinModel()
        
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
        # LA+IR variables
        self.la_dose = tk.StringVar(value="60")
        self.la_time = tk.StringVar(value="8")
        self.ir_afternoon_dose = tk.StringVar(value="20")
        self.ir_afternoon_time = tk.StringVar(value="16")
        self.ir_evening_dose = tk.StringVar(value="20")
        self.ir_evening_time = tk.StringVar(value="20")
        
        # IR-only variables
        self.ir_doses = [tk.StringVar(value="20") for _ in range(4)]
        self.ir_times = [tk.StringVar(value=str(t)) for t in [8, 12, 16, 20]]

    def create_la_ir_inputs(self):
        # LA inputs
        ttk.Label(self.la_ir_frame, text="LA Dose (mg):").grid(row=0, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.la_dose).grid(row=0, column=1, pady=5)
        ttk.Label(self.la_ir_frame, text="LA Time (hour):").grid(row=1, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.la_time).grid(row=1, column=1, pady=5)
        
        # IR afternoon inputs
        ttk.Label(self.la_ir_frame, text="IR Afternoon Dose (mg):").grid(row=2, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.ir_afternoon_dose).grid(row=2, column=1, pady=5)
        ttk.Label(self.la_ir_frame, text="IR Afternoon Time (hour):").grid(row=3, column=0, pady=5)
        ttk.Entry(self.la_ir_frame, textvariable=self.ir_afternoon_time).grid(row=3, column=1, pady=5)
        
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
            la_dose = float(self.la_dose.get())
            la_time = float(self.la_time.get())
            ir_afternoon_dose = float(self.ir_afternoon_dose.get())
            ir_afternoon_time = float(self.ir_afternoon_time.get())
            ir_evening_dose = float(self.ir_evening_dose.get())
            ir_evening_time = float(self.ir_evening_time.get())
            
            la_conc = self.model.la_concentration(t, la_dose, la_time)
            ir_afternoon_conc = self.model.immediate_release_concentration(t, ir_afternoon_dose, ir_afternoon_time)
            ir_evening_conc = self.model.immediate_release_concentration(t, ir_evening_dose, ir_evening_time)
            
            # Add residuals
            la_conc += self.model.la_concentration(t + 24, la_dose, la_time)
            ir_afternoon_conc += self.model.immediate_release_concentration(t + 24, ir_afternoon_dose, ir_afternoon_time)
            ir_evening_conc += self.model.immediate_release_concentration(t + 24, ir_evening_dose, ir_evening_time)
            
            total_ir_conc = ir_afternoon_conc + ir_evening_conc
            total_conc = la_conc + total_ir_conc
            
            self.ax1.plot(t, la_conc, label=f'Ritalin LA {la_dose}mg')
            self.ax1.plot(t, total_ir_conc, label='Total IR')
            self.ax1.plot(t, total_conc, label='Total Concentration', linestyle='--', color='red')
            
            for t0 in [la_time, ir_afternoon_time, ir_evening_time]:
                self.ax1.axvline(x=t0, color='gray', linestyle='--', alpha=0.5)
            
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
        
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = RitalinUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 