import streamlit as st

def setup_layout():
    # Create layout and return inputs for calculation
    st.columns([1, 1, 1])
    col1, col2, col3 = st.columns([1, 1, 1])

    stack_type = col1.selectbox("Electrolyzer stack:", ["PEM", "AEC"])
    electro_capacity_MW = col2.number_input("Electrolyzer capacity (MW):", value=20, min_value=1, step=1)
    stack_LT = col3.number_input("Stack lifetime (h):", value=120000, min_value=1, step=1)
    BoP_LT_y = col1.number_input("Balance of Plant lifetime (years):", value=20, min_value=1, step=1)
    eff = col2.number_input("Stack efficiency (0 to 1):", value=0.72, min_value=0.0, max_value=1.0, step=0.01)
    cf = col3.number_input("Capacity factor (0 to 1):", value=0.95, min_value=0.01, max_value=1.00, step=0.05)
    transp = col3.selectbox("Transport method", ["Pipeline", "Truck"], index=0)
    renewable_coupling = col1.selectbox("Photovoltaic coupled?", ["Yes", "No"], index=1)
    storage_choice = col2.selectbox("Storage", ["Tank", "No storage"], index=1)

    return electro_capacity_MW, cf, eff  # Return necessary inputs for calculation

def display_hydrogen_production(H2_year):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'<div style="padding: 5px; margin: 10px; border: 1px solid #cccccc; border-radius: 5px;"><b>Hydrogen production:</b> {H2_year/1000:.2f} t/year</div>',
                    unsafe_allow_html=True)
