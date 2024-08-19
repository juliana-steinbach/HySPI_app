import streamlit as st
from utils import some_func, get_pv_prod_data
from layout import setup_layout, display_hydrogen_production
from tooltip import add_tooltips
from calculation import calculate_hydrogen_production

def main():
    st.set_page_config(layout="wide")
    st.markdown("# HySPI Calculator")

    some_func()  # Example usage of a utility function

    # Set up the layout and capture user input
    inputs = setup_layout()

    # Perform calculations
    H2_year = calculate_hydrogen_production(*inputs)

    # Add tooltips
    add_tooltips()

    # Display results
    display_hydrogen_production(H2_year)

if __name__ == "__main__":
    main()
