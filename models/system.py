import numpy as np
from .generator import SynchronousGenerator
from .load import Load
from solvers.equation_system import solve_system

class GeneratorSystem:
    def __init__(self, params):
        """
        Inicializa el sistema de dos generadores síncronos en paralelo
        
        Parameters:
        -----------
        params : dict
            Diccionario con parámetros para los generadores y la carga
        """
        # Crear instancias de generadores
        self.generator1 = SynchronousGenerator(params["generator1"])
        self.generator2 = SynchronousGenerator(params["generator2"])
        
        # Crear instancia de carga
        self.load = Load(
            params["load"]["r_load"],
            params["load"]["x_load"]
        )
    
    def solve(self):
        """
        Resuelve el sistema completo
        
        Returns:
        --------
        dict
            Diccionario con todos los resultados calculados
        """
        # Resolver el sistema de ecuaciones no lineales
        solution = solve_system(self.generator1, self.generator2, self.load)
        
        # Extraer variables de la solución
        ia1_real, ia1_imag = solution[0], solution[1]
        ia2_real, ia2_imag = solution[2], solution[3]
        vt_real, vt_imag = solution[4], solution[5]
        delta1, delta2 = solution[6], solution[7]
        
        # Formar números complejos
        ia1 = complex(ia1_real, ia1_imag)
        ia2 = complex(ia2_real, ia2_imag)
        vt = complex(vt_real, vt_imag)
        
        # Calcular EA1 y EA2 usando las curvas de magnetización y los ángulos delta
        ea1_mag = self.generator1.get_ea_from_if(self.generator1.if_op)
        ea2_mag = self.generator2.get_ea_from_if(self.generator2.if_op)
        
        ea1 = ea1_mag * np.exp(1j * delta1)
        ea2 = ea2_mag * np.exp(1j * delta2)
        
        # Calcular corrientes de línea (asumiendo conexión en Y)
        il1 = ia1
        il2 = ia2
        
        # Calcular tensiones de fase (asumiendo sistema equilibrado)
        vf1 = vt
        vf2 = vt
        
        # Calcular potencias de los generadores
        p1 = (ea1 * np.conj(ia1)).real
        q1 = (ea1 * np.conj(ia1)).imag
        s1 = abs(ea1 * np.conj(ia1))
        
        p2 = (ea2 * np.conj(ia2)).real
        q2 = (ea2 * np.conj(ia2)).imag
        s2 = abs(ea2 * np.conj(ia2))
        
        # Calcular velocidad síncrona y frecuencia
        f1 = self.generator1.f_sc  # Asumimos que operan a la frecuencia especificada
        f2 = self.generator2.f_sc
        f = (f1 + f2) / 2  # Frecuencia del sistema
        
        omega_sinc1 = 2 * np.pi * f1 / (self.generator1.poles / 2)
        omega_sinc2 = 2 * np.pi * f2 / (self.generator2.poles / 2)
        
        # Calcular torques
        tind1 = p1 / omega_sinc1
        tind2 = p2 / omega_sinc2
        
        # Asumimos que el torque aplicado es igual al inducido en estado estable
        tap1 = tind1
        tap2 = tind2
        
        # Calcular pérdidas en el cobre
        pcu1 = 3 * (abs(ia1) ** 2) * self.generator1.ra
        pcu2 = 3 * (abs(ia2) ** 2) * self.generator2.ra
        
        # Calcular corriente y potencia de carga
        i_load = self.load.calculate_current(vt)
        s_complex_load = vt * np.conj(i_load)
        p_load = s_complex_load.real
        q_load = s_complex_load.imag
        s_load = abs(s_complex_load)
        fp_load = p_load / s_load if s_load > 0 else 1.0
        
        # Calcular pérdidas y potencia total
        p_total = p1 + p2
        q_total = q1 + q2
        losses_total = p_total - p_load
        
        # Preparar resultados
        results = {
            # Generador 1
            "g1_ia": ia1,
            "g1_il": il1,
            "g1_if": self.generator1.if_op,
            "g1_ea": ea1,
            "g1_vt": vt,
            "g1_vf": vf1,
            "g1_p": p1,
            "g1_q": q1,
            "g1_s": s1,
            "g1_delta": np.degrees(delta1),
            "g1_tind": tind1,
            "g1_tap": tap1,
            "g1_omega_sinc": omega_sinc1,
            "g1_fe": f1,
            "g1_pcu": pcu1,
            
            # Generador 2
            "g2_ia": ia2,
            "g2_il": il2,
            "g2_if": self.generator2.if_op,
            "g2_ea": ea2,
            "g2_vt": vt,
            "g2_vf": vf2,
            "g2_p": p2,
            "g2_q": q2,
            "g2_s": s2,
            "g2_delta": np.degrees(delta2),
            "g2_tind": tind2,
            "g2_tap": tap2,
            "g2_omega_sinc": omega_sinc2,
            "g2_fe": f2,
            "g2_pcu": pcu2,
            
            # Carga y sistema
            "vt": vt,
            "i_load": i_load,
            "p_load": p_load,
            "q_load": q_load,
            "s_load": s_load,
            "fp_load": fp_load,
            "f": f,
            "p_total": p_total,
            "q_total": q_total,
            "losses_total": losses_total,
            
            # Puntos de operación para gráficas
            "op_point_g1": {
                "if": self.generator1.if_op,
                "ea": abs(ea1),
                "p": p1,
                "q": q1
            },
            "op_point_g2": {
                "if": self.generator2.if_op,
                "ea": abs(ea2),
                "p": p2,
                "q": q2
            }
        }
        
        return results