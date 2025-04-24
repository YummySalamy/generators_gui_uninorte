import numpy as np

class Load:
    def __init__(self, r_load, x_load):
        self.r_load = r_load  # Resistencia de carga
        self.x_load = x_load  # Reactancia de carga (+ inductiva, - capacitiva)
        
    def calculate_impedance(self):
        """Calcula la impedancia compleja de la carga"""
        return complex(self.r_load, self.x_load)
    
    def calculate_admittance(self):
        """Calcula la admitancia compleja de la carga"""
        z = self.calculate_impedance()
        return 1 / z
    
    def calculate_current(self, voltage):
        """Calcula la corriente que fluye por la carga"""
        y = self.calculate_admittance()
        return voltage * y
    
    def calculate_power(self, voltage):
        """Calcula la potencia compleja consumida por la carga"""
        current = self.calculate_current(voltage)
        return voltage * np.conj(current)