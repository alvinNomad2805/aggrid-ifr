import streamlit as st
import datetime
from data import LoadData
import calendar, time, os
import pandas as pd
import numpy as np
from reports.profitloss.functions import preprocessing

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
        selected_month_num = month_dict[select_month]   
        selected_month = "0"+ str(selected_month_num) if len(str(selected_month_num)) < 2 else str(selected_month_num)
    with h3:
        pass
    with h4:
        pass

    raw_data = pd.DataFrame(LoadData.load_data(f"/profit-loss-view?year={str(select_year)}&month={selected_month}"))
    all_year = LoadData.getallyear(select_year, selected_month_num, selected_month)
    if raw_data.empty:
        empty_data = pd.DataFrame(
            columns=['CompanyCode', 'CompanyName', 'CompanyAbbreviation', 'PeriodYear','PeriodMonth', 'AccountNumber', 'AccountDescription', 'AccountType',
                    'Group1', 'Brand', 'ProfitCenter', 'ArGroup', 'RegionCode','MutationAmount', 'EndAmount']
        )
        raw_data = empty_data

    if all_year.empty:
        empty_data_all_year = pd.DataFrame(
            columns=['CompanyCode', 'CompanyName', 'CompanyAbbreviation', 'PeriodYear','PeriodMonth', 'AccountNumber', 'AccountDescription', 'AccountType',
                     'Group1', 'Brand', 'ProfitCenter', 'ArGroup', 'RegionCode','MutationAmount', 'EndAmount']
        )
        all_year = empty_data_all_year
    
    #flask data
    current_dir = os.getcwd()
    # all_year = pd.read_csv(current_dir + "\\bigload\\profit_loss.tsv", sep='\t')
    #-----
    all_year['PeriodYear'] = all_year['PeriodYear'].astype(str)
    all_year['PeriodMonth'] = all_year['PeriodMonth'].astype(str).str.zfill(2)
    all_year['AccountNumber'] = all_year['AccountNumber'].astype(str)
    #-----
    all_year["PeriodMonth"] = all_year["PeriodMonth"].str.strip()
    all_year["PeriodMonth"] = all_year["PeriodMonth"].replace(["13"], "12")
    # raw_data = all_year.copy()
    raw_data = raw_data[raw_data['PeriodMonth'] == selected_month]
    raw_data = raw_data[raw_data['PeriodYear'] == str(select_year)]
    if not raw_data.empty:
        all_year = pd.concat([all_year, raw_data], ignore_index=True)
    #end flask data

    # raw_data, all_year = LoadData.router_cache_data(select_year, selected_month_num, selected_month)
    applied_filter.append(select_month)

    # Console Filter
    data_company_console = pd.DataFrame(LoadData.load_data('/consolidation-company'))
    if data_company_console.empty:
        empty_data_company_console = pd.DataFrame(
            columns=['id','console_combine_code','console_combine_name','parent_code','level','company_code','company_name','use_dms']
        )
        data_company_console = empty_data_company_console
        
    data_company_console = data_company_console[data_company_console['use_dms'] == 'Yes']
    if companies != []:
        data_company_console = data_company_console[data_company_console['company_name'].isin(companies)]
    level = 0
    selected = 0

    #preprocessing
    raw_data = preprocessing.preprocessing(raw_data, data_company_console)
    all_year = preprocessing.preprocessing(all_year, data_company_console)
    
    h1,h2,h3,h4 = st.columns(4)
    with h1:
        level1 = data_company_console[(data_company_console['level'] == 1) &
                                      (data_company_console['console_combine_name'] != 'NA')]['console_combine_name'].sort_values().unique().tolist()
        # level1.insert(0, "Select Level 1")
        level1_with_na = data_company_console[(data_company_console['level'] == 1)]['console_combine_name'].sort_values().unique().tolist()
        # level1_with_na.insert(0, "Select Level 1")
        select_concom_level1 = h1.selectbox('Company Filter - Level 1', level1, key='level1')
        # if select_concom_level1 != 'Select Level 1':
        level = 1
        selected = 0
        list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level1]['company_name'].unique().tolist()
        raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
        all_year = all_year[all_year['CompanyName'].isin(list_company)]
        # else:
        #     pass

    with h2:
        if select_concom_level1 != 'Select Level 1':
            parent_code = data_company_console[data_company_console['console_combine_name'] == select_concom_level1]['console_combine_code'].unique()[0]
        else:
            parent_code = 0
        level2 = data_company_console[(data_company_console['level'] == 2) &
                                      (data_company_console['parent_code'] == parent_code)]['console_combine_name'].sort_values().unique().tolist()
        level2.insert(0, "Select Level 2")
        select_concom_level2 = h2.selectbox('Company Filter - Level 2', level2, key='level2')
        if select_concom_level2 != 'Select Level 2':
            level = 2
            selected = parent_code
            list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level2]['company_name'].unique().tolist()
            raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
            all_year = all_year[all_year['CompanyName'].isin(list_company)]
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
        select_concom_level3 = h3.selectbox('Company Filter - Level 3', level3, key='level3')
        if select_concom_level3 != 'Select Level 3':
            level = 3
            selected = parent_code
            list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level3]['company_name'].unique().tolist()
            raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
            all_year = all_year[all_year['CompanyName'].isin(list_company)]
        else:
            pass
    
    with h4:
        if companies != []:
            raw_data = raw_data[raw_data['CompanyName'].isin(companies)]
            raw_data = raw_data[raw_data['Brand'].isin(brands)]
            all_year = all_year[all_year['CompanyName'].isin(companies)]
            all_year = all_year[all_year['Brand'].isin(brands)]

        company = raw_data['CompanyName'].unique().tolist()
        company.insert(0, "Select Company")
        select_company = h4.selectbox('Company', company, key='company')
        if select_company != 'Select Company':
            raw_data = raw_data[raw_data['CompanyName'] == select_company]
            all_year = all_year[all_year['CompanyName'] == select_company]
        else:
            pass
    
    h5, h6, h7, h8 = st.columns(4)
    with h5:
        list_profitcenter = raw_data['ProfitCenter'].sort_values().unique().tolist()
        list_profitcenter.insert(0, "Select Profit Center")
        select_profitcenter = h5.selectbox("Profit Center", list_profitcenter, key='profitcenter')
        if select_profitcenter != 'Select Profit Center':
            raw_data = raw_data[raw_data['ProfitCenter'] == select_profitcenter]
            all_year = all_year[all_year['ProfitCenter'] == select_profitcenter]
        else:
            pass
    with h6:
        list_brand = raw_data['Brand'].sort_values().unique().tolist()
        list_brand.insert(0, "Select Brand")
        select_brand = h6.selectbox("Brand", list_brand, key='brand')
        if select_brand != 'Select Brand':
            raw_data = raw_data[raw_data['Brand'] == select_brand]
            all_year = all_year[all_year['Brand'] == select_brand]
        else:
            pass
    with h7:
        list_argroup = raw_data['ArGroup'].sort_values().unique().tolist()
        list_argroup.insert(0, "Select Group")
        select_argroup = h7.selectbox("Group", list_argroup, key='argroup')
        if select_argroup != "Select Group":
            raw_data = raw_data[raw_data['ArGroup'] == select_argroup]
            all_year = all_year[all_year['ArGroup'] == select_argroup]
        else:
            pass
    with h8:
        pass

    #for main.py
    data_comcon = {
        0: level1,
        1: level2,
        2: level3,
        3: company
    }
    return raw_data, all_year, level, data_comcon, data_company_console, selected, select_year, selected_month, selected_month_num, select_company