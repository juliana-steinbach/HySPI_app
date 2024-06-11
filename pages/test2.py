import pandas as pd
import streamlit as st
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

pv_cap_MW=100
pv_cap_kW=pv_cap_MW*1000
pv_cap_W=pv_cap_kW*1000

elec_cap_MW=20
elec_cap_W= elec_cap_MW*1000000
URL = f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat=38.6860347&lon=-4.1121461&raddatabase=PVGIS-SARAH2&browser=1&outputformat=csv&userhorizon=&usehorizon=1&angle=&aspect=&startyear=2020&endyear=2020&mountingplace=free&optimalinclination=0&optimalangles=1&js=1&select_database_hourly=PVGIS-SARAH2&hstartyear=2020&hendyear=2020&trackingtype=0&hourlyoptimalangles=1&pvcalculation=1&pvtechchoice=crystSi&peakpower={pv_cap_kW * 1.3}&loss=14&components=1"

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

# Create a DataFrame from the data and name the columns
df = pd.DataFrame(data2, columns=header)
interval_h=10/60

# Convert 'elec_W' column to numeric, handling possible conversion issues
df['elec_W'] = pd.to_numeric(df['elec_W'], errors='coerce')
df['elec_Wh'] = df['elec_W'] * interval_h

# Sum of all elec_W figures
TOTAL_power_produced_Wh = df['elec_Wh'].sum()
capped_values = df['elec_Wh'].clip(upper=elec_cap_W*interval_h)
real_consumption_Wh = capped_values.sum()
credit = TOTAL_power_produced_Wh - real_consumption_Wh

hours_year = 366 * 24
necessary_power_Wh = elec_cap_W * hours_year  #*cf kwh here we add the capacity factor
pv_credit_Wh = necessary_power_Wh - TOTAL_power_produced_Wh
grid = necessary_power_Wh - real_consumption_Wh

percentage_grid = grid / necessary_power_Wh
percentage_pv = 1 - percentage_grid

percentage_grid_real = min(max(percentage_grid, 0), 1)
percentage_pv_real = min(max(percentage_pv, 0), 1)

st.markdown(
    """
    <style>
    .right-align {
        text-align: right !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Create two columns within col2 for the table layout
row1_col1, row1_col2 = st.columns([4, 1])
row2_col1, row2_col2 = st.columns([4, 1])

# Fill the first row
row1_col1.write("percentage from grid:")
row1_col2.write(f'<p class="right-align">{percentage_grid_real:.2%}</p>', unsafe_allow_html=True)

# Fill the second row
row2_col1.write("percentage from PV:")
row2_col2.write(f'<p class="right-align">{percentage_pv_real:.2%}</p>', unsafe_allow_html=True)
# new part

df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y%m%d:%H%M')

# Extract date part and create a new column
df['Date'] = df['DateTime'].dt.date

# Group by the date and sum the 'elec_W' values
daily_sums = df.groupby('Date')['elec_Wh'].sum().reset_index()
daily_sums_24 = df.groupby('Date')['elec_Wh'].sum().reset_index()

# Rename columns for clarity
daily_sums.columns = ['Date', 'Total_elec_Wh_day']
daily_sums_24.columns = ['Date', 'Total_elec_Wh_day_24']

max_value = 24 * elec_cap_W  #*cf

#daily_sums_24['Total_elec_Wh_day_24'] = daily_sums_24['Total_elec_Wh_day_24'].clip(upper=max_value)
# total_sum_real_day = daily_sums_24['Total_elec_Wh_day_24'].sum()
merged_df = pd.merge(daily_sums, daily_sums_24, on='Date')

# Calculate the difference
merged_df['Difference'] = merged_df['Total_elec_Wh_day'] - merged_df['Total_elec_Wh_day_24']

# Create the new DataFrame with 'Date' and 'Difference'
diff = merged_df[['Date', 'Difference']]

# Rename the columns if needed
diff.columns = ['Date', 'Total_elec_Wh_day_Difference']

total_sum_real_year_Wh = daily_sums['Total_elec_Wh_day'].sum()  # =TOTAL_power_produced = df['elec_W'].sum()
total_sum_real_day_Wh = daily_sums_24['Total_elec_Wh_day_24'].sum()
credit_minus_daily_extra_Wh = diff['Total_elec_Wh_day_Difference'].sum()
pv_credit_daily = necessary_power_Wh - total_sum_real_day_Wh / 1000
extra_credit_from_total_credit = credit - credit_minus_daily_extra_Wh


print(daily_sums)
print(daily_sums_24)
print(diff)
print(total_sum_real_year_Wh)
print(total_sum_real_day_Wh)
print(f"TOTAL_power_produced_Wh: {TOTAL_power_produced_Wh/1000000}")
print(real_consumption_Wh)
print(f"credit: {pv_credit_Wh}")
print(f"not credit: {credit_minus_daily_extra_Wh}")
print(f"pv_cap_kW: {pv_cap_kW}")

