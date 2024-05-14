from __future__ import annotations
from pathlib import Path
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

if "first_element_ammonia" not in st.session_state or st.session_state.first_element_ammonia is None:
    st.write("To apply hydrogen in its industrial use, please select the parameters in Calculator and compute the result")
    st.stop()

p = Path(__file__).parent / "iconsequential.csv"
INDUSTRY_DATA = pd.read_csv(p)

st.set_page_config(layout="wide") #initial_sidebar_state='collapsed'

def get_city_from_lat_lon(lat: float, lon: float) -> str:
    city_row = INDUSTRY_DATA[
        (INDUSTRY_DATA.latitude == lat) & (INDUSTRY_DATA.longitude == lon)
        ].iloc[0]
    return city_row["city"]


def get_production(city: str) -> int:
    return INDUSTRY_DATA.set_index("city").loc[city]["production"]


def main():
    st.write("# Industrial Hydrogen")
    if "selected_cities" not in st.session_state:
        st.session_state["selected_cities"] = [] #if I substitute this for ' ' the list does not get created

    if "selected_city" not in st.session_state:
        st.session_state["selected_city"] = []

    cities = INDUSTRY_DATA.groupby(["city", "latitude", "longitude"])

    # Create a layout with two columns
    col1, col2, col3 = st.columns([3, 2, 2])

    col1.write("### Ammonia production sites")
    col2.write("### Selected Cities")
    col3.write("### CO2 data")


    # Calculate total ammonia production in France
    total_production = sum(city_info['production'] for city_info in st.session_state["selected_cities"])

    # Retrieve CO2 impact values from session state and convert to float
    co2_impact_ammonia = float(st.session_state.first_element_ammonia)
    co2_impact_ammonia_smr = float(st.session_state.first_element_ammonia_smr)

    # Calculate and display total CO2 impact produced using SMR and hydrogen
    co2_impact_hydrogen = int(total_production * co2_impact_ammonia)
    co2_impact_smr = int(total_production * co2_impact_ammonia_smr)
    difference=co2_impact_smr - co2_impact_hydrogen

    total_production = sum(city_info['production'] for city_info in st.session_state["selected_cities"])

    with col1.container():
        # Create the map
        m = folium.Map(location=[46.903354, 2.188334], zoom_start=5)

        for (city, lat, lon), group in cities:
            custom1_icon = folium.features.CustomIcon(
                'https://i.ibb.co/3419K9D/ammonia-H-removebg-preview.png',  # URL of your custom icon image
                icon_size=(40, 40),  # Size of the icon image (width, height)
                icon_anchor=(15, 15),  # Anchor point of the icon (relative to its top-left corner)
            )
            custom2_icon = folium.features.CustomIcon(
                'https://i.ibb.co/Z63QyZv/ammonia.png',  # URL of your custom icon image
                icon_size=(30, 30),  # Size of the icon image (width, height)
                icon_anchor=(15, 15),  # Anchor point of the icon (relative to its top-left corner)
            )
            marker = folium.Marker(
                location=[lat, lon],
                tooltip=f"{city}",
                #icon=custom1_icon if city == st.session_state["selected_city"] else custom2_icon
                icon = custom1_icon if city in [c["city"] for c in st.session_state["selected_cities"]] else custom2_icon
            )
            marker.add_to(m)

        map = st_folium(
            m,
            width=400, height=350
        )

    total_production_tons = total_production / 1000
    co2_impact_smr_tons = co2_impact_smr / 1000
    co2_impact_hydrogen_tons = co2_impact_hydrogen / 1000
    difference_tons = difference / 1000

    col3.write(f"Total Ammonia Production in France: {total_production_tons} tons")
    col3.write(f"Total CO2 impact produced using SMR: {co2_impact_smr_tons} tons of CO2")
    col3.write(f"Total CO2 impact produced using hydrogen: {co2_impact_hydrogen_tons} tons of CO2")
    col3.write(f'Electrolysis can save {difference_tons} tons of CO2 per year in the Ammonia sector')

    col2.write("Select an Ammonia plant to substitute SMR with Electrolysis")
    if map["last_object_clicked"] != st.session_state.get("last_object_clicked"):
        st.session_state["last_object_clicked"] = map["last_object_clicked"]
        lat, lon = map["last_object_clicked"]["lat"], map["last_object_clicked"]["lng"] #why lon doesnt work?
        city = get_city_from_lat_lon(lat, lon)


        if city != st.session_state["selected_cities"]:
            city_exists = any(c["city"] == city for c in st.session_state["selected_cities"])#é aqui
            col2.write(f"You have selected '{city}', click the button below to confirm the selection")
            if col2.button("Confirm Selection"):
                # Update session state variable if the button is clicked
                st.session_state["confirmed_selection"] = True
            if not city_exists:
                #st.session_state["selected_city"] = city
                production = get_production(city)
                st.session_state["selected_cities"].append({"city": city, "production": production})

    for city_info in st.session_state["selected_cities"]:
        col2.write(f"- City: {city_info['city']}, Production: {city_info['production']}")




if __name__ == "__main__":
    main()
