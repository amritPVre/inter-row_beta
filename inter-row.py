import streamlit as st
import pvlib
from pvlib import irradiance
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pytz
import pandas as pd


st.title('Solar PV Array Inter-table Distance Calculator')

# User inputs
latitude = st.number_input('Enter latitude:', value=22.50)
longitude = st.number_input('Enter longitude:', value=73.80)
date = st.date_input('Select date:', datetime.now())
time = st.time_input('Select time:', datetime.now())
tilt = st.number_input('Enter tilt angle (degrees):', value=20.0)
azimuth = st.number_input('Enter azimuth angle (degrees):', value=180.0)
module_height = st.number_input('Enter module height (m):', value=2.2)
module_width = st.number_input('Enter module width (m):', value=1.1)
num_rows = st.number_input('Enter number of rows in a table:', value=2, format='%d')
table_height = st.number_input('Enter table height from ground (m):', value=0.5)
timezone = st.sidebar.selectbox("Timezone", pytz.all_timezones, index=pytz.all_timezones.index("Asia/Calcutta"))

# Convert date and time to datetime object
timestamp = datetime.combine(date, time)

# Adjust the timestamp for the provided timezone
timestamp = pytz.timezone(timezone).localize(timestamp)

# Create location object
location = pvlib.location.Location(latitude, longitude, tz=timezone)

# Calculate the total height of the PV table (rows stacked)
total_table_height = module_height * num_rows + table_height

# Adjust the table height based on the tilt angle
table_height_tilt_adjusted = total_table_height * np.sin(np.radians(90 - tilt))

# Calculate solar position
solpos = location.get_solarposition(timestamp)

# Calculate AOI
aoi = irradiance.aoi(tilt, azimuth, solpos['apparent_zenith'], solpos['azimuth'])

#clearsky irradiance values
datetime = pd.date_range(date, periods=24, freq='H', tz=timezone)
# Calculate solar position
solar_position = location.get_solarposition(datetime)
# Calculate clear sky irradiance components
clearsky = location.get_clearsky(datetime)
#clearsky = location.get_clearsky(timestamp)
ghi=clearsky['ghi']
st.write(ghi)

# Calculate the length of the shadow
shadow_length = (table_height_tilt_adjusted * np.tan(np.radians(aoi))).item()

# Calculate inter-table distance
inter_table_distance = shadow_length + module_width

if np.isnan(inter_table_distance) or np.isinf(inter_table_distance):
    st.error("Inter-table distance calculation resulted in an invalid number. Please check your inputs.")
    st.stop()

st.write(f'Inter-table distance: {inter_table_distance} m')

# Plot
fig, ax = plt.subplots()

# Create array of table positions
try:
    table_positions = np.array([0, inter_table_distance])
except ValueError:
    st.error("Failed to create table positions array. Please check your inputs.")
    st.stop()

ax.plot(table_positions, [table_height_tilt_adjusted, table_height_tilt_adjusted], label='PV Tables')
ax.plot([0, shadow_length], [table_height_tilt_adjusted, 0], label='Shadow')

ax.legend()
ax.set_xlabel('Distance (m)')
ax.set_ylabel('Height (m)')
ax.set_title('Inter-table Distance and Shadow')

st.pyplot(fig)
