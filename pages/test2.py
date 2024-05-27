import pandas as pd
import streamlit as st
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
pv_cap_MW=3
elec_cap_MW=1
URL = f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat=43.4928&lon=6.8555&raddatabase=PVGIS-SARAH2&browser=1&outputformat=csv&userhorizon=&usehorizon=1&angle=&aspect=&startyear=2020&endyear=2020&mountingplace=free&optimalinclination=0&optimalangles=1&js=1&select_database_hourly=PVGIS-SARAH2&hstartyear=2020&hendyear=2020&trackingtype=0&hourlyoptimalangles=1&pvcalculation=1&pvtechchoice=crystSi&peakpower={pv_cap_MW * 1000 * 1.3}&loss=14&components=1"

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

# Convert 'elec_W' column to numeric, handling possible conversion issues
df['elec_W'] = pd.to_numeric(df['elec_W'], errors='coerce')

# Sum of all elec_W figures
TOTAL_power_produced = df['elec_W'].sum()
capped_values = df['elec_W'].clip(upper=elec_cap_MW * 1000000)
real_consumption = capped_values.sum()
credit = TOTAL_power_produced - real_consumption

hours_year = 366 * 24  # 2020 has 366 days
necessary_power = elec_cap_MW * 1000 * hours_year  # kwh
pv_credit = necessary_power - TOTAL_power_produced / 1000
grid = necessary_power - real_consumption / 1000

percentage_grid = grid / necessary_power
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
daily_sums = df.groupby('Date')['elec_W'].sum().reset_index()
daily_sums_24 = df.groupby('Date')['elec_W'].sum().reset_index()

# Rename columns for clarity
daily_sums.columns = ['Date', 'Total_elec_W_day']
daily_sums_24.columns = ['Date', 'Total_elec_W_day_24']

max_value = 24000000  # Adjust this value to your desired cap

daily_sums_24['Total_elec_W_day_24'] = daily_sums_24['Total_elec_W_day_24'].clip(upper=max_value)
# total_sum_real_day = daily_sums_24['Total_elec_W_day_24'].sum()
merged_df = pd.merge(daily_sums, daily_sums_24, on='Date')

# Calculate the difference
merged_df['Difference'] = merged_df['Total_elec_W_day'] - merged_df['Total_elec_W_day_24']

# Create the new DataFrame with 'Date' and 'Difference'
diff = merged_df[['Date', 'Difference']]

# Rename the columns if needed
diff.columns = ['Date', 'Total_elec_W_day_Difference']

total_sum_real_year = daily_sums['Total_elec_W_day'].sum()  # =TOTAL_power_produced = df['elec_W'].sum()
total_sum_real_day = daily_sums_24['Total_elec_W_day_24'].sum()
credit_minus_daily_extra = diff['Total_elec_W_day_Difference'].sum()
pv_credit = necessary_power - TOTAL_power_produced / 1000
grid = necessary_power - real_consumption / 1000
pv_credit_daily = necessary_power - total_sum_real_day / 1000
extra_credit_from_total_credit = credit - credit_minus_daily_extra


print(daily_sums)
print(daily_sums_24)
print(diff)
print(total_sum_real_year)
print(total_sum_real_day)
print(TOTAL_power_produced)
print(real_consumption)
print(f"credit: {pv_credit}")
print(f"not credit: {credit_minus_daily_extra}")

