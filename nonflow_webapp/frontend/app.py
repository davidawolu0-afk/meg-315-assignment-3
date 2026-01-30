import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Thermodynamic Process Lab", 
    page_icon="🌡️", 
    layout="wide"
)

# 2. Custom CSS for a "Tasteful" Look
st.markdown("""
    <style>
    /* Main background and font */
    .stApp {
        background-color: #fcfcfc;
    }
    /* Style the sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f0f2f6;
        border-right: 1px solid #e6e9ef;
    }
    /* Header styling */
    h1 {
        font-weight: 800;
        color: #1E3A8A;
        letter-spacing: -1px;
    }
    /* Card-like containers for charts */
    div[data-testid="column"] {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Header Section
st.title("🌡️ Non-Flow Process Calculator")
st.markdown("Analyze thermodynamic state changes using high-fidelity **CoolProp** data.")
st.divider()

# 4. Sidebar - Refined Inputs
with st.sidebar:
    st.header("⚙️ Configuration")
    
    with st.expander("Process Settings", expanded=True):
        process_type = st.selectbox(
            "Process Type",
            ["constant_volume", "constant_pressure", "isothermal", "adiabatic", "polytropic"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
    with st.expander("Initial States", expanded=True):
        col_side1, col_side2 = st.columns(2)
        T0 = col_side1.number_input("Temp (K)", value=300.0, step=10.0)
        V0 = col_side2.number_input("Vol (m³/kg)", value=1.0, step=0.1)
        
    n_points = st.select_slider("Resolution (Points)", options=[10, 20, 50, 100], value=20)
    
    st.divider()
    calculate_btn = st.button("🚀 Execute Calculation", use_container_width=True, type="primary")

# 5. Main Display Logic
# Process descriptions in a cleaner alert box
process_descriptions = {
    "constant_volume": "**Isochoric:** Volume remains constant while pressure changes with temperature.",
    "constant_pressure": "**Isobaric:** Pressure remains constant while volume changes with temperature.",
    "isothermal": "**Isothermal:** Temperature remains constant throughout the process.",
    "adiabatic": "**Adiabatic:** No heat transfer occurs ($P V^γ = C$).",
    "polytropic": "**Polytropic:** A generalized process model ($P V^n = C$)."
}

if not calculate_btn:
    st.info(process_descriptions[process_type])
    st.image("https://img.freepik.com/free-vector/blueprint-background-concept_23-2148507851.jpg", opacity=0.1) # Aesthetic placeholder

if calculate_btn:
    api_url = f"http://127.0.0.1:8000/process/{process_type}?T0={T0}&V0={V0}&n_points={n_points}"
    
    with st.spinner("Processing thermodynamic data..."):
        try:
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"**Backend Connection Error:** {e}")
            data = []

    if data:
        df = pd.DataFrame(data)
        
        # Plotly Theme Tweak
        chart_theme = dict(
            template="plotly_white",
            margin=dict(l=40, r=20, t=40, b=40)
        )

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("### 📈 Temperature-Entropy")
            fig1 = px.line(df, x="s", y="T", markers=True, 
                           color_discrete_sequence=['#1E3A8A'],
                           labels={"s": "Entropy (s)", "T": "Temperature (T)"})
            fig1.update_layout(chart_theme)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("### 📉 Pressure-Volume")
            fig2 = px.line(df, x="v", y="P", markers=True,
                           color_discrete_sequence=['#EF4444'],
                           labels={"v": "Specific Volume (v)", "P": "Pressure (P)"})
            fig2.update_layout(chart_theme)
            st.plotly_chart(fig2, use_container_width=True)

        # 6. Footer / Export Area
        st.divider()
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.success(f"Calculation complete for {process_type.replace('_', ' ')}.")
        with c3:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export CSV",
                data=csv,
                file_name=f"{process_type}_data.csv",
                mime="text/csv",
                use_container_width=True
        )
    
