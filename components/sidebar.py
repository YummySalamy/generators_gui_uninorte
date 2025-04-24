import streamlit as st
import numpy as np

def render_sidebar():
    """
    Renderiza la barra lateral con todos los inputs necesarios
    
    Returns:
    --------
    dict
        Diccionario con todos los parámetros ingresados
    """
    st.sidebar.title("Parámetros de entrada")
    
    # Crear pestañas para los generadores y la carga
    tab1, tab2, tab3 = st.sidebar.tabs(["Generador 1", "Generador 2", "Carga"])
    
    # Generador 1
    with tab1:
        params_g1 = _generator_params("g1")
    
    # Generador 2
    with tab2:
        params_g2 = _generator_params("g2")
    
    # Carga
    with tab3:
        r_load = st.number_input("Resistencia de carga (Ω)", value=100.0, key="r_load")
        x_type = st.radio("Tipo de reactancia", ["Inductiva", "Capacitiva"])
        x_load_abs = st.number_input("Valor absoluto de reactancia (Ω)", value=50.0, key="x_load_abs")
        x_load = x_load_abs if x_type == "Inductiva" else -x_load_abs
        
        load_params = {
            "r_load": r_load,
            "x_load": x_load
        }
    
    # Retornar todos los parámetros
    return {
        "generator1": params_g1,
        "generator2": params_g2,
        "load": load_params
    }

def _generator_params(key_prefix):
    """Helper para crear inputs de un generador"""
    st.subheader("Parámetros del circuito equivalente")
    ra = st.number_input(f"Resistencia de armadura RA (Ω)", value=0.01, key=f"{key_prefix}_ra")
    xs = st.number_input(f"Reactancia síncrona XS (Ω)", value=0.1, key=f"{key_prefix}_xs")
    
    st.subheader("Valores nominales")
    s_nom = st.number_input(f"Potencia aparente nominal (VA)", value=10000.0, key=f"{key_prefix}_s_nom")
    v_nom = st.number_input(f"Tensión nominal (V)", value=440.0, key=f"{key_prefix}_v_nom")
    fp_nom = st.number_input(f"Factor de potencia nominal", value=0.8, key=f"{key_prefix}_fp_nom")
    poles = st.number_input(f"Número de polos", value=4, key=f"{key_prefix}_poles")
    
    st.subheader("Curva de magnetización")
    # Aquí podríamos usar un enfoque más avanzado como cargar datos de un archivo
    # Por ahora usaremos un enfoque simple
    num_points = st.slider("Número de puntos", 3, 10, 5, key=f"{key_prefix}_num_points")
    
    if_values = []
    ea_values = []
    
    for i in range(num_points):
        col1, col2 = st.columns(2)
        with col1:
            if_val = st.number_input(f"IF {i+1} (A)", value=i+1.0, key=f"{key_prefix}_if_{i}")
        with col2:
            ea_val = st.number_input(f"EA {i+1} (V)", value=(i+1)*100.0, key=f"{key_prefix}_ea_{i}")
        if_values.append(if_val)
        ea_values.append(ea_val)
    
    st.subheader("Punto de operación")
    f_sc = st.number_input(f"Frecuencia de vacío (Hz)", value=60.0, key=f"{key_prefix}_f_sc")
    if_op = st.number_input(f"Corriente de campo (A)", value=2.0, key=f"{key_prefix}_if_op")
    
    st.subheader("Pérdidas")
    p_core = st.number_input(f"Pérdidas en el núcleo (W)", value=100.0, key=f"{key_prefix}_p_core")
    p_friction = st.number_input(f"Pérdidas por fricción (W)", value=50.0, key=f"{key_prefix}_p_friction")
    p_misc = st.number_input(f"Pérdidas misceláneas (W)", value=30.0, key=f"{key_prefix}_p_misc")
    
    st.subheader("Motor primario")
    p_motor = st.number_input(f"Potencia del motor primario (W)", value=8000.0, key=f"{key_prefix}_p_motor")
    
    return {
        "ra": ra,
        "xs": xs,
        "s_nom": s_nom,
        "v_nom": v_nom,
        "fp_nom": fp_nom,
        "poles": poles,
        "if_values": if_values,
        "ea_values": ea_values,
        "f_sc": f_sc,
        "if_op": if_op,
        "p_core": p_core,
        "p_friction": p_friction,
        "p_misc": p_misc,
        "p_motor": p_motor
    }