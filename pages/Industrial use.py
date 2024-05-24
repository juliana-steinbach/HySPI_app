from __future__ import annotations
from pathlib import Path
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from streamlit_extras.colored_header import colored_header

if "first_element_ammonia" not in st.session_state or st.session_state.first_element_ammonia is None:
    st.write("To apply hydrogen in its industrial use, please select the parameters in Calculator and compute the result")
    st.stop()

p = Path(__file__).parent / "iconsequential.csv"
INDUSTRY_DATA = pd.read_csv(p)

st.set_page_config(layout="wide")  # initial_sidebar_state='collapsed'

for k, v in st.session_state.items():
    st.session_state[k] = v

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
        st.session_state["selected_cities"] = []

    cities = INDUSTRY_DATA.groupby(["city", "latitude", "longitude"])

    col1, col2, col3 = st.columns([3, 2, 2])

    with col1.container():
        colored_header(
            label="Ammonia plant",
            description="",
            color_name="blue-70",
        )
        st.write("Click on the ammonia plants to switch from SMR H2 to electrolysis H2")
    with col2.container():
        colored_header(
            label="Selected Cities",
            description="",
            color_name="blue-70",
        )
    with col3.container():
        colored_header(
            label="CO2 data",
            description="",
            color_name="blue-70",
        )

    total_production = sum(city_info['production'] for city_info in st.session_state["selected_cities"])

    co2_impact_ammonia = float(st.session_state.first_element_ammonia)
    co2_impact_ammonia_smr = float(st.session_state.first_element_ammonia_smr)

    co2_impact_hydrogen = float(total_production * co2_impact_ammonia)
    co2_impact_smr = float(total_production * co2_impact_ammonia_smr)
    difference = co2_impact_smr - co2_impact_hydrogen

    with col1.container():
        m = folium.Map(location=[46.903354, 2.188334], zoom_start=5)

        for (city, lat, lon), group in cities:
            custom1_icon = folium.features.CustomIcon(
                'https://i.ibb.co/3419K9D/ammonia-H-removebg-preview.png',
                icon_size=(40, 40),
                icon_anchor=(15, 15),
            )
            custom2_icon = folium.features.CustomIcon(
                'https://i.ibb.co/Z63QyZv/ammonia.png',
                icon_size=(30, 30),
                icon_anchor=(15, 15),
            )
            marker = folium.Marker(
                location=[lat, lon],
                tooltip=f"{city}",
                icon=custom1_icon if city in [c["city"] for c in st.session_state["selected_cities"]] else custom2_icon
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

    #col3.write(f"Total Ammonia produced in France: 1500 tons")
    #col3.write(f"Selected Ammonia production: {total_production_tons/1500:.2%} tons")
    #col3.write(f"Total CO2 impact produced using SMR: {int(co2_impact_smr_tons)} tons of CO2")
    #col3.write(f"Total CO2 impact produced using hydrogen: {int(co2_impact_hydrogen_tons)} tons of CO2")
    #col3.write(f'Electrolysis can save {int(difference_tons)} tons of CO2 per year in the Ammonia sector')
    # Dados organizados em listas
    descriptions = [
        "Total Ammonia produced in France [t]",
        "Selected Ammonia production",
        "",
        "Impact produced using SMR",
        "Impact produced using hydrogen",
        "Impact reduction"
    ]

    values = [
            "1500",
            f"{total_production_tons / 1499:.2%}",
            "[tCO2eq]",
            f"{int(co2_impact_smr_tons)}",
            f"{int(co2_impact_hydrogen_tons)}",
            f"{int(difference_tons)}"
        ]

    data = list(zip(descriptions, values))
    df = pd.DataFrame(data, columns=["", ""])


    col3.write(df.to_html(index=False, header=False), unsafe_allow_html=True)

    if map["last_object_clicked"] != st.session_state.get("last_object_clicked"):
        st.session_state["last_object_clicked"] = map["last_object_clicked"]
        lat, lon = map["last_object_clicked"]["lat"], map["last_object_clicked"]["lng"]
        city = get_city_from_lat_lon(lat, lon)

        # Initialize previously clicked cities if it doesn't exist
        if "previously_clicked_cities" not in st.session_state:
            st.session_state["previously_clicked_cities"] = set()

        # Check if the city is already in the selected cities list
        city_exists = any(c["city"] == city for c in st.session_state["selected_cities"])

        # Check if the city was previously clicked
        if city not in st.session_state["previously_clicked_cities"]:
            st.session_state["previously_clicked_cities"].add(city)
            col2.write(f"You have selected '{city}', click the button below to confirm the selection")
            if col2.button("Confirm Selection"):
                st.session_state["confirmed_selection"] = True
            if not city_exists:
                production = get_production(city)
                st.session_state["selected_cities"].append({"city": city, "production": production})

    for city_info in st.session_state["selected_cities"]:
        col2.write(f"- City: {city_info['city']}, Production: {city_info['production']}")

    st.write("# Ammonia production")

    ammonia_schema = ('ammonia smr.png')
    st.image(ammonia_schema, caption='')

if __name__ == "__main__":
    main()
