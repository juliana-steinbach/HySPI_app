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

# Display the first few rows of the DataFrame
# print(df.head())
# print(df)
#print(df.iloc[:20, :])

# Define the threshold (10% of 1,000,000)
threshold = 0.05 * 1000000

# Sum of all elec_W figures
total_sum100PV = df['elec_W'].sum()
capped_values = df['elec_W'].clip(upper=1000000)
total_sum_real = capped_values.sum()

# Calculate the difference that is left out
difference_left_out = df['elec_W'].sum() - total_sum_real

print(total_sum100PV)
print(total_sum_real)
print(difference_left_out)

power_pv100 = (total_sum100PV) / 1000  # convert to kw
power_pv_real = (total_sum_real) / 1000  # convert to kw
hours_year = 366 * 24  # 2020 has 366 days
necessary_power = 1000 * hours_year  # kwh
grid100 = necessary_power - power_pv100
grid=necessary_power - power_pv_real

percentage_grid = grid100 / necessary_power
percentage_pv=1-percentage_grid

percentage_grid_real = grid / necessary_power
percentage_pv_real = 1 - percentage_grid_real

print(grid100)
print(grid)

print(percentage_grid)
print(percentage_pv)

print(percentage_grid_real)
print(percentage_pv_real)