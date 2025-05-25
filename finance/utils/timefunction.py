import streamlit as st
import datetime
import pytz

def last_day_of_month(year, month):
        if month == 2:
            if is_leap_year(year):
                return 29
            else:
                return 28
        elif month in (4, 6, 9, 11):
            return 30
        else:
            return 31

def is_leap_year(year):
    if year % 4 == 0:
        if year % 100 == 0:
            if year % 400 == 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False
    
def header_logo_period():
    h1,h2,h3,h4,h5,h6 = st.columns((2,1,1,1,1,1))
    today = datetime.datetime.now()
    with h1:
        pass
    with h2:
        list_year = ["Select Year", today.year,today.year-1,today.year-2]
        select_year = h2.selectbox("Year",list_year)
    with h3:
        list_month = ["Select Month", "January","February","March","April","May","June","July","August","September","October","November", "December"]
        select_month = h3.selectbox("Month",list_month, key="month_leads")
    with h4:
        list_quarter = ["Select Quarter","Q1","Q2","Q3","Q4"]
        select_quarter = h4.selectbox("Quarter",list_quarter,key='quarter_leads')
    with h5:
        list_week = ["Select Week", "1st","2nd","3rd","4th"]
        select_week = h5.selectbox("Week",list_week,key='week_leads')
    with h6:
        if select_year != 'Select Year':
            if select_month != 'Select Month':
                if select_week != 'Select Week':
                    if select_week == '1st':
                        date = [1,7]
                    elif select_week == '2nd':
                        date = [8,14]
                    elif select_week == '3rd':
                        date = [15,21]
                    else:
                        date = [22, last_day_of_month(int(select_year), list_month.index(select_month))]
                    start_date = datetime.date(int(select_year), list_month.index(select_month), date[0])
                    end_date = datetime.date(int(select_year), list_month.index(select_month), date[1])
                else:
                    start_date = datetime.date(int(select_year), list_month.index(select_month), 1)
                    end_date = datetime.date(int(select_year), list_month.index(select_month), last_day_of_month(int(select_year), list_month.index(select_month)))
                
            else:
                start_date = datetime.date(int(select_year), 1, 1)
                end_date = datetime.date(int(select_year), 12, last_day_of_month(select_year, 12))
                
            if select_quarter != 'Select Quarter':
                if select_quarter == 'Q1':
                    month = [1,3]
                elif select_quarter == 'Q2':
                    month = [4,6]
                elif select_quarter == 'Q3':
                    month = [7,9]
                else:
                    month = [10,12]
                start_date = datetime.date(int(select_year), month[0], 1)
                end_date = datetime.date(int(select_year), month[1], last_day_of_month(select_year, month[1]))
        else:
            start_date = datetime.date(today.year, today.month, 1)
            end_date = datetime.date(today.year, today.month, today.day)
        
        jan_1_min_year = datetime.date(today.year-3, 1, 1)
        dec_31_max_year = datetime.date(today.year, 12, 31)
        d = st.date_input("Select Date",
                          (start_date, end_date),
                          jan_1_min_year,dec_31_max_year,format="DD/MM/YYYY",key='date_leads')
        list_d = list(d)
        if len(list_d) == 1:
            list_d.append(list_d[0])

        return list_d, today, select_month, select_year
    
def get_current_date_time():
    return datetime.datetime.now(pytz.timezone('Asia/Jakarta')).strftime("%d/%m/%Y %H:%M")

def month_to_proceed(selected_month):
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    index_selected = month_list.index(selected_month)
    month_to_proceed = month_list[:index_selected+1]
    return month_to_proceed
