from io import BytesIO
import lca_algebraic as agb
from lca_algebraic import *
import folium
import pandas as pd
from streamlit_folium import st_folium
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from streamlit_extras.colored_header import colored_header
import time
from opencage.geocoder import OpenCageGeocode
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from lib.utils import some_func, get_pv_prod_data, INTERVAL_H



def show():
    import streamlit as st #error if removed from here, why? dnt know....

    st.set_page_config(layout="wide")

    st.markdown("# HySPI Calculator")

    some_func()

    colored_header(
        label="Foreground",
        description="Parameters extracted directly from your production plant",
        color_name="blue-70",
    )


    col1, col2, col3 = st.columns([1, 1, 1])

    #Forefround questions
    stack_type = col1.selectbox("Electrolyzer stack:", ["PEM", "AEC"])
    electro_capacity_MW = col2.number_input("Electrolyzer capacity (MW):", value=20, min_value=1, step=1)
    stack_LT = col3.number_input("Stack lifetime (h):", value=120000, min_value=1, step=1)
    BoP_LT_y = col1.number_input("Balance of Plant lifetime (years):", value=20, min_value=1, step=1)
    eff = col2.number_input("Stack efficiency (0 to 1):", value=0.72, min_value=0.0, max_value=1.0, step=0.01)
    cf = col3.number_input("Capacity factor (0 to 1):", value=0.95, min_value=0.01, max_value=1.00, step=0.05)
    transp = col3.selectbox("Transport method", ["Pipeline", "Truck"], index=0)
    renewable_coupling = col1.selectbox("Photovoltaic coupled?", ["Yes", "No"], index=1)
    storage_choice = col2.selectbox("Storage", ["Tank", "No storage"], index=1)

    electro_capacity_kW = electro_capacity_MW*1_000
    electro_capacity_W = electro_capacity_kW*1_000
    BoP_LT_h = BoP_LT_y * 365 * 24
    Electricity_consumed_kWh = BoP_LT_y * 365 * 24 * cf * electro_capacity_kW
    Ec_kWh = int(Electricity_consumed_kWh)
    Ec_MWh = Ec_kWh / 1_000 # Convert kWh to MWh
    Ec_GWh = Ec_kWh / 1_000_000  # Convert kWh to GWh
    # Higher heating value
    HHV_kWhkg = 39.4  # kWh/kg

    H2_year = 365 * 24 * cf * electro_capacity_kW * eff / HHV_kWhkg #24h

    # Help tooltips with data from IEA for stack and efficiency
    st.markdown("""
                <style>
                    /* Importando o CSS do Font Awesome */
                    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css');
                </style>
            """, unsafe_allow_html=True)

    tooltip_html = """
                <div class="tooltip">
                    <span class="tooltiptext">
                        <table>
                            <thead>
                                <tr>
                                    <th></th>
                                    <th colspan='2'>AEC</th>
                                    <th colspan='2'>PEM</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td></td><td>Current,&nbsp;2019</td><td>Future,&nbsp;2050</td><td>Current,&nbsp;2019</td><td>Future,&nbsp;2050</td></tr>
                                <tr><td>Stack lifetime (operating hours)</td><td>60000-90000</td><td>100000-150000</td><td>30000-90000</td><td>100000-150000</td></tr>
                            </tbody>
                        </table>
                        <p>source: IEA, The Future of Hydrogen - Seizing today’s opportunities, International Energy Agency, 2019.</p>
                    </span>
                    <span id="tooltip_trigger">Need help with prospective Stack lifetime data? Check this info  <i class="fas fa-lightbulb"></i></span>
                </div>
            """


    # JavaScript and CSS to show tooltip
    js_code = """
            <script>
                // Add event listener to show tooltip on mouseover
                document.getElementById("tooltip_trigger").addEventListener("mouseover", function() {
                    var tooltipText = document.querySelector(".tooltiptext");
                    tooltipText.style.visibility = "visible";
                });

                // Add event listener to hide tooltip on mouseout
                document.getElementById("tooltip_trigger").addEventListener("mouseout", function() {
                    var tooltipText = document.querySelector(".tooltiptext");
                    tooltipText.style.visibility = "hidden";
                });
            </script>
            """

    css_code = """
            <style>
                .tooltip {
                    position: relative;
                    display: inline-block;
                    cursor: help;
                }

                .tooltiptext {
                    visibility: hidden;
                    width: 800px;
                    background-color: white;
                    color: black;
                    text-align: left;
                    border-radius: 6px;
                    padding: 10px;
                    position: absolute;
                    z-index: 1;
                    top: 125%;
                    left: 0;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                    opacity: 1; /* Make the tooltip non-transparent */
                }

                .tooltip:hover .tooltiptext {
                    visibility: visible;
                }
            </style>
            """

    # Define the HTML content for the tooltip
    tooltip_html2 = """
                <div class="tooltip">
                    <span class="tooltiptext">
                        <table>
                            <thead>
                                <tr>
                                    <th></th>
                                    <th colspan='2'>AEC</th>
                                    <th colspan='2'>PEM</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td></td><td>Current,&nbsp;2019</td><td>Future,&nbsp;2050</td><td>Current,&nbsp;2019</td><td>Future,&nbsp;2050</td></tr>
                                <tr><td>Electrical efficiency (%LHV)</td><td>63-70</td><td>70-80</td><td>56-60</td><td>67-74</td></tr>
                            </tbody>
                        </table>
                        <p>source: IEA, The Future of Hydrogen - Seizing today’s opportunities, International Energy Agency, 2019.</p>
                    </span>
                    <span id="tooltip_trigger">Need help with prospective Stack efficiency data? Check this info  <i class="fas fa-lightbulb"></i></span>
                </div>
            """

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f'{tooltip_html}', unsafe_allow_html=True)
        st.markdown(f'{tooltip_html2}', unsafe_allow_html=True)
    with col2:
        st.markdown(
            f'<div style="padding: 5px; margin: 10px; border: 1px solid #cccccc; border-radius: 5px;"><b>Hydrogen production:</b> {H2_year/1000:.2f} t/year</div>',
            unsafe_allow_html=True)

    # JavaScript and CSS to show tooltip
    js_code = """
            <script>
                // Add event listener to show tooltip on mouseover
                document.getElementById("tooltip_trigger").addEventListener("mouseover", function() {
                    var tooltipText = document.querySelector(".tooltiptext");
                    tooltipText.style.visibility = "visible";
                });

                // Add event listener to hide tooltip on mouseout
                document.getElementById("tooltip_trigger").addEventListener("mouseout", function() {
                    var tooltipText = document.querySelector(".tooltiptext");
                    tooltipText.style.visibility = "hidden";
                });
            </script>
            """

    css_code = """
            <style>
                .tooltip {
                    position: relative;
                    display: inline-block;
                    cursor: help;
                }

                .tooltiptext {
                    visibility: hidden;
                    width: 700px;
                    background-color: white;
                    color: black;
                    text-align: left;
                    border-radius: 6px;
                    padding: 10px;
                    position: absolute;
                    z-index: 1;
                    top: 125%;
                    left: 0;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                    opacity: 1; /* Make the tooltip non-transparent */
                }

                .tooltip:hover .tooltiptext {
                    visibility: visible;
                }
            </style>
            """

    # Add JavaScript and CSS to the page
    st.markdown(js_code, unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)

    data = None  # Initialize data with a default value
    if renewable_coupling == "Yes":
        colored_header(
            label="Photovoltaic system",
            description="Select the location and PV capacity",
            color_name="blue-70",
        )

        import streamlit as st
        from opencage.geocoder import OpenCageGeocode
        import folium
        from streamlit_folium import st_folium

        if 'data' not in st.session_state:
            st.session_state["last_clicked"]=""
        if 'data' not in st.session_state:
            st.session_state["latlon"]=""
        if 'data' not in st.session_state:
            st.session_state["city_name"]=""


        # Initialize OpenCage geocoder with your API key
        API_KEY = '8dd1a5bd80ce401a8fee652c805092cc'
        geocoder = OpenCageGeocode(API_KEY)

        def get_pos(lat, lng):
            return lat, lng

        def get_city_coordinates(city_name):
            query = f'{city_name}, France'
            results = geocoder.geocode(query)
            if results and len(results):
                # Get the latitude and longitude values
                lat = results[0]['geometry']['lat']
                lng = results[0]['geometry']['lng']

                # Round the latitude and longitude to 4 decimal places
                rounded_lat = round(lat, 4)
                rounded_lng = round(lng, 4)

                return rounded_lat, rounded_lng
            else:
                return None

        st.write("#### Enter a location or select one on the map")
        with st.container():
            col1, col2, col3= st.columns([1, 1, 1])


            with col1:
                city_name = st.text_input("Enter city name:", placeholder="Fos-sur-Mer")
                st.write("or")
                latlon = st.text_input("Enter latitude and longitude :",placeholder="e.g.: 43.4380, 4.9455", type="default")
                if latlon:
                    city_lat, city_lon = map(float, latlon.split(','))

            # Create a Folium map
            m = folium.Map(location=[46.903354, 2.088334], zoom_start=5)
            m.add_child(folium.LatLngPopup())

            if city_name:  # Check if city name is entered
                data = get_city_coordinates(city_name)
                if data:
                    folium.Marker(location=data).add_to(m)
                    #m.location=data in case we want to use for the rest of europe
                
            if latlon:  # Check if latitude and longitude are entered
                data = (city_lat, city_lon)
                folium.Marker(location=data).add_to(m)
                m.fit_bounds([data])

            with col2:
                # When the user interacts with the map
                map_data = st_folium(
                    m,
                    width = 270,
                    height=290,
                    key="folium_map"
                )

                if map_data.get("last_clicked"):
                    # Round the latitude and longitude to 4 decimal places
                    lat = round(map_data["last_clicked"]["lat"], 4)
                    lng = round(map_data["last_clicked"]["lng"], 4)

                    # Get the position using the rounded values
                    data = get_pos(lat, lng)

                    # Add the marker to the map
                    folium.Marker(location=data).add_to(m)

            col1.write("")
            col1.markdown(f'<div style="padding: 5px; margin: 10px; border: 1px solid #cccccc; border-radius: 5px;"><b>Location selected:</b> {data}</div>', unsafe_allow_html=True)

            col3.write("")
            pv_logo = "pv logo.png"
            col3.image(pv_logo, caption='', width= 200)
            col3.markdown("Solar radiation data was extracted from the PVGIS webapp. It consists of one value for every hour over a one year period. For more information consult:")
            col3.markdown("[PVGIS documentation](https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/pvgis-user-manual_en)")
            #col3.markdown(':grey[_<div style="text-align: justify;">"With the HySPI calculator, it is now possible to determine if hydrogen produced from PV energy can be considered green. The tool evaluates the PV farm capacity and estimates the environmental impacts based on surplus production credits allocation. Users can also simulate systems with or without dedicated batteries."</div>_]', unsafe_allow_html=True)

        #st.markdown("---")

        if data is not None:

            col1, col2, col3 = st.columns([1, 1, 1])

            pv_cap_MW = col1.number_input("Select the PV farm capacity (MW):", value=5.0*electro_capacity_MW, min_value=0.1,
                                          max_value=1_000_000.0, step=0.1)
            pv_cap_kW=pv_cap_MW*1_000 #website requires pv capacity to be in kWp

            df = get_pv_prod_data(data[0], data[1], pv_cap_kW)


            # Sum of all elec_W figures
            TOTAL_elec_produced_Wh = df['elec_Wh'].sum()
            capped_values = df['elec_Wh'].clip(upper=electro_capacity_W*INTERVAL_H) #all values under electro_capacity_Wh
            hour_consumption_Wh = capped_values.sum()
            credit = TOTAL_elec_produced_Wh - hour_consumption_Wh #100% credit, all goes from PV to grid #change for surplus

            hours_year = 365 * 24
            necessary_elec_Wh = electro_capacity_W * cf * hours_year  # here we add the capacity factor because this is related to electrolyzer's consumption
            grid = necessary_elec_Wh - hour_consumption_Wh #consumed from the grid
            pv_credit_Wh = necessary_elec_Wh - TOTAL_elec_produced_Wh  #keeping this here as it helps to understand the situation in which all PV production is allocated to the impacts rather than the grig

            percentage_grid_hour = grid / necessary_elec_Wh
            percentage_pv_hour = 1 - percentage_grid_hour

            percentage_grid_hour = min(max(percentage_grid_hour, 0), 1)
            percentage_pv_hour= min(max(percentage_pv_hour, 0), 1)

            #should we add 1-cf duration so we stop hydrogen operation when the production is little?

            # monthly cap begins here:
            # Extract month and year part and create a new column
            df['YearMonth'] = df['DateTime'].dt.to_period('M')

            # Group by the month and sum the 'elec_Wh' values
            monthly_sums = df.groupby('YearMonth')['elec_Wh'].sum().reset_index()

            # Calculate the monthly maximum values based on the number of days in each month
            monthly_sums['days_in_month'] = monthly_sums['YearMonth'].dt.days_in_month
            monthly_sums['max_value'] = monthly_sums['days_in_month'] * 24 * electro_capacity_W

            # Cap the monthly sums
            monthly_sums['Total_elec_Wh_month_capped'] = monthly_sums['elec_Wh'].clip(upper=monthly_sums['max_value'])

            # Calculate the difference
            monthly_sums['Difference'] = monthly_sums['elec_Wh'] - monthly_sums['Total_elec_Wh_month_capped']

            total_sum_hour_month_Wh = monthly_sums['Total_elec_Wh_month_capped'].sum()
            credit_minus_monthly_extra_Wh = monthly_sums['Difference'].sum()
            pv_credit_monthly_Wh = necessary_elec_Wh - total_sum_hour_month_Wh

            # daily cap begins here:
            # Extract date part and create a new column
            df['Date'] = df['DateTime'].dt.date

            # Group by the date and sum the 'elec_Wh' values
            daily_sums = df.groupby('Date')['elec_Wh'].sum().reset_index()
            daily_sums_24 = df.groupby('Date')['elec_Wh'].sum().reset_index() #here they are the same thing

            # Rename columns for clarity
            daily_sums.columns = ['Date', 'Total_elec_Wh_day']
            daily_sums_24.columns = ['Date', 'Total_elec_Wh_day_24'] #creating a new name for daily cap

            # Daily cap
            max_value = 24 * electro_capacity_W

            daily_sums_24['Total_elec_Wh_day_24'] = daily_sums_24['Total_elec_Wh_day_24'].clip(upper=max_value) #capping value
            merged_df = pd.merge(daily_sums, daily_sums_24, on='Date')

            # Calculate the difference
            merged_df['Difference'] = merged_df['Total_elec_Wh_day'] - merged_df['Total_elec_Wh_day_24']

            # Created the new DataFrame with 'Date' and 'Difference'
            diff = merged_df[['Date', 'Difference']]

            diff.columns = ['Date', 'Total_elec_Wh_day_Difference']

            total_sum_hour_day_Wh = daily_sums_24['Total_elec_Wh_day_24'].sum()
            credit_minus_daily_extra_Wh = diff['Total_elec_Wh_day_Difference'].sum()
            pv_credit_Wh = necessary_elec_Wh - TOTAL_elec_produced_Wh
            pv_credit_daily_Wh = necessary_elec_Wh - total_sum_hour_day_Wh


            battery_coupling = col2.selectbox("Battery coupled?", ["Yes", "No"], index=1)

            if battery_coupling == "No":
                gifb_path = 'H2b.gif'
                col3.image(gifb_path, use_column_width=True)

                col4, col2, col3 = st.columns([3, 1, 2])

                col4.write("##### Electricity per year:")
                col2.write("##### [KWh]")
                col3.write("##### Allocation options:")

                col4.write(f"Electrolyzer's total consumption: ")
                col2.write(f"{Ec_MWh / BoP_LT_y:.2f}MWh")
                col4.write("PV production:")
                col2.markdown(f" {TOTAL_elec_produced_Wh / 1000000:.2f} MWh", unsafe_allow_html=True)
                col4.write("Electrolyzer's consumption from PV")
                col2.markdown(f" {hour_consumption_Wh / 1000000:.2f} MWh", unsafe_allow_html=True)

                if credit > 0:
                    col4.write("PV surplus production:")
                    col2.markdown(f" {credit / 1000000:.2f} MWh", unsafe_allow_html=True)
                    if credit - credit_minus_daily_extra_Wh > 0:
                        col4.write("PV surplus production (daily cap):")
                        col2.markdown(f"{(credit - credit_minus_daily_extra_Wh) / 1000000:.2f}MWh",
                                           unsafe_allow_html=True)
                    if credit - credit_minus_monthly_extra_Wh != 0:
                        col4.write("PV surplus production (monthly cap):")
                        col2.markdown(f"{(credit - credit_minus_monthly_extra_Wh) / 1000000:.2f}MWh",
                                      unsafe_allow_html=True)


                with col3:
                    col1, col2 = st.columns([3, 1])

                    # Display text and calculated percentages
                    with col1:
                        if TOTAL_elec_produced_Wh != hour_consumption_Wh:
                            st.write(":blue-background[Grid - yearly PV credit:]")
                            st.write(":blue-background[PV + yearly PV credit:]")
                        if credit - credit_minus_monthly_extra_Wh != 0:
                            st.write(":gray-background[Grid - monthly PV credit:]")
                            st.write(":gray-background[PV + monthly PV credit:]")
                        if credit - credit_minus_daily_extra_Wh != 0:
                            st.write(":blue-background[Grid - daily PV credit:]")
                            st.write(":blue-background[PV + daily PV credit:]")
                        st.write(":gray-background[Grid (hourly consumption):]")
                        st.write(":gray-background[PV (hourly consumption):]")

                    with col2:
                        percentage_grid_year = pv_credit_Wh / necessary_elec_Wh
                        percentage_pv_year = 1 - percentage_grid_year

                        plot_percentage_grid_year = min(max(percentage_grid_year, 0), 1)
                        plot_percentage_pv_year = min(max(percentage_pv_year, 0), 1)

                        if TOTAL_elec_produced_Wh != hour_consumption_Wh:
                            st.write(f'{percentage_grid_year:.2%}', unsafe_allow_html=True)
                            st.write(f'{percentage_pv_year:.2%}', unsafe_allow_html=True)

                        percentage_grid_month = pv_credit_monthly_Wh / necessary_elec_Wh
                        percentage_pv_month = 1 - percentage_grid_month

                        plot_percentage_grid_month = min(max(percentage_grid_month, 0), 1)
                        plot_percentage_pv_month = min(max(percentage_pv_month, 0), 1)

                        if credit - credit_minus_monthly_extra_Wh != 0:
                            st.write(f'{percentage_grid_month:.2%}', unsafe_allow_html=True)
                            st.write(f'{percentage_pv_month:.2%}', unsafe_allow_html=True)

                        percentage_grid_day = pv_credit_daily_Wh / necessary_elec_Wh
                        percentage_pv_day = 1 - percentage_grid_day

                        percentage_grid_day = min(max(percentage_grid_day, 0), 1)
                        percentage_pv_day = min(max(percentage_pv_day, 0), 1)

                        if credit - credit_minus_daily_extra_Wh != 0:
                            st.write(f'{percentage_grid_day:.2%}', unsafe_allow_html=True)
                            st.write(f'{percentage_pv_day:.2%}', unsafe_allow_html=True)

                        st.write(f'{percentage_grid_hour:.2%}', unsafe_allow_html=True)
                        st.write(f'{percentage_pv_hour:.2%}', unsafe_allow_html=True)

                allocation = col3.selectbox("Electricity Allocation cap",
                                          ["Annual", "Monthly", "Daily", "Hourly"], index=2)
                if allocation == "Annual":
                    percentage_grid = percentage_grid_year
                    percentage_pv = percentage_pv_year
                if allocation == "Monthly":
                    percentage_grid = percentage_grid_month
                    percentage_pv = percentage_pv_month
                if allocation == "Daily":
                    percentage_grid = percentage_grid_day
                    percentage_pv = percentage_pv_day
                if allocation == "hourly":
                    percentage_grid = percentage_grid_hour
                    percentage_pv = percentage_pv_hour

                # Prepare data for plotting
                data = {
                    'Category': ['Year', 'Month', 'Day', 'Hour'],
                    'Grid': [plot_percentage_grid_year, plot_percentage_grid_month, percentage_grid_day,
                             percentage_grid_hour],
                    'PV': [plot_percentage_pv_year, plot_percentage_pv_month, percentage_pv_day, percentage_pv_hour]
                }

                df = pd.DataFrame(data)

                # Plot the data using matplotlib
                fig, ax = plt.subplots(figsize=(5,3))

                # Plot stacked bar graph
                bar_width = 0.35
                bar1 = ax.bar(df['Category'], df['Grid'], bar_width, label='Grid', color='#7E868E')
                bar2 = ax.bar(df['Category'], df['PV'], bar_width, bottom=df['Grid'], label='PV', color='#FFBE18')

                # Add labels and title
                ax.set_xlabel('Category')
                ax.set_ylabel('Percentage')
                ax.set_title('Grid and PV Percentages')
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                plt.tight_layout()

                # Display the plot in Streamlit
                col4.pyplot(fig)

            if battery_coupling == "Yes":
                gif_path = 'H2.gif'
                col3.image(gif_path, use_column_width=True)

                # Battery system
                battery_power_capacity_MW = col1.number_input("Battery power capacity (MW):", value=5.0, min_value=0.0,
                                                              step=0.1)
                battery_power_capacity_W = battery_power_capacity_MW * 1_000_000  # Convert to watts

                # Define storage capacity in Wh (20 MWh)
                battery_storage_capacity_MWh = col2.number_input("Battery storage capacity (MWh):", value=20.0,
                                                                 min_value=0.0, step=0.1)
                battery_storage_capacity_Wh = battery_storage_capacity_MWh * 1_000_000  # Convert to watt-hours

                eff_charge = 0.995
                eff_discharge = 0.995

                # Initialize battery state variables
                battery_stored_Wh = 0
                total_elec_sent_to_battery_Wh = 0
                total_elec_consumed_from_battery_Wh = 0
                send_to_grid = 0

                # Initialize DataFrame for adjusted daily sums
                df['Date'] = df['DateTime'].dt.date
                daily_sums = df.groupby('Date')['elec_Wh'].sum().reset_index()
                daily_sums['Adjusted_elec_Wh_day'] = daily_sums['elec_Wh']  # Initialize with the same value

                # Process each row to manage battery charging/discharging
                for index, row in df.iterrows():
                    date = row['Date']
                    surplus_Wh = row['elec_Wh'] - electro_capacity_W * INTERVAL_H
                    if surplus_Wh > 0:
                        # Charge the battery with surplus electricity
                        available_to_charge_Wh = min(surplus_Wh, battery_power_capacity_W * INTERVAL_H,
                                                     battery_storage_capacity_Wh - battery_stored_Wh)
                        charged_Wh = available_to_charge_Wh * eff_charge
                        battery_stored_Wh += charged_Wh
                        total_elec_sent_to_battery_Wh += available_to_charge_Wh
                        daily_sums.loc[daily_sums['Date'] == date, 'Adjusted_elec_Wh_day'] += charged_Wh
                        send_to_grid = surplus_Wh - available_to_charge_Wh
                    else:
                        # Discharge the battery if there is no PV production
                        required_from_battery_Wh = min(-surplus_Wh, battery_power_capacity_W * INTERVAL_H,
                                                       battery_stored_Wh)
                        discharged_Wh = required_from_battery_Wh * eff_discharge
                        battery_stored_Wh -= required_from_battery_Wh
                        total_elec_consumed_from_battery_Wh += discharged_Wh

                # Calculate efficiency losses
                efficiency_losses_Wh = total_elec_sent_to_battery_Wh - total_elec_consumed_from_battery_Wh

                col4, col2, col3 = st.columns([3, 1, 2])

                col4.write("##### Electricity per year:")
                col2.write("##### [MWh]")
                col3.write("##### Allocation options:")

                col4.write(f"Electrolyzer's total consumption: ")
                col2.write(f"{Ec_MWh / BoP_LT_y:.2f}")
                col4.write("PV production:")
                col2.markdown(f" {TOTAL_elec_produced_Wh / 1000000:.2f}", unsafe_allow_html=True)
                col4.write("Electrolyzer's consumption from PV:")
                col2.markdown(f" {hour_consumption_Wh / 1000000:.2f}", unsafe_allow_html=True)
                col4.write("Electrolyzer's consumption from PV + battery:")
                col2.markdown(f" {(hour_consumption_Wh + total_elec_consumed_from_battery_Wh) / 1000000:.2f}",
                              unsafe_allow_html=True)
                #col4.write(f"Electricity sent to the battery:")
                #col2.write(f"{total_elec_sent_to_battery_Wh / 1000000:.2f}")
                col4.write(f"Electricity consumed from the battery:")
                col2.write(f"{total_elec_consumed_from_battery_Wh / eff_charge / 1_000_000: .2f}")
                #col4.write(f"Efficiency losses:")
                #col2.write(f"{efficiency_losses_Wh / 1_000_000: .2f}")


                # Updating percentages:
                grid = necessary_elec_Wh - (
                        hour_consumption_Wh + total_elec_consumed_from_battery_Wh)  # now the electricity used from PV gets an increment from battery

                percentage_grid_hour = grid / necessary_elec_Wh
                percentage_pv_hour = 1 - percentage_grid_hour

                percentage_grid_hour = min(max(percentage_grid_hour, 0), 1)
                percentage_pv_hour = min(max(percentage_pv_hour, 0), 1)

                # Adjust daily sums to include battery storage and apply daily cap
                daily_sums_24 = daily_sums.copy()
                daily_sums_24['Adjusted_elec_Wh_day'] = daily_sums_24['Adjusted_elec_Wh_day'].clip(upper=max_value)

                # Calculate the difference
                daily_sums['Difference'] = daily_sums['Adjusted_elec_Wh_day'] - daily_sums_24['Adjusted_elec_Wh_day']

                # Create the new DataFrame with 'Date' and 'Difference'
                diff = daily_sums[['Date', 'Difference']]

                # New column names
                diff.columns = ['Date', 'Total_elec_Wh_day_Difference']

                total_sum_hour_day_Wh = daily_sums_24['Adjusted_elec_Wh_day'].sum()
                credit_minus_daily_extra_Wh = diff['Total_elec_Wh_day_Difference'].sum()
                pv_credit_Wh = necessary_elec_Wh - TOTAL_elec_produced_Wh
                pv_credit_daily_Wh = necessary_elec_Wh - total_sum_hour_day_Wh

                # Monthly cap begins here:
                df['YearMonth'] = df['DateTime'].dt.to_period('M')

                # Group by the month and sum the 'elec_Wh' values
                monthly_sums = df.groupby('YearMonth')['elec_Wh'].sum().reset_index()

                # Calculate the monthly maximum values based on the number of days in each month
                monthly_sums['days_in_month'] = monthly_sums['YearMonth'].dt.days_in_month
                monthly_sums['max_value'] = monthly_sums['days_in_month'] * 24 * electro_capacity_W

                # Cap the monthly sums
                monthly_sums['Total_elec_Wh_month_capped'] = monthly_sums['elec_Wh'].clip(
                    upper=monthly_sums['max_value'])

                # Calculate the difference
                monthly_sums['Difference'] = monthly_sums['elec_Wh'] - monthly_sums['Total_elec_Wh_month_capped']

                total_sum_hour_month_Wh = monthly_sums['Total_elec_Wh_month_capped'].sum()
                credit_minus_monthly_extra_Wh = monthly_sums['Difference'].sum()
                pv_credit_monthly_Wh = necessary_elec_Wh - total_sum_hour_month_Wh

                with col3:
                    col1, col2 = st.columns([3, 1])

                    # Display text and calculated percentages
                    with col1:
                        if TOTAL_elec_produced_Wh != hour_consumption_Wh:
                            st.write(":blue-background[Grid - yearly PV credit:]")
                            st.write(":blue-background[PV + yearly PV credit:]")
                        if credit - credit_minus_monthly_extra_Wh != 0:
                            st.write(":gray-background[Grid - monthly PV credit:]")
                            st.write(":gray-background[PV + monthly PV credit:]")
                        if credit - credit_minus_daily_extra_Wh != 0:
                            st.write(":blue-background[Grid - daily PV credit:]")
                            st.write(":blue-background[PV + daily PV credit:]")
                        st.write(":gray-background[Grid (hourly consumption):]")
                        st.write(":gray-background[PV (hourly consumption):]")

                    with col2:
                        percentage_grid_year = pv_credit_Wh / necessary_elec_Wh
                        percentage_pv_year = 1 - percentage_grid_year

                        plot_percentage_grid_year = min(max(percentage_grid_year, 0), 1)
                        plot_percentage_pv_year = min(max(percentage_pv_year, 0), 1)


                        if TOTAL_elec_produced_Wh != hour_consumption_Wh:
                            st.write(f'{percentage_grid_year:.2%}', unsafe_allow_html=True)
                            st.write(f'{percentage_pv_year:.2%}', unsafe_allow_html=True)

                            percentage_grid_month = pv_credit_monthly_Wh / necessary_elec_Wh
                            percentage_pv_month = 1 - percentage_grid_month

                            plot_percentage_grid_month = min(max(percentage_grid_month, 0), 1)
                            plot_percentage_pv_month = min(max(percentage_pv_month, 0), 1)

                            if credit - credit_minus_monthly_extra_Wh != 0:
                                st.write(f'{percentage_grid_month:.2%}', unsafe_allow_html=True)
                                st.write(f'{percentage_pv_month:.2%}', unsafe_allow_html=True)

                            percentage_grid_day = pv_credit_daily_Wh / necessary_elec_Wh
                            percentage_pv_day = 1 - percentage_grid_day

                            percentage_grid_day = min(max(percentage_grid_day, 0), 1)
                            percentage_pv_day = min(max(percentage_pv_day, 0), 1)

                            if credit - credit_minus_daily_extra_Wh != 0:
                                st.write(f'{percentage_grid_day:.2%}', unsafe_allow_html=True)
                                st.write(f'{percentage_pv_day:.2%}', unsafe_allow_html=True)

                        st.write(f'{percentage_grid_hour:.2%}', unsafe_allow_html=True)
                        st.write(f'{percentage_pv_hour:.2%}', unsafe_allow_html=True)

                #allocation options
                allocation = col3.selectbox("Electricity allocation cap",
                                            ["Annual", "Monthly", "Daily", "Hourly"],
                                            index=2)
                if allocation == "Annual":
                    percentage_grid = percentage_grid_year
                    percentage_pv = percentage_pv_year
                if allocation == "Monthly":
                    percentage_grid = percentage_grid_month
                    percentage_pv = percentage_pv_month
                if allocation == "Daily":
                    percentage_grid = percentage_grid_day
                    percentage_pv = percentage_pv_day
                if allocation == "Hourly":
                    percentage_grid = percentage_grid_hour
                    percentage_pv = percentage_pv_hour

                # Allocation plot
                data = {
                    'Category': ['Year', 'Month', 'Day', 'Hour'],
                    'Grid': [plot_percentage_grid_year, plot_percentage_grid_month, percentage_grid_day,
                             percentage_grid_hour],
                    'PV': [plot_percentage_pv_year, plot_percentage_pv_month, percentage_pv_day, percentage_pv_hour]
                }

                df = pd.DataFrame(data)

                fig, ax = plt.subplots(figsize=(5, 3))

                # Plot stacked bar graph
                bar_width = 0.35
                bar1 = ax.bar(df['Category'], df['Grid'], bar_width, label='Grid', color='#7E868E')
                bar2 = ax.bar(df['Category'], df['PV'], bar_width, bottom=df['Grid'], label='PV',
                              color='#FFBE18')

                # Add labels and title
                ax.set_xlabel('Category')
                ax.set_ylabel('Percentage')
                ax.set_title('Grid and PV Percentages')
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                plt.tight_layout()

                # Display the plot in Streamlit
                col4.pyplot(fig)

    #Indication for background before the data
    colored_header(
        label="Background",
        description="Electricity scenarios 2050",
        color_name="blue-70",
    )

    col4, col5, col6, col7 = st.columns([1, 1, 1, 1])

    demand_scenario = col4.radio("**Demand Scenarios**",options=["Reference", "Sobriety", "Reindustrialization"],key="demand_scenario")
    production_scenario = col5.radio("**Production Scenarios**",options=["M0", "M1", "M23", "N1", "N2", "N03"],key="production_scenario", horizontal=True)
    imports_market_group = col6.radio("**Imports market group**",options=["Western European Union (WEU)", "Neighbouring"], key="imports_market_group")
    iam_applied = col7.radio("**IAM applied**",options=["SSP2-Base", "SSP2-26", "SSP2-19", "None"], key="iam_applied")

    choice=None
    if demand_scenario == "Reference":
        if production_scenario == "M0":
            if imports_market_group == "Western European Union (WEU)":
                if iam_applied == "SSP2-Base":
                    choice = "EFR2050BRM0"
                elif iam_applied == "SSP2-26":
                    choice = "EFR2050R26RM0"
                elif iam_applied == "SSP2-19":
                    choice = "EFR2050R19RM0"
                elif iam_applied == "None":
                    st.write("Demand modelling in progress, not currently available")
            else:
                if iam_applied == "None":
                    choice = "EFR2050RM0E"
                elif iam_applied == "SSP2-Base":
                    choice = "EFR2050BRM0N"
                else:
                    st.write("Demand modelling in progress, not currently available")
        elif production_scenario == "M1":
            if imports_market_group == "Western European Union (WEU)":
                if iam_applied == "SSP2-Base":
                    choice = "EFR2050BRM1"
                elif iam_applied == "SSP2-26":
                    choice = "EFR2050R26RM1"
                elif iam_applied == "SSP2-19":
                    choice = "EFR2050R19RM1"
                elif iam_applied == "None":
                    st.write("Demand modelling in progress, not currently available")
            else:
                if iam_applied == "None":
                    choice = "EFR2050RM1E"
                elif iam_applied == "SSP2-Base":
                    choice = "EFR2050BRM1N"
                else:
                    st.write("Demand modelling in progress, not currently available")
        elif production_scenario == "M23":
            if imports_market_group == "Western European Union (WEU)":
                if iam_applied == "SSP2-Base":
                    choice = "EFR2050BRM23"
                elif iam_applied == "SSP2-26":
                    choice = "EFR2050R26RM23"
                elif iam_applied == "SSP2-19":
                    choice = "EFR2050R19RM23"
                elif iam_applied == "None":
                    st.write("Demand modelling in progress, not currently available")
            else:
                if iam_applied == "None":
                    choice = "EFR2050RM23E"
                elif iam_applied == "SSP2-Base":
                    choice = "EFR2050BRM23N"
                elif iam_applied == "SSP2-Base":
                    choice = "EFR2050BRM1N"
                else:
                    st.write("Demand modelling in progress, not currently available")
        elif production_scenario == "N1":
            if imports_market_group == "Western European Union (WEU)":
                if iam_applied == "SSP2-Base":
                    choice = "EFR2050BRN1"
                elif iam_applied == "SSP2-26":
                    choice = "EFR2050R26RN1"
                elif iam_applied == "SSP2-19":
                    choice = "EFR2050R19RN1"
                elif iam_applied == "None":
                    st.write("Demand modelling in progress, not currently available")
            else:
                if iam_applied == "None":
                    choice = "EFR2050RN1E"
                elif iam_applied == "SSP2-Base":
                    choice = "EFR2050BRN1N"
                else:
                    st.write("Demand modelling in progress, not currently available")
        elif production_scenario == "N2":
            if imports_market_group == "Western European Union (WEU)":
                if iam_applied == "SSP2-Base":
                    choice = "EFR2050BRN2"
                elif iam_applied == "SSP2-26":
                    choice = "EFR2050R26RN2"
                elif iam_applied == "SSP2-19":
                    choice = "EFR2050R19RN2"
                elif iam_applied == "None":
                    st.write("Demand modelling in progress, not currently available")
            else:
                if iam_applied == "None":
                    choice = "EFR2050RN2E"
                elif iam_applied == "SSP2-Base":
                    choice = "EFR2050BRN2N"
                else:
                    st.write("Demand modelling in progress, not currently available")
        elif production_scenario == "N03":
            if imports_market_group == "Western European Union (WEU)":
                if iam_applied == "SSP2-Base":
                    choice = "EFR2050BRN03"
                elif iam_applied == "SSP2-26":
                    choice = "EFR2050R26RN03"
                elif iam_applied == "SSP2-19":
                    choice = "EFR2050R19RN03"
                elif iam_applied == "None":
                    st.write("Demand modelling in progress, not currently available")
            else:
                if iam_applied == "None":
                    choice = "EFR2050RN03E"
                elif iam_applied == "SSP2-Base":
                    choice = "EFR2050BRN03N"
                else:
                    st.write("Demand modelling in progress, not currently available")
    else:
        st.write("Demand modelling in progress, not currently available")



    if data is not None and st.button("Compute result"):
        choice2=choice

    elif data is None and st.button("Compute result"):
        choice2=choice
        percentage_pv=0
        percentage_grid=1

    else:
        st.stop()

    #project start:
    agb.initProject('HySPI_scenarios')

    USER_DB = 'user-db'
    EI = 'ei_3.9.1'
    agb.resetDb(USER_DB)
    agb.resetParams()
    B50RM0 = 'ecoinvent_cutoff_3.9_image_SSP2-Base_2050_RM0_2.1'
    B50RM1 = 'ecoinvent_cutoff_3.9_image_SSP2-Base_2050_RM1_2.1'
    B50RM23 = 'ecoinvent_cutoff_3.9_image_SSP2-Base_2050_RM23_2.1'
    B50RN1 = 'ecoinvent_cutoff_3.9_image_SSP2-Base_2050_RN1_2.1'
    B50RN2 = 'ecoinvent_cutoff_3.9_image_SSP2-Base_2050_RN2_2.1'
    B50RN03 = 'ecoinvent_cutoff_3.9_image_SSP2-Base_2050_RN03_2.1'
    R1950RM0 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP19_2050_RM0_2.1'
    R1950RM1 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP19_2050_RM1_2.1'
    R1950RM23 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP19_2050_RM23_2.1'
    R1950RN1 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP19_2050_RN1_2.1'
    R1950RN2 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP19_2050_RN2_2.1'
    R1950RN03 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP19_2050_RN03_2.1'
    R2650RM0 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP26_2050_RM0_2.1'
    R2650RM1 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP26_2050_RM1_2.1'
    R2650RM23 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP26_2050_RM23_2.1'
    R2650RN1 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP26_2050_RN1_2.1'
    R2650RN2 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP26_2050_RN2_2.1'
    R2650RN03 = 'ecoinvent_cutoff_3.9_image_SSP2-RCP26_2050_RN03_2.1'

    Elec_FR_2023 = agb.findActivity("market for electricity, low voltage", loc="FR", single=False, db_name=EI)
    Elec_DE_2023 = agb.findActivity("market for electricity, low voltage", loc="DE", single=False, db_name=EI)
    Elec_FR_2050_BRM0 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=B50RM0)
    Elec_FR_2050_BRM1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=B50RM1)
    Elec_FR_2050_BRM23 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=B50RM23)
    Elec_FR_2050_BRN1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=B50RN1)
    Elec_FR_2050_BRN2 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=B50RN2)
    Elec_FR_2050_BRN03 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=B50RN03)
    Elec_FR_2050_R19RM0 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R1950RM0)
    Elec_FR_2050_R19RM1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R1950RM1)
    Elec_FR_2050_R19RM23 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R1950RM23)
    Elec_FR_2050_R19RN1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R1950RN1)
    Elec_FR_2050_R19RN2 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R1950RN2)
    Elec_FR_2050_R19RN03 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,db_name=R1950RN03)
    Elec_FR_2050_R26RM0 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R2650RM0)
    Elec_FR_2050_R26RM1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R2650RM1)
    Elec_FR_2050_R26RM23 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R2650RM23)
    Elec_FR_2050_R26RN1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R2650RN1)
    Elec_FR_2050_R26RN2 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R2650RN2)
    Elec_FR_2050_R26RN03 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R2650RN03)
    Elec_FR_2050_RM0E = agb.findActivity(name="market for electricity, low voltage M0", db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RM1E = agb.findActivity(name="market for electricity, low voltage M1", db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RM23E = agb.findActivity(name="market for electricity, low voltage M23", db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RN1E = agb.findActivity(name="market for electricity, low voltage N1", db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RN2E = agb.findActivity(name="market for electricity, low voltage N2",db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RN03E = agb.findActivity(name="market for electricity, low voltage N03",db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_BRM0N = agb.findActivity("market for electricity, low voltage, FE2050 N", loc="FR", single=False, db_name=B50RM0)
    Elec_FR_2050_BRM1N = agb.findActivity("market for electricity, low voltage, FE2050 N", loc="FR", single=False, db_name=B50RM1)
    Elec_FR_2050_BRM23N = agb.findActivity("market for electricity, low voltage, FE2050 N", loc="FR", single=False, db_name=B50RM23)
    Elec_FR_2050_BRN1N = agb.findActivity("market for electricity, low voltage, FE2050 N", loc="FR", single=False, db_name=B50RN1)
    Elec_FR_2050_BRN2N = agb.findActivity("market for electricity, low voltage, FE2050 N", loc="FR", single=False, db_name=B50RN2)
    Elec_FR_2050_BRN03N = agb.findActivity("market for electricity, low voltage, FE2050 N", loc="FR", single=False,db_name=B50RN03)

    #PV_coupled = agb.findActivity("electricity production, photovoltaic, 570kWp open ground installation, multi-Si",loc="FR", single=False, db_name=EI)
    PV_coupled = agb.findActivity("electricity production, photovoltaic",loc="FR", db_name=B50RM0)

    base = ["EFR2050BRM0", "EFR2050BRM1", "EFR2050BRM23", "EFR2050BRN1", "EFR2050BRN2", "EFR2050BRN03"]
    N_base = ["EFR2050BRM0N", "EFR2050BRM1N", "EFR2050BRM23N", "EFR2050BRN1N", "EFR2050BRN2N", "EFR2050BRN03N"]
    R19 = ["EFR2050R19RM0", "EFR2050R19RM1", "EFR2050R19RM23", "EFR2050R19RN1", "EFR2050R19RN2", "EFR2050R19RN03"]
    R26 = ["EFR2050R26RM0", "EFR2050R26RM1", "EFR2050R26RM23", "EFR2050R26RN1", "EFR2050R26RN2", "EFR2050R26RN03"]
    E_RTE = ["EFR2050RM0E", "EFR2050RM1E", "EFR2050RM23E", "EFR2050RN1E", "EFR2050RN2E", "EFR2050RN03E"]
    options = ["EFR2023", "EDE2023", "PV"]+base+R19+R26+E_RTE

    #Results indication before code
    st.markdown("---")
    st.markdown("## Results")
    st.markdown("#### Hydrogen Environmental Impact")
    st.markdown("###### Functional unit: 1kg of Hydrogen produced")#verify the option to switch fu
    st.markdown("###### Method: EF v3.0 no LT")

    water_H2 = agb.findBioAct("Water, unspecified natural origin", categories=('natural resource', 'in ground'))

    Oxygen = agb.findBioAct("Oxygen", categories=('air',))

    Occupation_ind = agb.findBioAct("Occupation, industrial area", categories=('natural resource', 'land'))

    Transformation_from_ind = agb.findBioAct("Transformation, from industrial area",
                                             categories=('natural resource', 'land'))

    Transformation_to_ind = agb.findBioAct("Transformation, to industrial area", categories=('natural resource', 'land'))

    Lorry_E6= agb.findActivity("market for transport, freight, lorry >32 metric ton, EURO6", single=False, db_name=EI)

    tank = agb.findActivity(
        "high pressure storage tank production and maintenance, per 10kgH2 at 500bar, from grid electricity", single=False,
        db_name='AEC/PEM')

    NONE = newActivity(USER_DB,  # We define foreground activities in our own DB
                       "no activity, or zero impact activity",  # Name of the activity
                       "unit",  # Unit
                       exchanges={})

    #Method
    EF = 'EF v3.0 no LT'

    climate = (EF, 'climate change no LT', 'global warming potential (GWP100) no LT')
    m_resources = (EF, 'material resources: metals/minerals no LT', 'abiotic depletion potential (ADP): elements (ultimate reserves) no LT')
    land = (EF, 'land use no LT', 'soil quality index no LT')
    water = (EF, 'water use no LT', 'user deprivation potential (deprivation-weighted water consumption) no LT')
    acidification = (EF, 'acidification no LT', 'accumulated exceedance (AE) no LT')
    marine_eutroph = (EF, 'eutrophication: marine no LT', 'fraction of nutrients reaching marine end compartment (N) no LT')
    freshwater_eutroph = (EF, 'eutrophication: freshwater no LT', 'fraction of nutrients reaching freshwater end compartment (P) no LT')
    terre_eutroph = (EF, 'eutrophication: terrestrial no LT', 'accumulated exceedance (AE) no LT')
    radiation = (EF, 'ionising radiation: human health no LT', 'human exposure efficiency relative to u235 no LT')
    non_renew = (EF, 'energy resources: non-renewable no LT', 'abiotic depletion potential (ADP): fossil fuels no LT')

    # List of the impacts
    impacts = [climate, m_resources, land, water, acidification, marine_eutroph, freshwater_eutroph, terre_eutroph,
               radiation, non_renew]

    #Electrolyzer selection:
    activity_names = {
        'PEM': {
            'Stack': 'electrolyzer production, 1MWe, PEM, Stack',
            'BoP': 'electrolyzer production, 1MWe, PEM, Balance of Plant',
            'Treatment_Stack': 'treatment of fuel cell stack, 1MWe, PEM',
            'Treatment_BoP': 'treatment of fuel cell balance of plant, 1MWe, PEM'
        },
        'AEC': {
            'Stack': 'electrolyzer production, 1MWe, AEC, Stack',
            'BoP': 'electrolyzer production, 1MWe, AEC, Balance of Plant',
            'Treatment_Stack': 'treatment of fuel cell stack, 1MWe, AEC',
            'Treatment_BoP': 'treatment of fuel cell balance of plant, 1MWe, AEC'
        }
    }

    #negative act to convert negative itens in LCI table
    def negAct(act):
        """Correct the sign of some activities that are accounted as negative in brightway. """
        return agb.newActivity(USER_DB, act["name"] + "_neg", act["unit"], {
            act: -1,
        })

    #activities from AEC/PEM database
    stack_activity = agb.findActivity(name=activity_names[stack_type]['Stack'], db_name='AEC/PEM')
    bop_activity = agb.findActivity(name=activity_names[stack_type]['BoP'], db_name='AEC/PEM')
    t_Stack_activity = negAct(agb.findActivity(name=activity_names[stack_type]['Treatment_Stack'], db_name='AEC/PEM'))
    t_BoP_activity = negAct(agb.findActivity(name=activity_names[stack_type]['Treatment_BoP'], db_name='AEC/PEM'))


    #Parametrization for impact mean computation
    #electricity markets parameters
    param_electricity = agb.newEnumParam(
        "param_electricity",  # Short name
        label="electricity mix",  # English label
        description="RTE scenarios for FR electricity",  # Long description
        values=["EFR2023", "EDE2023", "PV"]+base+N_base+R19+R26+E_RTE,  # ["NONE"]
        default="Elec_FR_2050_BRM0")

    electricity = newSwitchAct(USER_DB, "electricity", param_electricity, {
        "EFR2023": Elec_FR_2023,
        "EDE2023": Elec_DE_2023,
        "PV": PV_coupled,
        "EFR2050BRM0": Elec_FR_2050_BRM0,
        "EFR2050BRM1": Elec_FR_2050_BRM1,
        "EFR2050BRM23": Elec_FR_2050_BRM23,
        "EFR2050BRN1": Elec_FR_2050_BRN1,
        "EFR2050BRN2": Elec_FR_2050_BRN2,
        "EFR2050BRN03": Elec_FR_2050_BRN03,
        "EFR2050R19RM0": Elec_FR_2050_R19RM0,
        "EFR2050R19RM1": Elec_FR_2050_R19RM1,
        "EFR2050R19RM23": Elec_FR_2050_R19RM23,
        "EFR2050R19RN1": Elec_FR_2050_R19RN1,
        "EFR2050R19RN2": Elec_FR_2050_R19RN2,
        "EFR2050R19RN03": Elec_FR_2050_R19RN03,
        "EFR2050R26RM0": Elec_FR_2050_R26RM0,
        "EFR2050R26RM1": Elec_FR_2050_R26RM1,
        "EFR2050R26RM23": Elec_FR_2050_R26RM23,
        "EFR2050R26RN1": Elec_FR_2050_R26RN1,
        "EFR2050R26RN2": Elec_FR_2050_R26RN2,
        "EFR2050R26RN03": Elec_FR_2050_R26RN03,
        "EFR2050RM0E": Elec_FR_2050_RM0E,
        "EFR2050RM1E": Elec_FR_2050_RM1E,
        "EFR2050RM23E": Elec_FR_2050_RM23E,
        "EFR2050RN1E": Elec_FR_2050_RN1E,
        "EFR2050RN2E": Elec_FR_2050_RN2E,
        "EFR2050RN03E": Elec_FR_2050_RN03E,
        "EFR2050BRM0N": Elec_FR_2050_BRM0N,
        "EFR2050BRM1N": Elec_FR_2050_BRM1N,
        "EFR2050BRM23N": Elec_FR_2050_BRM23N,
        "EFR2050BRN1N": Elec_FR_2050_BRN1N,
        "EFR2050BRN2N": Elec_FR_2050_BRN2N,
        "EFR2050BRN03N": Elec_FR_2050_BRN03N,
    })

    stack_type_p = agb.newEnumParam(
        "stack_type_parameter",  # Short name
        label="stack type pem or aec",  # Label
        description="PEM or AEC",  # Long description
        values=[  # Statistic weight of each option that fits with the market
            "PEM",
            "AEC"
        ],
        default=stack_type
    )

    stack_LT_p = agb.newFloatParam(
        "Stack_LT",
        distrib=agb.DistributionType.TRIANGLE,
        default=stack_LT, min=30000, max=150000,
        label="Stack lifetime",
        description="evolution of the stack lifetime",
        unit=" ")

    BoP_LT_y_p = agb.newFloatParam(
        "BOP_LT_y",
        distrib=agb.DistributionType.TRIANGLE,
        default=BoP_LT_y, min=20, max=40,
        label="BoP lifetime y",
        description="evolution of the BoP lifetime in years",
        unit=" ")

    eff_p = agb.newFloatParam(
        "eff",
        distrib=agb.DistributionType.TRIANGLE,
        default=eff, min=0.56, max=0.90,  # thermodinamic limits, but not technologial limit
        label="Stack efficiency",
        description="evolution of the stack efficiency",
        unit=" ")

    cf_p = agb.newFloatParam(
        "cf",
        distrib=agb.DistributionType.TRIANGLE,
        default=float(cf), min=float(0.3), max=float(0.95),
        label="Capacity Factor",
        description="Capacity factor linked to operational hours",
        unit=" ")

    #parameters missing:
    #transp = col3.selectbox("Transport method", ["Pipeline", "Truck"], index=0)
    #renewable_coupling = col1.selectbox("Photovoltaic coupled?", ["Yes", "No"], index=1)
    #storage_choice = col2.selectbox("Storage", ["Tank", "No storage"], index=1)

    H2_produced = BoP_LT_h  * cf * electro_capacity_kW * eff / HHV_kWhkg
    H2p = int(H2_produced)
    H2p_ton = (H2p / 1000) # Convert kg to tons
    H2_per_hour = H2p / (BoP_LT_h * cf)
    Electricity_1kg = (Electricity_consumed_kWh / H2_produced) # = HHV/eff

    E1 = round(Electricity_consumed_kWh / H2_produced, 2)

    n_stacks = BoP_LT_h / stack_LT

    def define_production():
        return agb.newActivity(USER_DB, "H2 production phase",
                               unit="unit",
                               exchanges={
                                   electricity: Electricity_1kg*percentage_grid,
                                   PV_coupled:Electricity_1kg*percentage_pv,
                                   water_H2: 0.0014,
                                   Oxygen: -8
                               })

    production = define_production()


    # land factors retrieved from Romain's LCI: no information was given regarding the references for these figures: *ask him!
    land_factor = 0.09 if stack_type == 'PEM' else 0.12

    # Infrastructure eol
    def define_eol():
        return agb.newActivity(USER_DB, "infrastructure end of lifefor H2 production",
                               unit="unit",
                               exchanges={
                                   t_Stack_activity: 1 / H2_produced,
                                   t_BoP_activity: 1 / H2_produced
                               })

    eol = define_eol()


    # Infrastructure
    def define_infrastructure():
        return agb.newActivity(USER_DB, "infrastructure for H2 production",
                               unit="unit",
                               exchanges={
                                   stack_activity: n_stacks / H2_produced,
                                   bop_activity: 1 / H2_produced,
                                   Occupation_ind: land_factor / electro_capacity_kW / H2_produced / BoP_LT_y,
                                   Transformation_from_ind: land_factor / H2_produced,
                                   Transformation_to_ind: land_factor / H2_produced,
                                   eol: 1,
                               })

    infra = define_infrastructure()


    def storage(storage_choice):
        if storage_choice == "Tank":
            n_tanks = col2.number_input("How many tanks does your system require throughout its lifetime?", value=10, min_value=1, step=1)
            storage_key = tank
            dx = float(n_tanks / H2_produced)
        elif storage_choice == "No storage":
            storage_key = NONE
            dx = 1

        return agb.newActivity(USER_DB, "H2 storage",
                               unit="unit",
                               exchanges={
                                   storage_key:dx
                                          })

    storage = storage(storage_choice)

    # Prompt user for input
    first_level_options = {
        "Referência": {
            "SSP2-Base": ["M0", "M1", "M23", "N1", "N2", "N03"],
            "SSP2-R19": ["M0", "M1", "M23", "N1", "N2", "N03"],
            "SSP2-R26": ["M0", "M1", "M23", "N1", "N2", "N03"]
        },
        "Extensive Reindustrialization": {
            "SSP2-Base": ["M0", "M1", "M23", "N1", "N2", "N03"],
            "SSP2-R19": ["M0", "M1", "M23", "N1", "N2", "N03"],
            "SSP2-R26": ["M0", "M1", "M23", "N1", "N2", "N03"]
        },
        "Sobriety": {
            "SSP2-Base": ["M0", "M1", "M23", "N1", "N2", "N03"],
            "SSP2-R19": ["M0", "M1", "M23", "N1", "N2", "N03"],
            "SSP2-R26": ["M0", "M1", "M23", "N1", "N2", "N03"]
        }
    }
    if 'counter' not in st.session_state:
        st.session_state.counter = 1

    order=f"result {st.session_state.counter}"
    def define_system():
        return agb.newActivity(USER_DB, name=order,
                               unit="kg",
                               exchanges={
                                   production: 1,
                                   infra: 1,
                                   storage: 1
                               })


    system = define_system()

    result_table_H2 = agb.multiLCAAlgebric(
        system,
        impacts,
        param_electricity=choice2
    )


    header_mapping = {
        'climate change no LT - global warming potential (GWP100) no LT[kg CO2-Eq]': 'climate change [kg CO2-Eq]',
        'material resources: metals/minerals no LT - abiotic depletion potential (ADP): elements (ultimate reserves) no LT[kg Sb-Eq]': 'material resources [kg Sb-Eq]',
        'land use no LT - soil quality index no LT[dimensionless]': 'land use [dimensionless]',
        'water use no LT - user deprivation potential (deprivation-weighted water consumption) no LT[m3 world eq. deprived]': 'water use [m3 world eq. deprived]',
        'acidification no LT - accumulated exceedance (AE) no LT[mol H+-Eq]': 'acidification [mol H+-Eq]',
        'eutrophication: marine no LT - fraction of nutrients reaching marine end compartment (N) no LT[kg N-Eq]': 'eutrophication: marine [kg N-Eq]',
        'eutrophication: freshwater no LT - fraction of nutrients reaching freshwater end compartment (P) no LT[kg P-Eq]': 'eutrophication: freshwater [kg P-Eq]',
        'eutrophication: terrestrial no LT - accumulated exceedance (AE) no LT[mol N-Eq]': 'eutrophication: terrestrial [mol N-Eq]',
        'ionising radiation: human health no LT - human exposure efficiency relative to u235 no LT[kBq U235-Eq]': 'ionising radiation [kBq U235-Eq]',
        'energy resources: non-renewable no LT - abiotic depletion potential (ADP): fossil fuels no LT[MJ, net calorific value]': 'energy resources: non-renewable [MJ, net calorific value]'
    }

    # Rename the columns in the result table using the mapping
    result_table_H2.rename(columns=header_mapping, inplace=True)

    lca_result = result_table_H2.iloc[:, :]

    # Check if 'stored_results' exists in session state, if not, initialize it
    if 'stored_results' not in st.session_state:
        st.session_state.stored_results = pd.DataFrame()

    # Append the new results to the stored results
    st.session_state.stored_results = pd.concat([st.session_state.stored_results, lca_result], axis=0)

    st.session_state.counter += 1 #update result name order

    # Transpose the stored results for display
    transposed_table = st.session_state.stored_results.transpose()

    # Display the transposed DataFrame
    st.table(transposed_table)


    with st.container():
        paragraph = (
            f"The estimated electricity consumption throughout the plant's lifetime is {Ec_GWh:.2f} GWh.\n\n"
            f"The total hydrogen production throughout the plant's lifetime is projected to be {H2p_ton:.2f} tons.\n\n"
            f"The hydrogen production rate is approximately {H2_per_hour:.2f} kg per hour.\n\n"
            f"Approximately {E1:.2f} kWh of electricity is required to produce 1 kg of hydrogen.\n\n"
        )

        # Display the combined paragraph
        st.info(paragraph)

    st.markdown("---")


    st.table(agb.exploreImpacts(impacts[0],
                       system,
                                param_electricity=choice2
                       ))
    st.table(agb.exploreImpacts(impacts[0],
                                production,
                                param_electricity=choice2
                                ))


    #Industrial use

    a_infra = agb.findActivity("market for chemical factory, organics", loc='GLO', db_name=EI)
    ammonia_smr = agb.findActivity("ammonia production, steam reforming, liquid", loc='FR', db_name=EI)
    def define_ammonia():
        return agb.newActivity(USER_DB, name="Ammonia production",
                               unit="unit",
                               exchanges={
                                   system: 0.177,  # LIFE CYCLE ASSESSMENT OF AMMONIA PRODUCTION METHODS
                                   a_infra: 3.904700991365526e-10,
                                   electricity: 0.64 + 0.823 * 0.37,
                                   # electricity for HB process + electricity for N2 production from air separation
                               })

    ammonia = define_ammonia()

    result_table_ammonia = agb.multiLCAAlgebric(
        ammonia,
        impacts,
        param_electricity=choice2
    )

    def define_Ammonia_smr():
        return agb.newActivity(USER_DB, name="Ammonia_smr production",
                               unit="unit",
                               exchanges={ammonia_smr: 1})

    Ammonia_smr = define_Ammonia_smr()

    result_table_ammonia_smr = agb.multiLCAAlgebric(
        Ammonia_smr,
        impacts,
        param_electricity=choice2
    )

    first_element = result_table_ammonia.iloc[0, 0]
    first_element_smr = result_table_ammonia_smr.iloc[0, 0]

    # Store the first element in session state
    st.session_state.first_element_ammonia = first_element
    st.session_state.first_element_ammonia_smr = first_element_smr



if __name__ == "__main__":
    show()
