import streamlit as st
import pandas as pd
import numpy as np

def render_results(results):
    """
    Renderiza los resultados del cálculo en una tabla
    
    Parameters:
    -----------
    results : dict
        Diccionario con todos los resultados calculados
    """
    st.header("Resultados del Cálculo")
    
    # Crear pestañas para mostrar resultados por categoría
    tab1, tab2, tab3 = st.tabs(["Generador 1", "Generador 2", "Sistema y Carga"])
    
    with tab1:
        render_generator_results(results, "g1")
    
    with tab2:
        render_generator_results(results, "g2")
    
    with tab3:
        render_load_results(results)

def render_generator_results(results, gen_key):
    """Muestra los resultados de un generador específico"""
    # Extraer prefijo apropiado para las claves
    prefix = "g1_" if gen_key == "g1" else "g2_"
    title = "Generador 1" if gen_key == "g1" else "Generador 2"
    
    st.subheader(f"Resultados de {title}")
    
    # Crear dataframes para diferentes categorías de resultados
    corrientes_df = pd.DataFrame({
        "Parámetro": ["Corriente de Armadura (IA)", "Corriente de Línea (IL)", "Corriente de Campo (IF)"],
        "Magnitud": [
            f"{abs(results[prefix+'ia']):.4f} A",
            f"{abs(results[prefix+'il']):.4f} A",
            f"{results[prefix+'if']:.4f} A"
        ],
        "Ángulo": [
            f"{np.angle(results[prefix+'ia'], deg=True):.2f}°",
            f"{np.angle(results[prefix+'il'], deg=True):.2f}°",
            "N/A"
        ]
    })
    
    tensiones_df = pd.DataFrame({
        "Parámetro": ["Fuerza Electromotriz (EA)", "Tensión Terminal (VT)", "Tensión de Fase (Vφ)"],
        "Magnitud": [
            f"{abs(results[prefix+'ea']):.4f} V",
            f"{abs(results[prefix+'vt']):.4f} V",
            f"{abs(results[prefix+'vf']):.4f} V"
        ],
        "Ángulo": [
            f"{np.angle(results[prefix+'ea'], deg=True):.2f}°",
            f"{np.angle(results[prefix+'vt'], deg=True):.2f}°",
            f"{np.angle(results[prefix+'vf'], deg=True):.2f}°"
        ]
    })
    
    potencias_df = pd.DataFrame({
        "Parámetro": ["Potencia Activa (P)", "Potencia Reactiva (Q)", "Potencia Aparente (S)"],
        "Valor": [
            f"{results[prefix+'p']:.4f} W",
            f"{results[prefix+'q']:.4f} VAr",
            f"{results[prefix+'s']:.4f} VA"
        ]
    })
    
    otros_df = pd.DataFrame({
        "Parámetro": [
            "Ángulo del Par (δ)", 
            "Torque Inducido (Tind)", 
            "Torque Aplicado (Tap)",
            "Velocidad Síncrona (ωsinc)",
            "Frecuencia Eléctrica (fe)",
            "Pérdidas en el Cobre (PCu)"
        ],
        "Valor": [
            f"{results[prefix+'delta']:.4f}°",
            f"{results[prefix+'tind']:.4f} N·m",
            f"{results[prefix+'tap']:.4f} N·m",
            f"{results[prefix+'omega_sinc']:.4f} rad/s",
            f"{results[prefix+'fe']:.4f} Hz",
            f"{results[prefix+'pcu']:.4f} W"
        ]
    })
    
    # Mostrar las tablas
    st.subheader("Corrientes")
    st.table(corrientes_df)
    
    st.subheader("Tensiones")
    st.table(tensiones_df)
    
    st.subheader("Potencias")
    st.table(potencias_df)
    
    st.subheader("Otros Parámetros")
    st.table(otros_df)

def render_load_results(results):
    """Muestra los resultados relacionados con la carga y el sistema completo"""
    st.subheader("Carga")
    
    load_df = pd.DataFrame({
        "Parámetro": [
            "Corriente de Carga (Icarga)",
            "Potencia Activa Consumida (Pcarga)",
            "Potencia Reactiva Consumida (Qcarga)",
            "Potencia Aparente Consumida (Scarga)",
            "Factor de Potencia de la Carga"
        ],
        "Valor": [
            f"{abs(results['i_load']):.4f} A",
            f"{results['p_load']:.4f} W",
            f"{results['q_load']:.4f} VAr",
            f"{results['s_load']:.4f} VA",
            f"{results['fp_load']:.4f}"
        ]
    })
    
    st.table(load_df)
    
    st.subheader("Sistema Completo")
    
    system_df = pd.DataFrame({
        "Parámetro": [
            "Tensión del Bus (VT)",
            "Frecuencia del Sistema (f)",
            "Potencia Total Generada (Ptotal)",
            "Potencia Reactiva Total Generada (Qtotal)",
            "Pérdidas Totales"
        ],
        "Valor": [
            f"{abs(results['vt']):.4f} V",
            f"{results['f']:.4f} Hz",
            f"{results['p_total']:.4f} W",
            f"{results['q_total']:.4f} VAr",
            f"{results['losses_total']:.4f} W"
        ]
    })
    
    st.table(system_df)
    
    # Distribución de potencia entre generadores
    st.subheader("Distribución de Potencia")
    
    p_g1 = results["g1_p"]
    p_g2 = results["g2_p"]
    p_total = p_g1 + p_g2
    
    q_g1 = results["g1_q"]
    q_g2 = results["g2_q"]
    q_total = q_g1 + q_g2
    
    distribution_df = pd.DataFrame({
        "Generador": ["Generador 1", "Generador 2", "Total"],
        "Potencia Activa (W)": [f"{p_g1:.4f}", f"{p_g2:.4f}", f"{p_total:.4f}"],
        "Potencia Reactiva (VAr)": [f"{q_g1:.4f}", f"{q_g2:.4f}", f"{q_total:.4f}"],
        "% Activa": [f"{(p_g1/p_total)*100:.2f}%", f"{(p_g2/p_total)*100:.2f}%", "100%"],
        "% Reactiva": [f"{(q_g1/q_total)*100:.2f}%", f"{(q_g2/q_total)*100:.2f}%", "100%"]
    })
    
    st.table(distribution_df)