
import streamlit as st

def show():

    import streamlit as st

    st.title("Database Overview")

    # Hydrogen LCA Calculator
    st.write(
        "The Hydrogen LCA Calculator was built using inventories collected from the literature for foreground activities and a list of available scenarios for background electricity markets. The foreground inventory can be accessed [here](Inventories), and it includes data for electrolyzers, balance of plant, treatment, storage, and distribution. The background inventory was brought to the foreground due to its significant contribution to the results. The calculator allows the user to select different scenarios for the electricity market in France in 2050. The repositories available contain the implementation of the prospective scenarios provided by the French Transmission System Operator - RTE.")

    # National Low-Carbon Strategy (NLCS)
    st.write(
        "France’s strategy for achieving carbon neutrality is laid out in its National Low-Carbon Strategy, or NLCS (Stratégie nationale bas-carbone – SNBC). The most recent version of this document, published in 2020, provided the framework for RTE’s 'Energy Pathways to 2050'. The scenarios explore a wide range of variants that allow carbon neutrality to be reached by 2050.")


    # Energy Pathways to 2050
    st.markdown("---")
    st.write("Energy Pathways to 2050 - Futurs énergétiques 2050 - FE2050")

    # RTE Demand Scenarios
    st.write("RTE provides 3 demand scenarios:")
    st.write("- Reference")
    st.write("- Extensive reindustrialization (higher demand compared to the reference scenario)")
    st.write("- Sobriety (lower demand compared to the reference scenario).")

    # RTE Electricity Production Scenarios
    st.write("For each demand scenario, RTE provides 6 electricity production scenarios:")
    st.write("- M0, M1, M23: These scenarios rely mostly on renewable development.")
    st.write("- N1, N2, N03: These scenarios rely on both renewables and nuclear development.")

    # Methodologies for Prospective Scenarios
    st.markdown("---")
    st.write("To model the prospective scenarios, two methodologies are available:")
    st.write(
        "- RTE Scenarios modeled with Premise + French imports of electricity provided by a regional IAM market for European electricity.")
    st.write(
        "- RTE Scenarios modeled according to current data available in EcoInvent + French imports of electricity modeled according to RTE's projections for DE, GB, IT, and ES and proxies for BE and CH.")

if __name__ == "__main__":
    show()