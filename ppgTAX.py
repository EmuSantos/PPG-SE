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
st.title('Pico y Placa Generator - Special Situation')

# Feriados por país
holidays_by_country = {
    "Colombia": "01012025, 06012025, 24032025, 17042025, 18042025, 01052025, 02062025, 23062025, 30062025, 20072025, 07082025, 18082025, 13102025, 03112025, 17112025, 08122025, 25122025",
    "México": "01012025, 03022025, 03032025, 17032025, 17042025, 18042025, 01052025, 05052025, 16092025, 03112025, 17112025, 25122025",
    "Brazil": "01012025, 01032025, 02032025, 03032025, 04032025, 05032025, 18042025, 21042025, 01052025, 07092025, 12102025, 02112025, 15112025, 24122025, 25122025, 31122025",
    "Costa Rica": "01012025, 19032025, 11042025, 17042025, 18042025, 01052025, 25072025, 02082025, 15082025, 15092025, 12102025, 24122025, 25122025",
    "Bolivia": "01012025, 22012025, 03032025, 04032025, 18042025, 01052025, 19062025, 21062025, 06082025, 02112025, 03112025, 25122025",
    "Ecuador": "01012025, 03032025, 04032025, 18042025, 01052025, 24052025, 10082025, 09102025, 02112025, 03112025, 25122025",
    "Perú": "01012025, 17042025, 18042025, 01052025, 07062025, 29062025, 23072025, 28072025, 29072025, 06082025, 30082025, 08102025, 01112025, 08122025, 09122025, 25122025",
    "Chile": "01012025, 18042025, 19042025, 01052025, 21052025, 07062025, 20062025, 29062025, 16072025, 15082025, 20082025, 18092025, 19092025, 12102025, 31102025, 01112025, 16112025, 08122025, 14122025, 25122025, 31122025"
}

# Select Country
country = st.selectbox("Select a country's public holidays:", list(holidays_by_country.keys()))
selected_holidays = holidays_by_country[country]

# Add Manually if needed
manual_holidays = st.text_area(
    "Or add holidays manually (format DDMMYYYY, separated by commas):",
    value=selected_holidays
)

# Process Holidays
holidays = manual_holidays.replace(" ", "").split(',')

# Convert holidays to datetime
holiday_dates = [datetime.strptime(date, '%d%m%Y').date() for date in holidays]

# Function to create a record
def addreg(EZname, EZid, Vcat, VcatID, EZvr_value, EZkeyid_value, EZkeyname, EZtag, EZval, timeft, dayft, monthft, dateft):
    return {
        'ENVZONE_NAME': EZname,
        'ENVZONE_ID': EZid,
        'Restriction_id': '',
        'vehicle_category': Vcat,
        'vehicle_category_id': VcatID,
        'EZ_VR_VALUES': EZvr_value,
        'EZ_KEY_ID': EZkeyid_value,
        'EZ_KEY_NAMES': EZkeyname,
        'EZ_ADDT_TAG': EZtag,
        'EZ_VALUES': EZval,
        'timeFrom_timeTo': timeft,
        'dayFrom_dayTo': dayft,
        'monthFrom_monthTo': monthft,
        'dateFrom_dateTo': f'{dateft}-{dateft}'
    }

# Convert month to 'MM' format
def monthm(varmonth):
    return varmonth.strftime('%m')

# Convert days to 'DD-DD'
def dayy(varname):
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

# Vehicle Categories and value
vehicle_categories = {
    'AUTO': 3,
    'CARPOOL': 16,
    'MOTORCYCLE': 2,
    'THROUGH_TRAFFIC': 15,
    'TAXI': 14,
    'TRUCK': 6,
    'BUS': 13
}

# Ez_VehicleRestriction Values
EZvr_values = {
    'License Plate Number': 'LIC_PLATE',
    'OVERRIDE': 'OVERRIDE',
    'Max_Total_Weight': 'MAX_TOTAL_WGHT'
}

# Ez_Tag Values
Ez_Tag = {
    'LicensePlate': 3,
    'LicensePlateEnding': 5,
    'LicensePlateStarting': 7
}

# Insert text
EZname = st.text_input('Zone Name:', 'Pico y Placa')
selected_categories = st.multiselect('Vehicle Categories:', list(vehicle_categories.keys()))
EZid = st.text_input('Zone ID:', '')
EZvr_selected = st.selectbox('Vehicle Restriction Value:', list(EZvr_values.keys()))
EZtag_selected = st.selectbox('EzTag:', list(Ez_Tag.keys()))
startdate = st.date_input('Start day:', datetime(2025, 1, 1))
enddate = st.date_input('End Day:', datetime(2025, 12, 31))
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


# Display weekly input by month
plates_per_day = {}

st.write("### Enter plate numbers")

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
if 'records_weekdays' not in st.session_state:
    st.session_state.records_weekdays = []

def generate_records():
    EZvr_value = EZvr_values[EZvr_selected]
    EZkeyid_value = Ez_Tag[EZtag_selected]
    EZkeyname = EZvr_selected

    for date, plates in plates_per_day.items():
        day_ft = dayy(date.strftime('%A'))
        month_ft = monthm(date)

        for val in plates:
            for category in selected_categories:
                VcatID = vehicle_categories[category]
                record = addreg(EZname, EZid, category, VcatID, EZkeyname, EZvr_value, EZtag_selected, EZkeyid_value, val, times, day_ft, month_ft, date.strftime("%Y%m%d"))
                st.session_state.records_weekdays.append(record)

if st.button("Generate DataFrame"):
    generate_records()
    st.success("Records generated successfully.")

# Export DataFrame to CSV
df_weekdays = pd.DataFrame(st.session_state.records_weekdays)
st.write('### DataFrame:')
st.dataframe(df_weekdays)

file_name = f"EZ_{EZname}_{EZid}_Metadata_{datetime.now().year}.csv"
csv = df_weekdays.to_csv(index=False, quoting=1).encode('utf-8')

st.download_button("Download CSV", csv, file_name, "text/csv")
