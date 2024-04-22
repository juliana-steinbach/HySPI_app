from __future__ import annotations
from pathlib import Path
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
#from pages.Calculator import calculate_result


p = Path(__file__).parent / "iconsequential.csv"
INDUSTRY_DATA = pd.read_csv(p)

st.set_page_config(layout="wide")

def get_city_from_lat_lon(lat: float, lon: float) -> str:
    city_row = INDUSTRY_DATA[
        (INDUSTRY_DATA.latitude == lat) & (INDUSTRY_DATA.longitude == lon)
        ].iloc[0]
    return city_row["city"]


def get_production(city: str) -> int:
    return INDUSTRY_DATA.set_index("city").loc[city]["production"]


def main():
    if "selected_cities" not in st.session_state:
        st.session_state["selected_cities"] = []

    if "selected_city" not in st.session_state:
        st.session_state["selected_city"] = None  # Set default selected city

    cities = INDUSTRY_DATA.groupby(["city", "latitude", "longitude"])

    # Create a layout with two columns
    col1, col2 = st.columns([2, 2])

    # Column 1: List of selected cities
    with col1:
        st.write("# Industrial Hydrogen")
        st.write("## Selected Cities")

        # Display the first number
        #st.write(calculate_result())

        total_production = sum(city_info['production'] for city_info in st.session_state["selected_cities"])
        st.write(f"Total Ammonia Production in France: {total_production}")
        for city_info in st.session_state["selected_cities"]:
            st.write(f"- City: {city_info['city']}, Production: {city_info['production']}")

    # Column 2: Map
    with col2:
        # Create the map
        m = folium.Map(location=[46.903354, 1.888334], zoom_start=5)

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
                icon=custom1_icon if city == st.session_state["selected_city"] else custom2_icon
            )
            marker.add_to(m)

        out = st_folium(
            m,
            width=400,
            height=350,
        )

        if out["last_object_clicked"] != st.session_state.get("last_object_clicked"):
            st.session_state["last_object_clicked"] = out["last_object_clicked"]
            lat, lon = out["last_object_clicked"]["lat"], out["last_object_clicked"]["lng"]
            city = get_city_from_lat_lon(lat, lon)

            # Check if the city is already selected
            if city != st.session_state["selected_city"]:
                # Check if the city is already in the list of selected cities
                city_exists = any(c["city"] == city for c in st.session_state["selected_cities"])
                st.write(f"you have selected '{city}', click anywhere on the map to add it to your list")
                if not city_exists:
                    st.session_state["selected_city"] = city
                    production = get_production(city)

                    # Append selected city and its production to the list
                    st.session_state["selected_cities"].append({"city": city, "production": production})


if __name__ == "__main__":
    main()
