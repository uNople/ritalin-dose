import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf
from datetime import datetime, timedelta

class RitalinModel:
    def __init__(self, half_life=2.5):
        self.half_life = half_life
        self.elimination_rate = np.log(2) / self.half_life

    def immediate_release_concentration(self, t, dose, t0=0):
        """Model immediate release concentration over time."""
        # Using a combined absorption-elimination model
        ka = 2.0  # absorption rate constant
        F = 1.0   # bioavailability
        V = 1.0   # volume of distribution (normalized)
        
        concentration = (F * dose / V) * (ka / (ka - self.elimination_rate)) * (
            np.exp(-self.elimination_rate * (t - t0)) - np.exp(-ka * (t - t0))
        )
        return np.where(t >= t0, concentration, 0)

    def la_concentration(self, t, dose, t0=0):
        """Model LA (long-acting) concentration over time."""
        # First phase (immediate release)
        immediate = self.immediate_release_concentration(t, dose/2, t0)
        
        # Second phase (delayed release, assume 4-hour delay)
        delayed = self.immediate_release_concentration(t, dose/2, t0 + 4)
        
        return immediate + delayed

def plot_concentrations(model):
    # Create time points (24 hours, in 5-minute intervals)
    t = np.linspace(0, 24, 289)
    
    # Set dosing times
    t0_morning = 8    # 8 AM
    t0_afternoon = 16 # 4 PM
    t0_evening = 20   # 8 PM
    
    # Calculate concentrations including residual from previous day
    la_conc = model.la_concentration(t, 60, t0_morning)
    ir_afternoon_conc = model.immediate_release_concentration(t, 20, t0_afternoon)  # 2x10mg
    ir_evening_conc = model.immediate_release_concentration(t, 20, t0_evening)      # 2x10mg
    
    # Calculate residual from previous day
    prev_la_conc = model.la_concentration(t + 24, 60, t0_morning)
    prev_ir_afternoon_conc = model.immediate_release_concentration(t + 24, 20, t0_afternoon)
    prev_ir_evening_conc = model.immediate_release_concentration(t + 24, 20, t0_evening)
    
    # Add residuals
    la_conc += prev_la_conc
    ir_afternoon_conc += prev_ir_afternoon_conc
    ir_evening_conc += prev_ir_evening_conc
    
    # Combine all IR doses
    total_ir_conc = ir_afternoon_conc + ir_evening_conc
    
    # Calculate total concentration
    total_conc = la_conc + total_ir_conc

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(t, la_conc, label='Ritalin LA 60mg (2x30mg at 8 AM)', linewidth=2)
    plt.plot(t, total_ir_conc, label='Total IR (2x10mg + 2x10mg)', linewidth=2)
    plt.plot(t, total_conc, label='Total Concentration', linewidth=2, 
            linestyle='--', color='red')
    
    # Customize plot
    plt.xlabel('Time (hours)')
    plt.ylabel('Relative Concentration')
    plt.title('Ritalin Concentration Over Time (with residual)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Set x-axis ticks to show hours
    plt.xticks(np.arange(0, 25, 2))
    
    # Add vertical lines at dosing times
    for t0, label in [(t0_morning, '8 AM'), 
                      (t0_afternoon, '4 PM'), 
                      (t0_evening, '8 PM')]:
        plt.axvline(x=t0, color='gray', linestyle='--', alpha=0.5)
        plt.text(t0 + 0.1, plt.ylim()[1] * (0.95 - 0.1 * (t0/8 - 1)), 
                f'Dosing Time ({label})', rotation=90)
    
    plt.tight_layout()
    return plt

def plot_concentrations_ir_only(model):
    # Create time points (24 hours, in 5-minute intervals)
    t = np.linspace(0, 24, 289)
    
    # Set dosing times
    t0_morning = 8     # 8 AM
    t0_noon = 12      # 12 PM
    t0_afternoon = 16  # 4 PM
    t0_evening = 20    # 8 PM
    
    # Calculate concentrations including residual from previous day
    ir_morning_conc = model.immediate_release_concentration(t, 20, t0_morning)    # 2x10mg
    ir_noon_conc = model.immediate_release_concentration(t, 20, t0_noon)         # 2x10mg
    ir_afternoon_conc = model.immediate_release_concentration(t, 20, t0_afternoon)  # 2x10mg
    ir_evening_conc = model.immediate_release_concentration(t, 20, t0_evening)     # 2x10mg
    
    # Calculate residual from previous day
    prev_ir_morning_conc = model.immediate_release_concentration(t + 24, 20, t0_morning)
    prev_ir_noon_conc = model.immediate_release_concentration(t + 24, 20, t0_noon)
    prev_ir_afternoon_conc = model.immediate_release_concentration(t + 24, 20, t0_afternoon)
    prev_ir_evening_conc = model.immediate_release_concentration(t + 24, 20, t0_evening)
    
    # Add residuals
    ir_morning_conc += prev_ir_morning_conc
    ir_noon_conc += prev_ir_noon_conc
    ir_afternoon_conc += prev_ir_afternoon_conc
    ir_evening_conc += prev_ir_evening_conc
    
    # Calculate total concentration
    total_conc = ir_morning_conc + ir_noon_conc + ir_afternoon_conc + ir_evening_conc

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(t, total_conc, label='Total Concentration', linewidth=2, color='red')
    
    # Customize plot
    plt.xlabel('Time (hours)')
    plt.ylabel('Relative Concentration')
    plt.title('Ritalin IR Only - 2x10mg doses (with residual)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Set x-axis ticks to show hours
    plt.xticks(np.arange(0, 25, 2))
    
    # Add vertical lines at dosing times
    for t0, label in [(t0_morning, '8 AM'),
                      (t0_noon, '12 PM'),
                      (t0_afternoon, '4 PM'),
                      (t0_evening, '8 PM')]:
        plt.axvline(x=t0, color='gray', linestyle='--', alpha=0.5)
        plt.text(t0 + 0.1, plt.ylim()[1] * (0.95 - 0.1 * (t0/8 - 1)), 
                f'Dosing Time ({label})\n2x10mg IR', rotation=90)
    
    plt.tight_layout()
    return plt

def main():
    model = RitalinModel()
    
    # Create LA + IR plot
    plt1 = plot_concentrations(model)
    plt1.savefig('ritalin_concentration_la_ir.png')
    
    # Create IR only plot
    plt2 = plot_concentrations_ir_only(model)
    plt2.savefig('ritalin_concentration_ir_only.png')
    
    plt.show()

if __name__ == "__main__":
    main() 