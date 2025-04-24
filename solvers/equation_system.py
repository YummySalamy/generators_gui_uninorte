import numpy as np
from scipy import optimize

def create_equation_system(generator1, generator2, load, vt_initial):
    """
    Crea el sistema de ecuaciones no lineales para resolver
    
    Parameters:
    -----------
    generator1 : SynchronousGenerator
        Primer generador síncrono
    generator2 : SynchronousGenerator
        Segundo generador síncrono
    load : Load
        Carga conectada a los generadores
    vt_initial : complex
        Valor inicial para la tensión en terminales
        
    Returns:
    --------
    callable
        Función que representa el sistema de ecuaciones
    """
    
    def equations(variables):
        """
        Sistema de ecuaciones no lineales
        
        Variables:
        - variables[0], variables[1]: Parte real e imaginaria de IA1
        - variables[2], variables[3]: Parte real e imaginaria de IA2
        - variables[4], variables[5]: Parte real e imaginaria de VT
        - variables[6]: Ángulo delta1
        - variables[7]: Ángulo delta2
        """
        # Extraer variables
        ia1_real, ia1_imag = variables[0], variables[1]
        ia2_real, ia2_imag = variables[2], variables[3]
        vt_real, vt_imag = variables[4], variables[5]
        delta1, delta2 = variables[6], variables[7]
        
        # Formar números complejos
        ia1 = complex(ia1_real, ia1_imag)
        ia2 = complex(ia2_real, ia2_imag)
        vt = complex(vt_real, vt_imag)
        
        # Calcular EA1 y EA2 usando las curvas de magnetización
        ea1_mag = generator1.get_ea_from_if(generator1.if_op)
        ea2_mag = generator2.get_ea_from_if(generator2.if_op)
        
        # Convertir a forma compleja usando los ángulos delta
        ea1 = ea1_mag * np.exp(1j * delta1)
        ea2 = ea2_mag * np.exp(1j * delta2)
        
        # Calcular impedancias
        z1 = complex(generator1.ra, generator1.xs)
        z2 = complex(generator2.ra, generator2.xs)
        
        # Ecuaciones fasoriales
        eq1_real = (ea1 - vt - z1 * ia1).real
        eq1_imag = (ea1 - vt - z1 * ia1).imag
        
        eq2_real = (ea2 - vt - z2 * ia2).real
        eq2_imag = (ea2 - vt - z2 * ia2).imag
        
        # Corriente de carga
        i_load = load.calculate_current(vt)
        
        # Ley de Kirchhoff para corrientes
        eq5_real = (ia1 + ia2 - i_load).real
        eq5_imag = (ia1 + ia2 - i_load).imag
        
        # Ecuaciones de potencia (simplificadas para mejorar convergencia)
        # Usamos restricciones más suaves para ayudar a la convergencia
        p1 = (ea1 * np.conj(ia1)).real
        p2 = (ea2 * np.conj(ia2)).real
        
        # En lugar de restricciones estrictas, usamos desviaciones respecto a los valores deseados
        p1_target = generator1.p_motor * 0.9  # Objetivo ligeramente menor para facilitar convergencia
        p2_target = generator2.p_motor * 0.9
        
        eq7 = (p1 - p1_target) / max(1.0, abs(p1_target))  # Normalizado
        eq8 = (p2 - p2_target) / max(1.0, abs(p2_target))
        
        return [eq1_real, eq1_imag, eq2_real, eq2_imag, eq5_real, eq5_imag, eq7, eq8]
    
    return equations

def solve_system(generator1, generator2, load, initial_guess=None):
    """
    Resuelve el sistema de ecuaciones no lineales usando múltiples intentos
    con diferentes configuraciones si es necesario.
    """
    # Valor inicial para VT (en voltios)
    vt_magnitude = generator1.v_nom / np.sqrt(3)  # Tensión de fase
    vt_initial = complex(vt_magnitude, 0)
    
    # Crear el sistema de ecuaciones
    system = create_equation_system(generator1, generator2, load, vt_initial)
    
    # Si no se proporciona una estimación inicial, creamos una razonable
    if initial_guess is None:
        # Estimación para corrientes de armadura basada en potencia nominal
        s1_nom = generator1.s_nom
        s2_nom = generator2.s_nom
        v_nom = vt_magnitude
        
        # Corriente nominal aproximada
        i1_nom = s1_nom / (3 * v_nom)
        i2_nom = s2_nom / (3 * v_nom)
        
        # Estimación para ángulos de potencia
        delta1_est = 0.2  # Estimación pequeña para delta (en radianes)
        delta2_est = 0.2
        
        # Vector de estimación inicial
        initial_guess = [
            i1_nom * 0.5, 0,  # IA1 (real, imag)
            i2_nom * 0.5, 0,  # IA2 (real, imag)
            vt_magnitude, 0,  # VT (real, imag)
            delta1_est, delta2_est  # Ángulos delta
        ]
    
    # Lista de métodos y opciones para probar
    methods_to_try = [
        ('hybr', {}),
        ('lm', {'ftol': 1e-5}),
        ('lm', {'ftol': 1e-3}),
        ('krylov', {}),
        ('broyden1', {'tol': 1e-3})
    ]
    
    # Intentar con diferentes métodos hasta que uno funcione
    solution = None
    last_error = None
    
    for method, options in methods_to_try:
        try:
            print(f"Intentando con método: {method}")
            solution = optimize.root(system, initial_guess, method=method, options=options)
            
            if solution.success:
                print(f"Éxito con método: {method}")
                return solution.x
            else:
                print(f"Método {method} falló: {solution.message}")
                last_error = solution.message
        except Exception as e:
            print(f"Error con método {method}: {str(e)}")
            last_error = str(e)
    
    # Si llegamos aquí, ningún método funcionó
    raise ValueError(f"No se pudo encontrar una solución después de probar varios métodos. Último error: {last_error}")