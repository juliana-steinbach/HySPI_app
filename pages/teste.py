import lca_algebraic as agb
from lca_algebraic import *
import folium
import pandas as pd
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from streamlit_extras.colored_header import colored_header
import time
from opencage.geocoder import OpenCageGeocode
import matplotlib.pyplot as plt

import streamlit as st
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
import streamlit as st
from opencage.geocoder import OpenCageGeocode
import folium



cf=1
electro_capacity_W=20000000
pv_cap_MW = 100
pv_cap_kW=pv_cap_MW*1_000 #website requires pv capacity to be in kWp

data = [38.5482, -4.3506]

URL = f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat=38.5482&lon=-4.3506&raddatabase=PVGIS-SARAH2&browser=1&outputformat=csv&userhorizon=&usehorizon=1&angle=&aspect=&startyear=2020&endyear=2020&mountingplace=free&optimalinclination=0&optimalangles=1&js=1&select_database_hourly=PVGIS-SARAH2&hstartyear=2020&hendyear=2020&trackingtype=0&hourlyoptimalangles=1&pvcalculation=1&pvtechchoice=crystSi&peakpower={pv_cap_kW* 1.3}&loss=14&components=1"
#https://www.sciencedirect.com/science/article/pii/S0360319922045232#fig1  paper with another variation >> h2 produced only with enought electricity from PV

# Create a temporary file to save the CSV data
o = NamedTemporaryFile(suffix=".csv", delete=False)

# Download the CSV data
r = urlopen(URL)
o.write(r.read())
o.close()

# Initialize variables
data2 = []
start_line = 12  # Line to start reading the actual data
header = ["DateTime", "elec_W"]

# Read the CSV file starting from the 12th line
with open(o.name, 'r') as file:
    for i, line in enumerate(file):
        if i >= start_line:
            # Stop reading if an empty line is encountered
            if line.strip() == "":
                break
            # Split the line by commas and select only the first and second columns
            columns = line.strip().split(',')
            if len(columns) >= 2:
                data2.append([columns[0], columns[1]])

df = pd.DataFrame(data2, columns=header)
interval_h=1 #hourly

# Convert 'elec_W' column to numeric, handling possible conversion issues
df['elec_W'] = pd.to_numeric(df['elec_W'], errors='coerce')
df['elec_Wh'] = df['elec_W'] * interval_h
df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y%m%d:%H%M')

# Filter out 29th February as 2020 has 366 days
df = df[~((df['DateTime'].dt.month == 2) & (df['DateTime'].dt.day == 29))]

# Sum of all elec_W figures
TOTAL_elec_produced_Wh = df['elec_Wh'].sum()
capped_values = df['elec_Wh'].clip(upper=electro_capacity_W*interval_h) #all values under electro_capacity_Wh
real_consumption_Wh = capped_values.sum()
credit = TOTAL_elec_produced_Wh - real_consumption_Wh #100% credit, all goes from PV to grid #change for surplus

hours_year = 365 * 24
necessary_elec_Wh = electro_capacity_W * cf * hours_year  # here we add the capacity factor because this is related to electrolyzer's consumption
grid = necessary_elec_Wh - real_consumption_Wh #consumed from the grid
pv_credit_Wh = necessary_elec_Wh - TOTAL_elec_produced_Wh  #keeping this here as it helps to understand the situation in which all PV production is allocated to the impacts rather than the grig

percentage_grid = grid / necessary_elec_Wh
percentage_pv = 1 - percentage_grid

percentage_grid_real = min(max(percentage_grid, 0), 1)
percentage_pv_real = min(max(percentage_pv, 0), 1)

#should we add 1-cf duration so we stop hydrogen operation when the production is little?

# monthly cap begins here:
# Extract month and year part and create a new column
df['YearMonth'] = df['DateTime'].dt.to_period('m')

# Group by the month and sum the 'elec_Wh' values
monthly_sums = df.groupby('YearMonth')['elec_Wh'].sum().reset_index()
monthly_sums_M = df.groupby('YearMonth')['elec_Wh'].sum().reset_index()  # here they are the same thing

# Rename columns for clarity
monthly_sums.columns = ['YearMonth', 'Total_elec_Wh_month']
monthly_sums_M.columns = ['YearMonth', 'Total_elec_Wh_month_M']  # creating a new name for monthly cap

# Monthly cap
max_value = 24 * electro_capacity_W * df[
    'DateTime'].dt.days_in_month.unique().max()  # Adjust for the maximum days in any month

monthly_sums_M['Total_elec_Wh_month_M'] = monthly_sums_M['Total_elec_Wh_month_M'].clip(
    upper=max_value)  # capping value
merged_df = pd.merge(monthly_sums, monthly_sums_M, on='YearMonth')

# Calculate the difference
merged_df['Difference'] = merged_df['Total_elec_Wh_month'] - merged_df['Total_elec_Wh_month_M']

# Created the new DataFrame with 'YearMonth' and 'Difference'
diff = merged_df[['YearMonth', 'Difference']]

diff.columns = ['YearMonth', 'Total_elec_Wh_month_Difference']

total_sum_real_month_Wh = monthly_sums_M['Total_elec_Wh_month_M'].sum()
credit_minus_monthly_extra_Wh = diff['Total_elec_Wh_month_Difference'].sum()
pv_credit_monthly_Wh = necessary_elec_Wh - total_sum_real_month_Wh

print(f'TOTAL_elec_produced_Wh {TOTAL_elec_produced_Wh/1000000}')
print(f'real_consumption_Wh {real_consumption_Wh/1000000}')
print(f'total_sum_real_month_Wh {total_sum_real_month_Wh/1000000}')
print(f'necessary_elec_Wh {necessary_elec_Wh/1000000}')
print(f'pv_credit_monthly_Wh {pv_credit_monthly_Wh/1000000}')
print(f'max_value {max_value/1000000}')