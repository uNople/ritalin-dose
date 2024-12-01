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

def plot_concentrations(model, include_residual=False):
    # Create time points (24 hours, in 5-minute intervals)
    t = np.linspace(0, 24, 289)
    
    # Set dosing time (8 AM = hour 8)
    t0 = 8
    
    # Calculate concentrations
    la_conc = model.la_concentration(t, 30, t0)
    ir_conc = model.immediate_release_concentration(t, 10, t0)
    
    if include_residual:
        # Calculate residual from previous day
        prev_la_conc = model.la_concentration(t + 24, 30, t0)
        prev_ir_conc = model.immediate_release_concentration(t + 24, 10, t0)
        la_conc += prev_la_conc
        ir_conc += prev_ir_conc

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(t, la_conc, label='Ritalin LA 30mg', linewidth=2)
    plt.plot(t, ir_conc, label='Ritalin IR 10mg', linewidth=2)
    
    # Customize plot
    plt.xlabel('Time (hours)')
    plt.ylabel('Relative Concentration')
    plt.title(f'Ritalin Concentration Over Time {"(with residual)" if include_residual else ""}')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Set x-axis ticks to show hours
    plt.xticks(np.arange(0, 25, 2))
    
    # Add vertical line at dosing time
    plt.axvline(x=t0, color='gray', linestyle='--', alpha=0.5)
    plt.text(t0 + 0.1, plt.ylim()[1] * 0.95, 'Dosing Time (8 AM)', rotation=90)
    
    plt.tight_layout()
    return plt

def main():
    model = RitalinModel()
    
    # Plot without residual
    plt1 = plot_concentrations(model, include_residual=False)
    plt1.savefig('ritalin_concentration_no_residual.png')
    
    # Plot with residual
    plt2 = plot_concentrations(model, include_residual=True)
    plt2.savefig('ritalin_concentration_with_residual.png')
    
    plt.show()

if __name__ == "__main__":
    main() 