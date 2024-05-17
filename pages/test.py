from urllib.request import urlopen
from tempfile import NamedTemporaryFile
import pandas as pd

URL = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat=43.667&lon=5.596&raddatabase=PVGIS-SARAH2&browser=1&outputformat=csv&userhorizon=&usehorizon=1&angle=&aspect=&startyear=2020&endyear=2020&mountingplace=free&optimalinclination=0&optimalangles=1&js=1&select_database_hourly=PVGIS-SARAH2&hstartyear=2020&hendyear=2020&trackingtype=0&hourlyoptimalangles=1&pvcalculation=1&pvtechchoice=crystSi&peakpower=1300&loss=14&components=1"

# Create a temporary file to save the CSV data
o = NamedTemporaryFile(suffix=".csv", delete=False)

# Download the CSV data
r = urlopen(URL)
o.write(r.read())
o.close()

# Initialize variables
data = []
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
                data.append([columns[0], columns[1]])

# Create a DataFrame from the data and name the columns
df = pd.DataFrame(data, columns=header)

# Convert 'elec_W' column to numeric, handling possible conversion issues
df['elec_W'] = pd.to_numeric(df['elec_W'], errors='coerce')

# Display the first few rows of the DataFrame
#print(df.head())
#print(df)
#print(df.iloc[:20, :])

# Define the threshold (10% of 1,000,000)
threshold = 0.05 * 1000000

# Sum of all elec_W figures
total_sum = df['elec_W'].sum()

# Sum of elec_W figures excluding values smaller than the threshold
filtered_sum = df[df['elec_W'] >= threshold]['elec_W'].sum()

real_power_pv=(total_sum)/1000#convert to kw
hours_year = 366 * 24 #2020 has 366 days
necessary_power=1000*hours_year #kwh
grid=necessary_power-real_power_pv
print(real_power_pv)
print(hours_year)
print(grid/necessary_power)

