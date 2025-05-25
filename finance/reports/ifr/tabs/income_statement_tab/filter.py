import os
from utils.caching import parquet_by_monthly
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
        # default_month_index = today.month - 1 # current month
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
        selected_month = "0"+ str(selected_month) if len(str(selected_month-1)) < 2 else selected_month-1
    with h3:
        select_brand = h3.selectbox("Brand", brands)
    with h4:
        pass
    
    #GET DATA
    empty_data_income_statement = pd.DataFrame(
            columns=['CompanyCode', 'CompanyName', 'CompanyAbbreviation', 'PeriodYear',
                    'PeriodMonth', 'AccountNumber', 'AccountDescription', 'AccountType',
                    'Group1', 'BeginAmount', 'DebitAmount', 'CreditAmount', 'EndAmount',
                    'Brand', 'ProfitCenter', 'ArGroup']
    )
    empty_data_ar_aging_overdue = pd.DataFrame(
        columns=['CompanyCode', 'CompanyName', 'CompanyAbbreviation', 'ProfitCenterCode',
       'ProfitCenter', 'Brand', 'PeriodYear', 'PeriodMonth',
       'Aging2BaseAmount', 'Aging3BaseAmount', 'Aging4BaseAmount']
    )
    raw_data_income_statement = parquet_by_monthly(select_year, selected_month, 
                                                    f"reports/ifr/parquet/ifr-income-statement_{select_year}_{selected_month}_{select_brand}.parquet",
                                                    f"/ifr-income-statement?period_year={select_year}&period_month={selected_month}&brand={select_brand}")
    if raw_data_income_statement.empty:
        raw_data_income_statement = empty_data_income_statement

    raw_data_income_statement_last_year = parquet_by_monthly(select_year-1, selected_month, 
                                                    f"reports/ifr/parquet/ifr-income-statement_{select_year-1}_{selected_month}_{select_brand}.parquet",
                                                    f"/ifr-income-statement?period_year={select_year-1}&period_month={selected_month}&brand={select_brand}")
    if raw_data_income_statement_last_year.empty:
        raw_data_income_statement_last_year = empty_data_income_statement
    
    raw_data_ar_aging_overdue = parquet_by_monthly(select_year, selected_month, 
                                                    f"reports/ifr/parquet/ifr-ar-aging-overdue_{select_year}_{selected_month}_{select_brand}.parquet",
                                                    f"/ifr-ar-aging-overdue?period_year={select_year}&period_month={selected_month}&brand={select_brand}")
    if raw_data_ar_aging_overdue.empty:
        raw_data_ar_aging_overdue = empty_data_ar_aging_overdue

    raw_data_ar_aging_overdue_last_year = parquet_by_monthly(select_year-1, selected_month, 
                                                    f"reports/ifr/parquet/ifr-ar-aging-overdue_{select_year-1}_{selected_month}_{select_brand}.parquet",
                                                    f"/ifr-ar-aging-overdue?period_year={select_year-1}&period_month={selected_month}&brand={select_brand}")
    if raw_data_ar_aging_overdue_last_year.empty:
        raw_data_ar_aging_overdue_last_year = empty_data_ar_aging_overdue
    
    #End Get Data
    companies = raw_data_income_statement['CompanyName'].unique().tolist()
    applied_filter.append(select_month)

    # Console Filter
    filename = "reports/ifr/parquet/consolidation-company.parquet"
    if os.path.exists(filename):
        data_company_console = pd.read_parquet(filename)
    else:
        data_company_console = pd.DataFrame(LoadData.load_data('/consolidation-company'))
        data_company_console.to_parquet(filename)
    data_company_console = data_company_console[data_company_console['use_dms'] == 'Yes']
    if companies != []:
        data_company_console = data_company_console[data_company_console['company_name'].isin(companies)]
    level = 0
    selected = 0

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
            raw_data_income_statement = raw_data_income_statement[raw_data_income_statement['CompanyName'].isin(list_company)]
            raw_data_income_statement_last_year = raw_data_income_statement_last_year[raw_data_income_statement_last_year['CompanyName'].isin(list_company)]
            raw_data_ar_aging_overdue = raw_data_ar_aging_overdue[raw_data_ar_aging_overdue['CompanyName'].isin(list_company)]
            raw_data_ar_aging_overdue_last_year = raw_data_ar_aging_overdue_last_year[raw_data_ar_aging_overdue_last_year['CompanyName'].isin(list_company)]
        else:
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
            raw_data_income_statement = raw_data_income_statement[raw_data_income_statement['CompanyName'].isin(list_company)]
            raw_data_income_statement_last_year = raw_data_income_statement_last_year[raw_data_income_statement_last_year['CompanyName'].isin(list_company)]
            raw_data_ar_aging_overdue = raw_data_ar_aging_overdue[raw_data_ar_aging_overdue['CompanyName'].isin(list_company)]
            raw_data_ar_aging_overdue_last_year = raw_data_ar_aging_overdue_last_year[raw_data_ar_aging_overdue_last_year['CompanyName'].isin(list_company)]
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
            raw_data_income_statement = raw_data_income_statement[raw_data_income_statement['CompanyName'].isin(list_company)]
            raw_data_income_statement_last_year = raw_data_income_statement_last_year[raw_data_income_statement_last_year['CompanyName'].isin(list_company)]
            raw_data_ar_aging_overdue = raw_data_ar_aging_overdue[raw_data_ar_aging_overdue['CompanyName'].isin(list_company)]
            raw_data_ar_aging_overdue_last_year = raw_data_ar_aging_overdue_last_year[raw_data_ar_aging_overdue_last_year['CompanyName'].isin(list_company)]
        else:
            pass
    
    with h4:
        if companies != []:
            raw_data_income_statement = raw_data_income_statement[raw_data_income_statement['CompanyName'].isin(companies)]
            raw_data_income_statement = raw_data_income_statement[raw_data_income_statement['Brand'].isin(brands)]
        
        company = raw_data_income_statement['CompanyName'].sort_values().unique().tolist()
        select_company = h4.selectbox('Company', company, key='company')
        if select_company != 'Select Company':
            raw_data_income_statement = raw_data_income_statement[raw_data_income_statement['CompanyName'] == select_company]
            raw_data_income_statement_last_year = raw_data_income_statement_last_year[raw_data_income_statement_last_year['CompanyName'] == select_company]
            raw_data_ar_aging_overdue = raw_data_ar_aging_overdue[raw_data_ar_aging_overdue['CompanyName'] == select_company]
            raw_data_ar_aging_overdue_last_year = raw_data_ar_aging_overdue_last_year[raw_data_ar_aging_overdue_last_year['CompanyName'] == select_company]
        else:
            pass
    #for main.py
    data_comcon = {
        0: level1,
        1: level2,
        2: level3,
        3: company
    }
    return raw_data_income_statement, raw_data_income_statement_last_year, raw_data_ar_aging_overdue, raw_data_ar_aging_overdue_last_year, selected_month