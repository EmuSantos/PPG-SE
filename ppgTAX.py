"""
##################################################################################
##                      Pico y Placa Generator - TAXI Edition                    ##
##                         Environmental Zone Project                            ##
##                          Here Technologies (2025)                             ##
##                      Created by Emi Santos Tinoco - SDS1                      ##
##                            Last Updated: 19 March 2025                        ##
##################################################################################
##                                                                               
## DESCRIPTION:                                                                  
## This Python application generates vehicle restriction metadata for taxi plates
## in Environmental Zones (EZ) using Streamlit. It allows users to:
##  - Input license plates manually by day.
##  - Select custom date ranges and holiday exclusions.
##  - Group dates into consecutive weekly blocks, even if weeks are incomplete.
##  - Dynamically select EZ_Tag values (LicensePlate, Ending, Starting).
##  - Export the results as a CSV file for further processing.    
##                                                                               
## USAGE INSTRUCTIONS:                                                           
## 1. Install required libraries using pip:                                       
##    pip install streamlit pandas                                               
##                                                                               
## 2. Run the application locally:                                               
##    streamlit run pico_y_placa_taxi.py                                         
##                                                                               
## 3. Features:                                                                  
##    - Select date ranges and input holidays.                                    
##    - Select the EZ_Tag (LicensePlate, Ending, Starting) dynamically.           
##    - Input plate numbers by day, grouped by consecutive weekly blocks.         
##    - Generate a DataFrame and export it as a CSV.                              
##                                                                               
## DEPENDENCIES:                                                                 
## - Python 3.8+                                                                 
## - Streamlit 1.30+                                                             
## - Pandas 2.0+                                                                 
##                                                                               
## Notes:
## - Ensure all required fields are correctly filled before generating the DataFrame.
## - The tool prevents duplicate records from being added.
## - Open-source and adaptable for specific implementation needs.

## License:
## - This project follows an open-source model. Users can modify the code to 
##   suit their requirements while maintaining proper attribution.

"""


import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

# Streamlit Config
st.title('Pico y Placa Generator - TAXI Edition')

# Holidays
holidays = st.text_area(
    "Holidays (format DDMMYYYY):",
    value='01012025, 31122025'
)
holidays = holidays.replace(" ", "").split(',')

# Convert holidays to datetime
holiday_dates = [datetime.strptime(date, '%d%m%Y').date() for date in holidays]

# Function to add records
def addreg(EZname, EZid, Vcat, VcatID, EZvr_value, EZkeyid_value, EZkeyname, EZtag, EZval, timeft, dayft, monthft, dateft):
    return {
        'ENVZONE_NAME': EZname,
        'ENVZONE_ID': EZid,
        'Restriction_id': '',
        'vehicle_category': Vcat,
        'vehicle_category_id': VcatID,
        'EZ_VR_VALUES': EZvr_value,
        'EZ_KEY_ID': EZkeyid_value,    # Dynamic EZ_KEY_ID
        'EZ_KEY_NAMES': EZkeyname,
        'EZ_ADDT_TAG': EZtag,
        'EZ_VALUES': EZval,
        'timeFrom_timeTo': timeft,
        'dayFrom_dayTo': dayft,
        'monthFrom_monthTo': monthft,
        'dateFrom_dateTo': f'{dateft}-{dateft}'
    }

# Date conversion helpers
def monthm(varmonth):
    """Convert date to 'MM' format."""
    return varmonth.strftime('%m')

def dayy(varname):
    """Map weekday names to 'DD' format."""
    day_map = {
        'Monday': '02',
        'Tuesday': '03',
        'Wednesday': '04',
        'Thursday': '05',
        'Friday': '06',
        'Saturday': '07',
        'Sunday': '01'
    }
    return day_map.get(varname, '')

# Ez_Tag Values (dynamic mapping)
Ez_Tag = {
    'LicensePlate': 3,
    'LicensePlateEnding': 5,
    'LicensePlateStarting': 7
}

# Constants for Taxi
EZname = st.text_input('Zone Name:', 'Pico y Placa - TAXI')
EZid = st.text_input('Zone ID:', '')
EZvr_value = 'LIC_PLATE'

# **Dynamic selection for Ez_Tag**
selected_tag = st.selectbox("Select EZ Tag:", list(Ez_Tag.keys()))
EZkeyid_value = Ez_Tag[selected_tag]  # Dynamically update EZ_KEY_ID
EZkeyname = 'License Plate Number'

# Date range selection
startdate = st.date_input('Start day:', datetime(2025, 1, 1))
enddate = st.date_input('End day:', datetime(2025, 12, 31))
times = st.text_input('Time Range:', '00:00-23:59')

# Group dates by month
day_count = (enddate - startdate).days + 1
dates_by_month = {}

for n in range(day_count):
    current_date = startdate + timedelta(days=n)

    # Skip holidays
    if current_date in holiday_dates:
        continue

    month_name = current_date.strftime('%B %Y')
    
    if month_name not in dates_by_month:
        dates_by_month[month_name] = []

    dates_by_month[month_name].append(current_date)

# ** Group dates into consecutive weekly blocks **
def group_by_consecutive_weeks(dates):
    """Groups dates by consecutive weeks, even if they don't start on Monday."""
    weeks = []
    current_week = []

    for date in dates:
        # Append dates into weeks
        if len(current_week) == 7 or (len(current_week) > 0 and date.weekday() == 0):
            weeks.append(current_week)
            current_week = []

        current_week.append(date)

    # Append the last week
    if current_week:
        weeks.append(current_week)

    return weeks

# Display plate number input by month in weekly blocks
plates_per_day = {}

st.write("### Enter plate numbers by month (consecutive weeks):")

for month, dates in dates_by_month.items():
    weeks = group_by_consecutive_weeks(dates)

    with st.expander(f"📅 {month}", expanded=False):  # Collapsible month section
        for week_num, week_dates in enumerate(weeks, start=1):
            st.write(f"**Week {week_num}**")

            num_days = len(week_dates)
            cols = st.columns(num_days)  # Columns for each day in the week

            for i, date in enumerate(week_dates):
                weekday = date.strftime('%A')
                plate_input = cols[i].text_area(
                    f"{weekday} - {date.strftime('%d')}", 
                    key=f"{month}_{date.strftime('%d')}"
                )

                plates = [plate.strip() for plate in plate_input.split(',') if plate.strip()]

                if plates:
                    plates_per_day[date] = plates

# Generate records
if 'records_taxi' not in st.session_state:
    st.session_state.records_taxi = []

def generate_taxi_records():
    for date, plates in plates_per_day.items():
        day_ft = dayy(date.strftime('%A'))
        month_ft = monthm(date)

        for plate in plates:
            record = addreg(
                EZname, EZid, 'TAXI', 14, EZkeyname,  EZvr_value, selected_tag, EZkeyid_value, plate, times, day_ft, month_ft, date.strftime("%Y%m%d"))

            # Avoid duplicates
            if record not in st.session_state.records_taxi:
                st.session_state.records_taxi.append(record)

# Generate DataFrame
if st.button("Generate DataFrame"):
    if plates_per_day:
        generate_taxi_records()
        st.success("Records generated successfully.")
    else:
        st.error("Please enter plate numbers for at least one day.")

# Display DataFrame
df_taxi = pd.DataFrame(st.session_state.records_taxi)
st.write('### DataFrame:')
st.dataframe(df_taxi)

# Export DataFrame to CSV
csv = df_taxi.to_csv(index=False, quoting=1).encode('utf-8')

st.download_button(
    label="Download CSV",
    data=csv,
    file_name='PicoYPlaca_TAXI.csv',
    mime='text/csv',
)
