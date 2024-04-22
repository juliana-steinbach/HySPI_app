import streamlit as st
import pandas as pd
from folium import Map, Marker
from streamlit_folium import folium_static
from IPython.display import display, HTML
from pathlib import Path

# Define the function to show Folium map in Streamlit
def folium_deepnote_show(m):
    data = m._repr_html_()
    data_fixed_height = data.replace('width: 100%;height: 100%', 'width: 100%').replace('height: 100.0%;', 'height: 609px;', 1)
    st.components.v1.html(data_fixed_height, width=800, height=600)

# Load the CSV file
p = Path(__file__).parent / "iconsequential.csv"
data = pd.read_csv(p)

# Main function
def main():
    st.title("Interactive Map Example")


    # Create a folium map centered on France
    m = Map(location=[46.603354, 1.888334], zoom_start=6)

    # Add markers for each city
    for i, row in data.iterrows():
        Marker([row['latitude'], row['longitude']], tooltip=row['city']).add_to(m)

    # Display the map
    folium_deepnote_show(m)

    # Add button to retrieve places
    clicked = st.button("Click me to retrieve places!")

    if clicked:
        selected_places = data[['city', 'latitude', 'longitude']]
        st.write(selected_places)

if __name__ == "__main__":
    main()
