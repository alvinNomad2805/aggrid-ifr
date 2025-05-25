import streamlit as st
import datetime
from data import LoadData
import calendar
import pandas as pd
import numpy as np

def applyfilter(companies, brands):
    applied_filter = []
    h1,h2,h3,h4= st.columns(4)
    today = datetime.datetime.now()
    if today.month - 1 == 0:
        default_month_index = 11
        default_year = today.year - 1
    else:
        default_month_index = today.month - 2 # previous month
        default_year = today.year

    with h1:
        list_year = [today.year, today.year - 1]
        select_year = h1.selectbox("Year", list_year, index=list_year.index(default_year), key="year")
        applied_filter.append(select_year)
    with h2:
        list_month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        select_month = h2.selectbox("Month", list_month, index=default_month_index, key="month_start")
        month_dict = dict((v, k) for k, v in enumerate(calendar.month_name))
        selected_month = month_dict[select_month]   
        selected_month = "0"+ str(selected_month) if len(str(selected_month)) < 2 else selected_month
    with h3:
        pass
    with h4:
        pass
    #balance sheet raw data
    raw_data = pd.DataFrame(LoadData.load_data(f"/balance-sheet?year={str(select_year)}&month={selected_month}"))
    #profit loss raw data
    pl_raw_data = pd.DataFrame(LoadData.load_data(f"/profit-loss-view?year={str(select_year)}&month={selected_month}"))
    applied_filter.append(select_month)

    # Console Filter
    data_company_console = pd.DataFrame(LoadData.load_data('/consolidation-company'))
    data_company_console = data_company_console[data_company_console['use_dms'] == 'Yes']
    if companies != []:
        data_company_console = data_company_console[data_company_console['company_name'].isin(companies)]
    level = 0
    selected = 0
    
    if raw_data.empty:
        empty_data = pd.DataFrame(
            columns=['CompanyCode','CompanyName','Brand','CompanyAbbreviation','PeriodYear','PeriodMonth','AccountNumber','AccountDescription',
                    'BankAccount','BankName','BankAccountNo','BankAccountName','AccountType','Group1','BeginAmount','DebitAmount','CreditAmount',
                    'EndAmount','ProfitCenter','ArGroup','RegionCode']
        )
        raw_data = empty_data

    if data_company_console.empty:
        empty_data_company_console = pd.DataFrame(
            columns=['id','console_combine_code','console_combine_name','parent_code','level','company_code','company_name','use_dms']
        )
        data_company_console = empty_data_company_console

    if pl_raw_data.empty:
        empty_data_pl = pd.DataFrame(
            columns=['CompanyCode','CompanyName','CompanyAbbreviation','PeriodYear','PeriodMonth','AccountNumber','AccountDescription','AccountType',
                    'Group1','Brand','ProfitCenter','ArGroup','RegionCode','MutationAmount','EndAmount']
        )
        pl_raw_data = empty_data_pl

    h1,h2,h3,h4 = st.columns(4)
    with h1:
        level1 = data_company_console[(data_company_console['level'] == 1) &
                                      (data_company_console['console_combine_name'] != 'NA')]['console_combine_name'].sort_values().unique().tolist()
        level1.insert(0, "Select Level 1")
        level1_with_na = data_company_console[(data_company_console['level'] == 1)]['console_combine_name'].sort_values().unique().tolist()
        level1_with_na.insert(0, "Select Level 1")
        select_concom_level1 = h1.selectbox('Console Combine - Level 1', level1, key='level1')
        if select_concom_level1 != 'Select Level 1':
            level = 1
            selected = 0
            list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level1]['company_name'].unique().tolist()
            raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
            pl_raw_data = pl_raw_data[pl_raw_data['CompanyName'].isin(list_company)]
            default_companies = []
        else:
            default_companies = level1
            pass

    with h2:
        if select_concom_level1 != 'Select Level 1':
            parent_code = data_company_console[data_company_console['console_combine_name'] == select_concom_level1]['console_combine_code'].unique()[0]
        else:
            parent_code = 0
        level2 = data_company_console[(data_company_console['level'] == 2) &
                                      (data_company_console['parent_code'] == parent_code)]['console_combine_name'].sort_values().unique().tolist()
        level2.insert(0, "Select Level 2")
        select_concom_level2 = h2.selectbox('Console Combine - Level 2', level2, key='level2')
        if select_concom_level2 != 'Select Level 2':
            level = 2
            selected = parent_code
            list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level2]['company_name'].unique().tolist()
            raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
            pl_raw_data = pl_raw_data[pl_raw_data['CompanyName'].isin(list_company)]
        else:
            pass
    
    with h3:
        if select_concom_level2 != 'Select Level 2':
            parent_code = data_company_console[(data_company_console['console_combine_name'] == select_concom_level2)]['console_combine_code'].unique()[0]
        else:
            parent_code = 0
        level3 = data_company_console[(data_company_console['level'] == 3) &
                                      (data_company_console['parent_code'] == parent_code)]['console_combine_name'].sort_values().unique().tolist()
        level3.insert(0, "Select Level 3")
        select_concom_level3 = h3.selectbox('Combine - Level 3', level3, key='level3')
        if select_concom_level3 != 'Select Level 3':
            level = 3
            selected = parent_code
            list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level3]['company_name'].unique().tolist()
            raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
            pl_raw_data = pl_raw_data[pl_raw_data['CompanyName'].isin(list_company)]
        else:
            pass
    with h4:
        if companies != []:
            raw_data = raw_data[raw_data['CompanyName'].isin(companies)]
            raw_data = raw_data[raw_data['Brand'].isin(brands) | (raw_data['Brand']=='')]
            pl_raw_data = pl_raw_data[pl_raw_data['CompanyName'].isin(companies)]
            pl_raw_data = pl_raw_data[pl_raw_data['Brand'].isin(brands)]

        company = raw_data['CompanyName'].unique().tolist()
        company.insert(0, "Select Company")
        select_company = h4.selectbox('Company', company, key='company')
        if select_company != 'Select Company':
            raw_data = raw_data[raw_data['CompanyName'] == select_company]
            pl_raw_data = pl_raw_data[pl_raw_data['CompanyName'] == select_company]
        else:
            pass
    #for main.py
    data_comcon = {
        0: level1,
        1: level2,
        2: level3,
        3: company
    }
    return raw_data, level, data_comcon, data_company_console, selected, selected_month, default_companies, pl_raw_data