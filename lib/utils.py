from io import StringIO
from urllib.request import urlopen

from six import BytesIO
from streamlit import cache_data
from streamlit.web.cli import cache
import pandas as pd
CONSTANT=34

INTERVAL_H = 1

def some_func() :
    return 2


@cache_data
def get_pv_prod_data(lat, lon, pv_cap_kW) :
    URL = f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat={lat:.3f}&lon={lon:.3f}&raddatabase=PVGIS-SARAH2&browser=1&outputformat=csv&userhorizon=&usehorizon=1&angle=&aspect=&startyear=2020&endyear=2020&mountingplace=free&optimalinclination=0&optimalangles=1&js=1&select_database_hourly=PVGIS-SARAH2&hstartyear=2020&hendyear=2020&trackingtype=0&hourlyoptimalangles=1&pvcalculation=1&pvtechchoice=crystSi&peakpower={pv_cap_kW}&loss=14&components=1"  # pc_cap_kW*1.3
    # https://www.sciencedirect.com/science/article/pii/S0360319922045232#fig1  paper with another variation >> h2 produced only with enought electricity from PV

    # Create a temporary file to save the CSV data

    # Download the CSV data
    r = urlopen(URL)
    o = StringIO(r.read().decode())

    # Initialize variables
    data2 = []
    start_line = 12  # Line to start reading the actual data
    header = ["DateTime", "elec_W"]

    # Read the CSV file starting f
    o.seek(0)

    for i, line in enumerate(o):
        if i >= start_line:
            # Stop reading if an empty line is encountered
            if line.strip() == "":
                break
            # Split the line by commas and select only the first and second columns
            columns = line.strip().split(',')
            if len(columns) >= 2:
                data2.append([columns[0], columns[1]])

    df = pd.DataFrame(data2, columns=header)

    # Convert 'elec_W' column to numeric, handling possible conversion issues
    df['elec_W'] = pd.to_numeric(df['elec_W'], errors='coerce')
    df['elec_Wh'] = df['elec_W'] * INTERVAL_H
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%Y%m%d:%H%M')

    # Filter out 29th February as 2020 has 366 days
    df = df[~((df['DateTime'].dt.month == 2) & (df['DateTime'].dt.day == 29))]

    return df