import streamlit as st
from components.sidebar import render_sidebar
from components.results import render_results
from components.plots import render_magnetization_curve, render_capability_curve
from models.system import GeneratorSystem

def main():
    st.set_page_config(
        page_title="Generadores Síncronos en Paralelo",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Simulador de Generadores Síncronos en Paralelo")
    
    # Cargar parámetros desde la barra lateral
    params = render_sidebar()
    
    # Inicializar el sistema con los parámetros
    system = GeneratorSystem(params)
    
    # Resolver el sistema cuando se presione el botón
    if st.button("Calcular"):
        with st.spinner("Calculando..."):
            results = system.solve()
            
            # Mostrar resultados
            render_results(results)
            
            # Mejorar presentación de gráficas
            st.header("Curvas de Generadores")
            
            # Usar pestañas para separar las gráficas de cada generador
            tab1, tab2 = st.tabs(["Generador 1", "Generador 2"])
            
            with tab1:
                st.subheader("Generador 1")
                col1, col2 = st.columns(2)
                with col1:
                    render_magnetization_curve(system.generator1, results["op_point_g1"], "Generador 1")
                with col2:
                    render_capability_curve(system.generator1, results["op_point_g1"], "Generador 1")
            
            with tab2:
                st.subheader("Generador 2")
                col1, col2 = st.columns(2)
                with col1:
                    render_magnetization_curve(system.generator2, results["op_point_g2"], "Generador 2")
                with col2:
                    render_capability_curve(system.generator2, results["op_point_g2"], "Generador 2")

if __name__ == "__main__":
    main()