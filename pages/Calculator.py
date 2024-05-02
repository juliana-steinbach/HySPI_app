import bw2analyzer as bwa
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
import SALib
from tabulate import tabulate
from sympy import *
from scipy.stats import binned_statistic
import seaborn as sns
from IPython.display import HTML, display
import bw2io as bi
import brightway2 as bw
import lca_algebraic as agb
from lca_algebraic import *
from brightway2 import *
import math
import ipywidgets as widgets
from IPython.display import display
import bw2io
from pyDOE2 import fullfact
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tabulate import tabulate
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from io import BytesIO
from sympy import symbols
from matplotlib.patches import Patch
#from ecoinvent_interface import Settings, permanent_setting




def show():
    import folium
    from streamlit_folium import st_folium
    import streamlit as st
    st.set_page_config(layout="wide")

    st.title("HySPI Hydrogen Impact Calculator")
    # Add content for the other page:

    agb.initProject('HySPI_scenarios')

    col1, col2, col3 = st.columns([1, 1, 1])

    stack_type = col1.selectbox("Select the electrolyzer stack:", ["PEM", "AEC"])
    elec_cap_mw = col2.number_input("Select the electrolyzer capacity (MW):", value=1, min_value=1, step=1)
    stack_LT = col3.number_input("Select the stack lifetime (h):", value=120000, min_value=1, step=1)
    BoP_LT_y = col1.number_input("Select the BoP lifetime (years):", value=20, min_value=1, step=1)
    eff = col2.number_input("Select the stack efficiency (0 to 1):", value=0.72, min_value=0.0, max_value=1.0, step=0.01)
    #st.write("")
    cf = col3.number_input("Select the capacity factor (0 to 1):", value=0.9, min_value=0.01, step=0.05)
    renewable_coupling = col1.selectbox("Will your plant include solar panels?", ["Yes", "No"], index=1)
    storage_choice = col2.selectbox("How hydrogen is going to be stored?", ["Tank", "No storage"], index=1)


    # Give the password associated with your ecoinvent account

    #permanent_setting("username", "put_here_your_username")
    #permanent_setting("password", "put_here_your_password")
    #bw2io.import_ecoinvent_release("3.9.1", "cutoff")


    USER_DB = 'user-db'
    EI = 'ecoinvent 3.9.1 cutoff'
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

    EF = 'EF v3.0 no LT'

    climate = (EF, 'climate change no LT', 'global warming potential (GWP100) no LT')
    m_resources = (EF, 'material resources: metals/minerals no LT',
                   'abiotic depletion potential (ADP): elements (ultimate reserves) no LT')
    land = (EF, 'land use no LT', 'soil quality index no LT')
    water = (EF, 'water use no LT', 'user deprivation potential (deprivation-weighted water consumption) no LT')
    acidification = (EF, 'acidification no LT', 'accumulated exceedance (AE) no LT')
    marine_eutroph = (EF, 'eutrophication: marine no LT', 'fraction of nutrients reaching marine end compartment (N) no LT')
    freshwater_eutroph = (
    EF, 'eutrophication: freshwater no LT', 'fraction of nutrients reaching freshwater end compartment (P) no LT')
    terre_eutroph = (EF, 'eutrophication: terrestrial no LT', 'accumulated exceedance (AE) no LT')
    radiation = (EF, 'ionising radiation: human health no LT', 'human exposure efficiency relative to u235 no LT')
    non_renew = (EF, 'energy resources: non-renewable no LT', 'abiotic depletion potential (ADP): fossil fuels no LT')

    # Test if the chosen impacts are impact cathegories
    # bw.methods[climate]

    # List of the impacts
    impacts = [climate, m_resources, land, water, acidification, marine_eutroph, freshwater_eutroph, terre_eutroph,
               radiation, non_renew]
    # impacts

    Elec_FR_2023 = agb.findActivity("market for electricity, low voltage", loc="FR", single=False, db_name=EI)

    Elec_DE_2023 = agb.findActivity("market for electricity, low voltage", loc="DE", single=False, db_name=EI)

    Elec_FR_2050_BRM0 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=B50RM0)
    Elec_FR_2050_BRM1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=B50RM1)
    Elec_FR_2050_BRM23 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=B50RM23)
    Elec_FR_2050_BRN1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=B50RN1)
    Elec_FR_2050_BRN2 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=B50RN2)
    Elec_FR_2050_BRN03 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=B50RN03)
    Elec_FR_2050_R19RM0 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R1950RM0)
    Elec_FR_2050_R19RM1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R1950RM1)
    Elec_FR_2050_R19RM23 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R1950RM23)
    Elec_FR_2050_R19RN1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R1950RN1)
    Elec_FR_2050_R19RN2 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R1950RN2)
    Elec_FR_2050_R19RN03 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R1950RN03)
    Elec_FR_2050_R26RM0 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False, db_name=R2650RM0)
    Elec_FR_2050_R26RM1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R2650RM1)
    Elec_FR_2050_R26RM23 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R2650RM23)
    Elec_FR_2050_R26RN1 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R2650RN1)
    Elec_FR_2050_R26RN2 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R2650RN2)
    Elec_FR_2050_R26RN03 = agb.findActivity("market for electricity, low voltage, FE2050", loc="FR", single=False,
                                         db_name=R2650RN03)

    Elec_FR_2050_RM0E = agb.findActivity(name="market for electricity, low voltage M0",
                                         db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RM1E = agb.findActivity(name="market for electricity, low voltage M1",
                                         db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RM23E = agb.findActivity(name="market for electricity, low voltage M23",
                                          db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RN1E = agb.findActivity(name="market for electricity, low voltage N1",
                                         db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RN2E = agb.findActivity(name="market for electricity, low voltage N2",
                                         db_name='RTE scenarios with RTE imports')
    Elec_FR_2050_RN03E = agb.findActivity(name="market for electricity, low voltage N03",
                                         db_name='RTE scenarios with RTE imports')

    PV_coupled = agb.findActivity("electricity production, photovoltaic, 570kWp open ground installation, multi-Si",
                                  loc="FR", single=False, db_name=EI)

    water_H2 = agb.findBioAct("Water, unspecified natural origin", categories=('natural resource', 'in ground'))

    Oxygen = agb.findBioAct("Oxygen", categories=('air',))

    Occupation_ind = agb.findBioAct("Occupation, industrial area", categories=('natural resource', 'land'))

    Transformation_from_ind = agb.findBioAct("Transformation, from industrial area",
                                             categories=('natural resource', 'land'))

    Transformation_to_ind = agb.findBioAct("Transformation, to industrial area", categories=('natural resource', 'land'))

    Lorry_E6: agb.findActivity("market for transport, freight, lorry >32 metric ton, EURO6", single=False, db_name=EI)

    base = ["EFR2050BRM0", "EFR2050BRM1", "EFR2050BRM23", "EFR2050BRN1", "EFR2050BRN2", "EFR2050BRN03"]
    R19 = ["EFR2050R19RM0", "EFR2050R19RM1", "EFR2050R19RM23", "EFR2050R19RN1", "EFR2050R19RN2", "EFR2050R19RN03"]
    R26 = ["EFR2050R26RM0", "EFR2050R26RM1", "EFR2050R26RM23", "EFR2050R26RN1", "EFR2050R26RN2", "EFR2050R26RN03"]
    E_RTE = ["EFR2050RM0E", "EFR2050RM1E", "EFR2050RM23E", "EFR2050RN1E", "EFR2050RN2E", "EFR2050RN03E"]
    options = ["EFR2023", "EDE2023", "PV"]+base+R19+R26+E_RTE
    choice = col3.selectbox("Select the future electricity scenario:", options, index=0)


    tank = agb.findActivity(
        "high pressure storage tank production and maintenance, per 10kgH2 at 500bar, from grid electricity", single=False,
        db_name='AEC/PEM')

    NONE = newActivity(USER_DB,  # We define foreground activities in our own DB
                       "no activity, or zero impact activity",  # Name of the activity
                       "unit",  # Unit
                       exchanges={})



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


    def negAct(act):
        """Correct the sign of some activities that are accounted as negative in brightway. """
        return agb.newActivity(USER_DB, act["name"] + "_neg", act["unit"], {
            act: -1,
        })


    stack_activity = agb.findActivity(name=activity_names[stack_type]['Stack'], db_name='AEC/PEM')
    bop_activity = agb.findActivity(name=activity_names[stack_type]['BoP'], db_name='AEC/PEM')
    t_Stack_activity = negAct(agb.findActivity(name=activity_names[stack_type]['Treatment_Stack'], db_name='AEC/PEM'))
    t_BoP_activity = negAct(agb.findActivity(name=activity_names[stack_type]['Treatment_BoP'], db_name='AEC/PEM'))

    elec_cap = elec_cap_mw * 1000

    #table reference to guide user
    ref1_data = [
        ["", "AEC", "", "PEM", ""],
        ["", "Current,&nbsp;2019", "Future, 2050", "Current,&nbsp;2019", "Future, 2050"],
        ["Stack lifetime (operating hours)", "60,000-90,000", "100,000-150,000", "30,000-90,000", "100,000-150,000"],
    ]

    st.markdown("""
        <style>
            /* Importando o CSS do Font Awesome */
            @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css');
        </style>
    """, unsafe_allow_html=True)

    # Define the HTML content for the tooltip
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
            <span id="tooltip_trigger"><i class="fas fa-lightbulb"></i></span></span>
        </div>
    """

    #st.markdown(f'{tooltip_html}', unsafe_allow_html=True)

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

    # Add JavaScript and CSS to the page
    st.markdown(js_code, unsafe_allow_html=True)
    st.markdown(css_code, unsafe_allow_html=True)

    # BoP lifetime

    BoP_LT_h = BoP_LT_y * 365 * 24

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
            <span id="tooltip_trigger"><i class="fas fa-lightbulb"></i></span></span>
        </div>
    """

    #st.markdown(f'{tooltip_html2}', unsafe_allow_html=True)



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

    # capacity factor


    Electricity_consumed = BoP_LT_h * cf * elec_cap
    Ec = int(Electricity_consumed)
    Ec_GWh = Ec / 1000000  # Convert kWh to GWh

    # Higher heating value
    HHV = 39.4  # kWh/kg

    H2_produced = BoP_LT_h * cf * elec_cap * eff / HHV
    H2p = int(H2_produced)
    H2p_ton = H2p / 1000  # Convert kg to tons

    H2_per_hour = H2p / (BoP_LT_h * cf)

    Electricity_1kg = Electricity_consumed / H2_produced  # = HHV/eff
    E1 = round(Electricity_consumed / H2_produced, 2)



    n_stacks = BoP_LT_h / stack_LT



    param_electricity = agb.newEnumParam(
        "param_electricity",  # Short name
        label="electricity mix",  # English label
        description="RTE scenarios for FR electricity",  # Long description
        values=["EFR2023", "EDE2023", "PV"]+base+R19+R26+E_RTE,  # ["NONE"]
        default="EFR2023")

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
        "EFR2050RN03E": Elec_FR_2050_RN03E
    })

    if renewable_coupling == "Yes":
        hours_year = 365 * 24
        #"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat=45.256&lon=2.734&raddatabase=PVGIS-SARAH2&browser=1&outputformat=csv&userhorizon=&usehorizon=1&angle=0&aspect=1&startyear=2005&endyear=2005&mountingplace=free&optimalinclination=0&optimalangles=0&js=1&select_database_hourly=PVGIS-SARAH2&hstartyear=2005&hendyear=2005&trackingtype=0&hourlyangle=0&hourlyaspect=1&pvcalculation=1&pvtechchoice=crystSi&peakpower=1&loss=14"
        while True:
            with col1:
                import streamlit as st
                import folium
                from streamlit_folium import folium_static

                # Initialize session state to store clicked points
                if "clicked_points" not in st.session_state:
                    st.session_state["clicked_points"] = []

                # Create a Folium map
                m = folium.Map(location=[46.903354, 1.888334], zoom_start=5)

                # Define a callback function to handle map clicks
                def handle_click(lat, lon):
                    st.session_state["clicked_points"].append({"lat": lat, "lon": lon})

                # Add a click event handler to the map
                folium.Marker(
                    [46.903354, 1.888334],
                    icon=folium.Icon(color="blue"),
                    popup="Click me!",
                    callback=handle_click
                ).add_to(m)

                # Display the map using the Streamlit-Folium component
                folium_static(m)

                # Display clicked points
                if st.session_state["clicked_points"]:
                    st.write("Clicked Points:")
                    for point in st.session_state["clicked_points"]:
                        st.write(point)

            hours_sun_y = col1.number_input("What is the average number of hours of sun per year in your region?",
                                          key="hours_sun_y_input")
            break  # Exit the loop as number_input() already handles validation

        share_from_solar = int(hours_sun_y) / hours_year
        share_from_grid = 1 - share_from_solar
        col1.write(f"Share from solar: {share_from_solar:.2%}")
        col1.write(f"Share from grid: {share_from_grid:.2%}")

    def define_production():
        return agb.newActivity(USER_DB, "H2 production phase",
                               unit="unit",
                               exchanges={
                                   electricity: Electricity_1kg,
                                   water_H2: 0.0014,
                                   Oxygen: -8
                               })

    production = define_production()

    # land factors retrieved from Romain's LCI: no information was given regarding the references for these figures: *ask him!
    land_factor = 0.09 if stack_type == 'PEM' else 0.12

    BoP_LT_y = BoP_LT_h / 365 / 24

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
                                   Occupation_ind: land_factor / elec_cap / H2_produced / BoP_LT_y,
                                   Transformation_from_ind: land_factor / H2_produced,
                                   Transformation_to_ind: land_factor / H2_produced,
                                   eol: 1,
                               })

    infra = define_infrastructure()




    def storage(storage_choice):
        if storage_choice == "Tank":
            n_tanks = col2.number_input("How many tanks does your system require throughout its lifetime?", value=10, min_value=1, step=1)
            storage_key = "tank",
            dx = int(n_tanks) / H2_produced
        elif storage_choice == "No storage":
            storage_key = "NONE"
            dx = 1

        return agb.newActivity(USER_DB, "H2 storage",
                               unit="unit",
                               phase="distribution",
                               storage_key= dx
                               )

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



    def define_system():
        return agb.newActivity(USER_DB, name=choice,
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
        param_electricity=choice
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

    result_table_H2_styled = result_table_H2.style.set_table_styles(
        [{"selector": "th", "props": [("max-width", "100px")]},
         {"selector": "td", "props": [("max-width", "100px")]}]
    )

    st.markdown("---")
    st.markdown("## Results")
    st.markdown("#### Hydrogen Impact")

    # Display the styled DataFrame table
    st.table(result_table_H2_styled)



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
                                param_electricity=choice
                       ))

    #consequential

    a_infra = agb.findActivity("market for chemical factory, organics", loc='GLO', db_name=EI)
    ammonia_smr = agb.findActivity("market for ammonia, anhydrous, liquid", loc='RER', db_name=EI)
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
        param_electricity=choice
    )

    def define_Ammonia_smr():
        return agb.newActivity(USER_DB, name="Ammonia_smr production",
                               unit="unit",
                               exchanges={ammonia_smr: 1})

    Ammonia_smr = define_Ammonia_smr()

    result_table_ammonia_smr = agb.multiLCAAlgebric(
        Ammonia_smr,
        impacts,
        param_electricity=choice
    )

    st.session_state.result_table_ammonia = result_table_ammonia
    st.session_state.result_table_ammonia_smr = result_table_ammonia_smr



if __name__ == "__main__":
    show()

    def calculate_result():
        # Calculate result_table_H2_styled
        result_table_ammonia = ...

        # Extract the first number from the table
        result = result_table_ammonia[0]

        return result










