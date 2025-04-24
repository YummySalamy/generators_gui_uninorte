import numpy as np
from scipy.interpolate import interp1d

class SynchronousGenerator:
    def __init__(self, params):
        # Parámetros del circuito equivalente
        self.ra = params["ra"]  # Resistencia de armadura
        self.xs = params["xs"]  # Reactancia síncrona
        
        # Valores nominales
        self.s_nom = params["s_nom"]  # Potencia aparente nominal
        self.v_nom = params["v_nom"]  # Tensión nominal
        self.fp_nom = params["fp_nom"]  # Factor de potencia nominal
        self.poles = params["poles"]  # Número de polos
        
        # Curva de magnetización
        self.if_values = np.array(params["if_values"])  # Corrientes de campo
        self.ea_values = np.array(params["ea_values"])  # Fuerzas electromotrices
        self.magnetization_curve = interp1d(
            self.if_values, 
            self.ea_values, 
            kind='cubic', 
            bounds_error=False, 
            fill_value="extrapolate"
        )
        
        # Punto de operación
        self.f_sc = params["f_sc"]  # Frecuencia de vacío
        self.if_op = params["if_op"]  # Corriente de campo
        
        # Pérdidas
        self.p_core = params["p_core"]  # Pérdidas en el núcleo
        self.p_friction = params["p_friction"]  # Pérdidas por fricción
        self.p_misc = params["p_misc"]  # Pérdidas misceláneas
        
        # Capacidad del motor primario
        self.p_motor = params["p_motor"]  # Potencia del motor primario
    
    def get_ea_from_if(self, if_value):
        """Calcula la fuerza electromotriz a partir de la corriente de campo"""
        # Asegurarse de que la curva de magnetización maneja valores fuera de rango
        if if_value < min(self.if_values):
            # Para valores menores, usamos una extrapolación lineal desde el origen
            slope = self.ea_values[0] / self.if_values[0]
            return float(slope * if_value)
        elif if_value > max(self.if_values):
            # Para valores mayores, extrapolamos con saturación
            # Usamos los dos últimos puntos para calcular la pendiente
            n = len(self.if_values)
            slope = (self.ea_values[n-1] - self.ea_values[n-2]) / (self.if_values[n-1] - self.if_values[n-2])
            extra = slope * (if_value - self.if_values[n-1]) + self.ea_values[n-1]
            # Limitamos la extrapolación para evitar valores irreales
            max_ea = self.ea_values[n-1] * 1.3  # 30% más que el último valor
            return float(min(extra, max_ea))
        else:
            # Dentro del rango, usamos la interpolación
            return float(self.magnetization_curve(if_value))
    
    def calculate_power_angle(self, ea, vt, ia):
        """Calcula el ángulo de potencia delta"""
        # Implementación basada en la relación fasorial
        # EA = VT + (RA + jXS)IA
        pass
    
    def calculate_induced_torque(self, p, omega):
        """Calcula el torque inducido"""
        return p / omega
    
    def calculate_copper_losses(self, ia):
        """Calcula las pérdidas en el cobre"""
        return 3 * (abs(ia) ** 2) * self.ra
    
    def get_capability_curve(self):
        """Genera los puntos para la curva de capacidad"""
        # Implementación para generar los límites P-Q del generador
        pass