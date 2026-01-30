import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# --- 1. CONFIGURATION & THEMING ---
st.set_page_config(
    page_title="ThermoCalc | Non-Flow Process",
    page_icon="🌡️",
    layout="wide"
)

# Custom CSS for a clean, modern look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://www.coolprop.org/_static/CoolPropLogo.png", width=150) # Assuming a logo fits the vibe
    st.header("⚙️ Configuration")
    
    with st.expander("Process Parameters", expanded=True):
        process_type = st.selectbox(
            "Process Type",
            ["constant_volume", "constant_pressure", "isothermal", "adiabatic", "polytropic"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        T0 = st.number_input("Initial Temp (K)", value=300.0, step=10.0)
        V0 = st.number_input("Init. Spec. Volume (m³/kg)", value=1.0, step=0.1)
        n_points = st.select_slider("Data Resolution", options=[10, 20, 50, 100], value=20)
    
    st.divider()
    calc_trigger = st.button("🚀 Calculate Process")

# --- 3. MAIN HEADER ---
col_head, col_logo = st.columns([4, 1])
with col_head:
    st.title("Thermodynamic Process Analysis")
    st.caption("Advanced Non-Flow Process Calculator powered by CoolProp & Plotly")

# --- 4. PROCESS DESCRIPTION ---
process_descriptions = {
    "constant_volume": "Isochoric Process: Volume remains constant while pressure varies linearly with temperature.",
    "constant_pressure": "Isobaric Process: Pressure is maintained constant as volume expands or contracts.",
    "isothermal": "Isothermal Process: Temperature remains constant; ideal for slow heat exchange models.",
    "adiabatic": "Adiabatic Process: No heat transfer ($Q=0$). Governed by $P v^\gamma = C$.",
    "polytropic": "Polytropic Process: A generalized thermodynamic model governed by $P v^n = C$."
}

st.info(f"**Current Selection:** {process_descriptions[process_type]}")

# --- 5. LOGIC & VISUALIZATION ---
if calc_trigger:
    api_url = f"http://127.0.0.1:8000/process/{process_type}?T0={T0}&V0={V0}&n_points={n_points}"
    
    with st.spinner("Synchronizing with Backend..."):
        try:
            # Added a slight delay feel or direct call
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            st.error(f"⚠️ Connection Failed: Ensure the FastAPI server is running at {api_url}")
            data = []

    if data:
        df = pd.DataFrame(data)
        
        # Dashboard style metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Start Pressure", f"{df['P'].iloc[0]:.2f} Pa")
        m2.metric("End Pressure", f"{df['P'].iloc[-1]:.2f} Pa")
        m3.metric("Entropy Change", f"{df['s'].iloc[-1] - df['s'].iloc[0]:.4f} J/kg·K")

        st.divider()

        # Visualization Grid
        chart_col1, chart_col2 = st.columns(2, gap="large")

        with chart_col1:
            st.subheader("📊 T-s Diagram")
            fig1 = px.line(df, x="s", y="T", markers=True, 
                           template="plotly_white", 
                           color_discrete_sequence=["#007bff"])
            fig1.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            st.subheader("📊 P-v Diagram")
            fig2 = px.line(df, x="v", y="P", markers=True, 
                           template="plotly_white",
                           color_discrete_sequence=["#ef4444"])
            fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)

        # Download Area
        st.divider()
        footer_col1, footer_col2 = st.columns([3, 1])
        with footer_col2:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Dataset (CSV)",
                data=csv,
                file_name=f"thermo_{process_type}.csv",
                mime="text/csv",
            )
else:
    # Empty state to keep the UI clean before calculation
    st.write("---")
    st.center = st.columns([1, 2, 1])[1].image("https://cdn-icons-png.flaticon.com/512/2622/2622271.png", width=100)
    st.columns([1, 4, 1])[1].markdown("<p style='text-align: center; color: grey;'>Configure parameters in the sidebar and click Calculate to generate diagrams.</p>", unsafe_allow_html=True)
