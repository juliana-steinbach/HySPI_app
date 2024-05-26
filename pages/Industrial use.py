from __future__ import annotations
from pathlib import Path
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import io
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
    data = {
        "Description": [
            "Impact using SMR ",
            "Impact using H2",
            "Impact savings"
        ],
        "[tCO2eq]": [
            f"{int(co2_impact_smr_tons)}",
            f"{int(co2_impact_hydrogen_tons)}",
            f"{int(difference_tons)}"
        ]
    }

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(data)
    df.set_index("Description", inplace=True)
    df.index.name = None
    col3.write("Total Ammonia produced in France: 1500t")
    col3.write(f"Selected Ammonia production: {total_production_tons / 1499:.2%}")
    col3.table(df)


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

    colored_header(
        label="Ammonia production technology",
        description="",
        color_name="blue-70",
    )

    # function to extract table from inventory and disply in page

    def extract_data(filename, sheet_name, item_name, columns, column_names):
        df = pd.read_excel(filename, sheet_name=sheet_name, header=None)
        line = df[df[1] == item_name].index

        line = line[0]

        line_amount = df[df[1] == "amount"].index
        line_amount = line_amount[line_amount > line][0]
        line_data = line_amount + 2
        table = []
        while True:
            try:
                value = df.iloc[line_data, 1]
                if pd.isnull(value):
                    break
                pd.to_numeric(value)
            except (ValueError, TypeError):
                break

            values = [df.iloc[line_data, i] for i in columns]
            table.append(values)
            line_data += 1

        df_final = pd.DataFrame(table, columns=column_names)

        # Convert all columns to scientific notation
        pd.set_option('display.float_format', lambda x: '%.2e' % x)

        # Alternatively, if you only want to convert specific columns:
        for column in column_names:
            df_final[column] = df_final[column].apply(lambda x: format(x, '.2e') if isinstance(x, (int, float)) else x)

        return df_final

    st.markdown("---")

    st.markdown("**Ammonia production via SMR**")

    st.write('''Amonia, ammonia, ammonia.''')

    ammonia_schema = ('ammonia smr.png')
    st.image(ammonia_schema, caption='')

    expander = st.expander("Ammonia from SMR")
    item_name = "ammonia production, steam reforming, liquid"
    column_names = ["Name", "Amount", "Location", "Unit", "Category", "Type"]
    columns = [0, 1, 2, 3, 4, 5]
    df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
    expander.table(df)

    expander = st.expander("Ammonia from hydrogen")
    item_name = "ammonia production, hydrogen, liquid"
    column_names = ["Name", "Amount", "Location", "Unit", "Category", "Type"]
    columns = [0, 1, 2, 3, 4, 5]
    df = extract_data('electrolyzers_LCI.xlsx', 'M1-2', item_name, columns, column_names)
    expander.table(df)

if __name__ == "__main__":
    main()
