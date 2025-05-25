import streamlit as st
import requests
import pandas as pd
import extra_streamlit_components as stx
import datetime
import pytz

@st.cache_data(ttl=43200)
def load_data(pagetype):
    try:
        server  = "http://localhost:5000"
        read_data = requests.get(server+pagetype)
        print(f"hit-url: {server+pagetype}")
    except:
        server = "http://172.16.5.5:5000"
        read_data = requests.get(server+pagetype)
        print(f"hit-url: {server+pagetype}")
    return read_data.json()

@st.cache_data(ttl=31536000)
def load_data_old(pagetype):
    try:
        server  = "http://localhost:5000"
        read_data = requests.get(server+pagetype)
        print(f"hit-url: {server+pagetype}")
    except:
        server = "http://172.16.5.5:5000"
        read_data = requests.get(server+pagetype)
        print(f"hit-url: {server+pagetype}")
    return read_data.json()

def router_cache_data(this_year, selected_month_num, selected_month):
    today = datetime.datetime.now()
    if today.month == 1:
        actual_last_month = '12'
        actual_this_year = today.year - 1
        actual_last_year = today.year - 1
    else:
        actual_last_month = "0"+ str(today.month - 1) if len(str(today.month - 1)) < 2 else str(today.month - 1)
        actual_this_year = today.year
        actual_last_year = today.year - 1

    year_list = [this_year-1, this_year]
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
    list_df = []

    for year in year_list:
        if year == this_year:
            if str(selected_month_num) == '12':
                index = -1
            else:
                index = selected_month_num
        else:
            index = -1

        for month in month_list[:index]:
            if (month == actual_last_month or selected_month_num >= today.month-1) and year == actual_this_year:
                print("cache 12 hours")
                get_data = load_data(f"/profit-loss-view?year={str(year)}&month={month}")
                get_data = pd.DataFrame(get_data)
                list_df.append(get_data)
            else:
                print('cache 1 year')
                get_data = load_data_old(f"/profit-loss-view?year={str(year)}&month={month}")
                get_data = pd.DataFrame(get_data)
                list_df.append(get_data)

    results = pd.concat(list_df)
    results["PeriodMonth"] = results["PeriodMonth"].str.strip()
    results["PeriodMonth"] = results["PeriodMonth"].replace(["13"], "12")
    raw_data = results.copy()
    raw_data = raw_data[raw_data['PeriodMonth'] == selected_month]
    raw_data = raw_data[raw_data['PeriodYear'] == str(this_year)]
    return raw_data, results


def post_logging(module, page_change, brand_selector, userlogin, statusrole):
    try:
        url = "http://172.16.5.5:5000/logging"
        payload = {
            "module": module,
            "page_change": page_change,
            "brand": brand_selector,
            "username": userlogin,
            "role": statusrole,
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print("Logging failed :", response.status_code)
            return False, response.status_code
        return True, response.status_code
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return False, response.status_code

@st.cache_resource()
def CookieManager():
    return stx.CookieManager()

def load_data_users(pagetype):
    try:
        server  = "http://localhost:5000"
        read_data = requests.get(server+pagetype)
    except:
        server = "http://172.16.5.5:5000"
        read_data = requests.get(server+pagetype)

    return read_data.json()

@st.cache_data(ttl=43200)
def refresh_time(page_data):
    page_data = page_data
    last_refresh = str(datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d/%m/%Y %H:%M"))
    return last_refresh

# @st.cache_data(ttl=31536000) #this function will cache one year ttl
def getallyear(this_year, selected_month_num, selected_month):
    year_list = [str(int(this_year)-1), this_year]
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
    list_df = []

    for year in year_list:
        if year == this_year:
            if str(selected_month_num) == '12':
                index = -1
            else:
                index = selected_month_num - 1
        else:
            index = -1

        for month in month_list[:index]:
            if (selected_month == month and year == this_year):
                pass
            else:
                get_data = load_data_old(f"/profit-loss-view?year={str(year)}&month={month}")
                get_data = pd.DataFrame(get_data)
                list_df.append(get_data)

    results = pd.concat(list_df)
    results["PeriodMonth"] = results["PeriodMonth"].str.strip()
    results["PeriodMonth"] = results["PeriodMonth"].replace(["13"], "12")
    return results

@st.cache_data(ttl=43200)
def getallyearbalancesheet():
    today = datetime.datetime.now()
    year_list = [today.year-1, today.year]
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
    list_df = []

    for year in year_list:
        if year == today.year:
            if today.month == '12':
                index = -1
            else:
                index = today.month - 1
        else:
            index = -1

        for month in month_list[:index]:
            get_data = load_data(f"/profit-loss-view?year={str(year)}&month={month}")
            get_data = pd.DataFrame(get_data)
            list_df.append(get_data)

    results = pd.concat(list_df)
    results["PeriodMonth"] = results["PeriodMonth"].str.strip()
    results["PeriodMonth"] = results["PeriodMonth"].replace(["13"], "12")
    return results
