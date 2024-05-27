import pandas as pd
from urllib.request import urlopen
from tempfile import NamedTemporaryFile
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

PV=5000*1.3
URL = f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat=43.4928&lon=6.8555&raddatabase=PVGIS-SARAH2&browser=1&outputformat=csv&userhorizon=&usehorizon=1&angle=&aspect=&startyear=2020&endyear=2020&mountingplace=free&optimalinclination=0&optimalangles=1&js=1&select_database_hourly=PVGIS-SARAH2&hstartyear=2020&hendyear=2020&trackingtype=0&hourlyoptimalangles=1&pvcalculation=1&pvtechchoice=crystSi&peakpower={PV}&loss=14&components=1"

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
#total_sum_real_day = daily_sums_24['Total_elec_W_day_24'].sum()
merged_df = pd.merge(daily_sums, daily_sums_24, on='Date')

# Calculate the difference
merged_df['Difference'] = merged_df['Total_elec_W_day'] - merged_df['Total_elec_W_day_24']

# Create the new DataFrame with 'Date' and 'Difference'
diff_column = merged_df[['Date', 'Difference']]

# Rename the columns if needed
diff_column.columns = ['Date', 'Total_elec_W_day_Difference']

total_sum_real_year = daily_sums['Total_elec_W_day'].sum() #=TOTAL_power_produced = df['elec_W'].sum()
total_sum_real_day = daily_sums_24['Total_elec_W_day_24'].sum()
credit_minus_daily_extra = diff_column['Total_elec_W_day_Difference'].sum()

TOTAL_power_produced = df['elec_W'].sum()
capped_values = df['elec_W'].clip(upper=1*1000000)
real_consumption = capped_values.sum()
credit=TOTAL_power_produced-real_consumption


print(daily_sums)
print(daily_sums_24)
print(diff_column)
print(total_sum_real_year)
print(total_sum_real_day)
print(TOTAL_power_produced)
print(real_consumption)
print(f"credit: {credit}")
print(f"not credit: {credit_minus_daily_extra}")

