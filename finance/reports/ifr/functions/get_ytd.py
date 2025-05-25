import datetime
import pandas as pd
import streamlit as st
from data.LoadData import load_data

@st.cache_data(ttl=86400)
def get_ytd(selected_month, brand, endpoint, empty_data):
    today = datetime.datetime.now()
    year_list = [today.year-1, today.year]
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    index_selected = month_list.index(selected_month)
    month_to_proceed = month_list[:index_selected+1]
    list_df = []

    for year in year_list:
        for month in month_to_proceed:
            print(f"/{endpoint}?period_year={str(year)}&period_month={month}&brand={brand}")
            get_data = load_data(f"/{endpoint}?period_year={str(year)}&period_month={month}&brand={brand}")
            get_data = get_data['Data']
            get_data = pd.DataFrame(get_data)
            if get_data.empty:
                get_data = empty_data
            list_df.append(get_data)
    results = pd.concat(list_df)
    results["PeriodMonth"] = results["PeriodMonth"].str.strip()
    ytd = results[results['PeriodYear'] == today.year]
    last_ytd = results[results['PeriodYear'] == today.year-1]
    return ytd, last_ytd