import streamlit as st
import plotly.graph_objects as go
import numpy as np

def render_magnetization_curve(generator, op_point, title_prefix=""):
    """
    Renderiza la curva de magnetización interactiva con el punto de operación usando Plotly
    
    Parameters:
    -----------
    generator : SynchronousGenerator
        Generador síncrono
    op_point : dict
        Punto de operación (contiene IF y EA)
    title_prefix : str
        Prefijo para el título (opcional)
    """
    title = "Curva de Magnetización"
    if title_prefix:
        title = f"{title_prefix} - {title}"
        
    st.subheader(title)
    
    # Crear puntos para la curva
    if_range = np.linspace(
        min(generator.if_values) * 0.9,
        max(generator.if_values) * 1.1, 
        100
    )
    ea_range = [generator.get_ea_from_if(if_val) for if_val in if_range]
    
    # Crear figura de Plotly
    fig = go.Figure()
    
    # Añadir la curva de magnetización
    fig.add_trace(go.Scatter(
        x=if_range,
        y=ea_range,
        mode='lines',
        name='Curva de magnetización',
        line=dict(color='blue', width=2)
    ))
    
    # Añadir el punto de operación
    fig.add_trace(go.Scatter(
        x=[op_point["if"]],
        y=[op_point["ea"]],
        mode='markers',
        name='Punto de operación',
        marker=dict(
            color='red',
            size=12,
            line=dict(
                color='black',
                width=1
            )
        ),
        hoverinfo='text',
        hovertext=f'IF: {op_point["if"]:.2f} A<br>EA: {op_point["ea"]:.2f} V'
    ))
    
    # Configurar el layout
    fig.update_layout(
        title=title,
        xaxis_title="Corriente de campo (A)",
        yaxis_title="Fuerza electromotriz (V)",
        hovermode='closest',
        template='plotly_white',
        width=600,
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Añadir cuadrícula
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    # Mostrar la figura
    st.plotly_chart(fig, use_container_width=True)

def render_capability_curve(generator, op_point, title_prefix=""):
    """
    Renderiza la curva de capacidad interactiva con el punto de operación usando Plotly
    
    Parameters:
    -----------
    generator : SynchronousGenerator
        Generador síncrono
    op_point : dict
        Punto de operación (contiene P y Q)
    title_prefix : str
        Prefijo para el título (opcional)
    """
    title = "Curva de Capacidad"
    if title_prefix:
        title = f"{title_prefix} - {title}"
        
    st.subheader(title)
    
    # Definir colores
    color_termica = 'red' if title_prefix == "Generador 1" else 'crimson'
    color_excitacion = 'green' if title_prefix == "Generador 1" else 'darkgreen'
    color_estabilidad = 'blue' if title_prefix == "Generador 1" else 'navy'
    
    # Crear figura de Plotly
    fig = go.Figure()
    
    # Límites de la curva de capacidad
    # Límite de corriente de armadura (círculo)
    p_range = np.linspace(-generator.s_nom, generator.s_nom, 200)
    q_max = np.sqrt(generator.s_nom**2 - p_range**2)
    q_min = -q_max
    
    # Límite de corriente de campo (semicírculo superior)
    p_field_range = np.linspace(0, generator.s_nom, 100)
    q_field_limit = np.sqrt((0.8*generator.s_nom)**2 - p_field_range**2)
    
    # Límite de estabilidad (línea vertical)
    p_stability = 0.9 * generator.s_nom
    q_stability = np.linspace(-generator.s_nom, generator.s_nom, 50)
    
    # Añadir límite térmico (armadura)
    fig.add_trace(go.Scatter(
        x=p_range,
        y=q_max,
        mode='lines',
        name='Límite térmico (armadura)',
        line=dict(color=color_termica, width=2),
        hoverinfo='none'
    ))
    
    fig.add_trace(go.Scatter(
        x=p_range,
        y=q_min,
        mode='lines',
        showlegend=False,
        line=dict(color=color_termica, width=2),
        hoverinfo='none'
    ))
    
    # Añadir límite de excitación
    fig.add_trace(go.Scatter(
        x=p_field_range,
        y=q_field_limit,
        mode='lines',
        name='Límite de excitación',
        line=dict(color=color_excitacion, width=2),
        hoverinfo='none'
    ))
    
    # Añadir límite de estabilidad
    fig.add_trace(go.Scatter(
        x=[p_stability] * len(q_stability),
        y=q_stability,
        mode='lines',
        name='Límite de estabilidad',
        line=dict(color=color_estabilidad, width=2),
        hoverinfo='none'
    ))
    
    # Añadir líneas de factor de potencia nominal
    fp_angle = np.arccos(generator.fp_nom)
    p_fp = np.linspace(0, generator.s_nom * 1.2, 100)
    q_fp_ind = p_fp * np.tan(fp_angle)
    q_fp_cap = -p_fp * np.tan(fp_angle)
    
    fig.add_trace(go.Scatter(
        x=p_fp,
        y=q_fp_ind,
        mode='lines',
        name=f'FP = {generator.fp_nom} ind',
        line=dict(color='black', width=1, dash='dash'),
        hoverinfo='none'
    ))
    
    fig.add_trace(go.Scatter(
        x=p_fp,
        y=q_fp_cap,
        mode='lines',
        name=f'FP = {generator.fp_nom} cap',
        line=dict(color='black', width=1, dash='dot'),
        hoverinfo='none'
    ))
    
    # Añadir punto de operación
    fig.add_trace(go.Scatter(
        x=[op_point["p"]],
        y=[op_point["q"]],
        mode='markers',
        name='Punto de operación',
        marker=dict(
            color='red',
            size=12,
            line=dict(color='black', width=1)
        ),
        hoverinfo='text',
        hovertext=(f'P: {op_point["p"]:.2f} W<br>'
                  f'Q: {op_point["q"]:.2f} VAr<br>'
                  f'S: {np.sqrt(op_point["p"]**2 + op_point["q"]**2):.2f} VA<br>'
                  f'FP: {op_point["p"]/np.sqrt(op_point["p"]**2 + op_point["q"]**2):.3f}')
    ))
    
    # Configurar el layout
    fig.update_layout(
        title=title,
        xaxis_title="Potencia Activa P (W)",
        yaxis_title="Potencia Reactiva Q (VAr)",
        hovermode='closest',
        template='plotly_white',
        width=600,
        height=500,
        xaxis=dict(scaleanchor="y", scaleratio=1),  # Mantener proporciones 1:1
        yaxis=dict(autorange=True),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Añadir cuadrícula
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray', zeroline=True, zerolinewidth=1, zerolinecolor='gray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray', zeroline=True, zerolinewidth=1, zerolinecolor='gray')
    
    # Mostrar la figura
    st.plotly_chart(fig, use_container_width=True)