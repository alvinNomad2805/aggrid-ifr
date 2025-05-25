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
        selected_month = "0"+ str(selected_month) if len(str(selected_month)) < 2 else str(selected_month)
    with h3:
        pass
    with h4:
        pass
    raw_data = pd.DataFrame(LoadData.load_data(f"/araging?year={str(select_year)}&month={selected_month}"))
    applied_filter.append(select_month)

    if raw_data.empty:
            empty_raw_data = pd.DataFrame(
                columns = [
                    'CompanyConsole',
                    'ConsolidationName',
                    'CompanyCode',
                    'CompanyName',
                    'CompanyAbbreviation',
                    'PeriodYear',
                    'PeriodMonth',
                    'ArType',
                    'ArTypeDescription',
                    'ArGroup',
                    'ArGroupDescription',
                    'ProfitCenter',
                    'ProfitCenterDescription',
                    'VehicleBrand',
                    'Leasing',
                    'LeasingName',
                    'CustType',
                    'CustTypeDescription',
                    'CustCode',
                    'CustomerName',
                    'CustGroupCode',
                    'CustGroupDescription',
                    'InvDate',
                    'InvDocNo',
                    'InvDueDate',
                    'BeginAmount',
                    'SalesAmount',
                    'SalesCorrectionAmount',
                    'PayAmount',
                    'PayReturnAmount',
                    'PayCorrectionAmount',
                    'NotOverDueAmount',
                    'Days0to7',
                    'Days8to14',
                    'Days15to21',
                    'Days22to30',
                    'Days31to60',
                    'Days61to90',
                    'Days90',
                    'AsOfDatePayAmount',
                    'Remark',
                    'Status',
                    'AgingDay',
                    'InvOriAmount',
                    'TaxInvDocNo',
                    'Tnkb',
                    'TrxTypeDescription',
                ]
            )
            raw_data = empty_raw_data

    # Console Filter
    data_company_console = pd.DataFrame(LoadData.load_data('/consolidation-company'))
    data_company_console = data_company_console[data_company_console['use_dms'] == 'Yes']
    if companies != []:
        data_company_console = data_company_console[data_company_console['company_name'].isin(companies)]

    h1,h2,h3,h4 = st.columns(4)
    with h1:
        level1 = data_company_console[(data_company_console['level'] == 1) &
                                      (data_company_console['console_combine_name'] != 'NA')]['console_combine_name'].sort_values().unique().tolist()
        # level1.insert(0, "Select Level 1")
        select_concom_level1 = h1.selectbox('Company Filter - Level 1', level1, key='level1')
        # if select_concom_level1 != 'Select Level 1':
        list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level1]['company_name'].unique().tolist()
        raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
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
            list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level2]['company_name'].unique().tolist()
            raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
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
            list_company = data_company_console[data_company_console['console_combine_name'] == select_concom_level3]['company_name'].unique().tolist()
            raw_data = raw_data[raw_data['CompanyName'].isin(list_company)]
        else:
            pass
    
    with h4:
        if companies != []:
            raw_data = raw_data[raw_data['CompanyName'].isin(companies)]
            raw_data = raw_data[raw_data['VehicleBrand'].isin(brands)]

        company = raw_data['CompanyName'].unique().tolist()
        company.insert(0, "Select Company")
        select_company = h4.selectbox('Company', company, key='company')
        if select_company != 'Select Company':
            raw_data = raw_data[raw_data['CompanyName'] == select_company]
        else:
            pass
    
    h5, h6, h7, h8 = st.columns(4)
    with h5:
        list_argroup = raw_data['ArGroupDescription'].unique().tolist()
        list_argroup.insert(0, "Select AR Group")
        select_argroup = h5.selectbox("AR Group", list_argroup, key='argroup')
        if select_argroup != 'Select AR Group':
            raw_data = raw_data[raw_data['ArGroupDescription'] == select_argroup]
        else:
            pass
    with h6:
        list_profitcenter = raw_data['ProfitCenterDescription'].unique().tolist()
        list_profitcenter.insert(0, "Select Profit Center")
        select_profitcenter = h6.selectbox("Profit Center", list_profitcenter, key='profitcenter')
        if select_profitcenter != 'Select Profit Center':
            raw_data = raw_data[raw_data['ProfitCenterDescription'] == select_profitcenter]
        else:
            pass
    with h7:
        list_brand = raw_data['VehicleBrand'].unique().tolist()
        list_brand.insert(0, "Select Brand")
        select_brand = h7.selectbox("Brand", list_brand, key='brand')
        if select_brand != 'Select Brand':
            raw_data = raw_data[raw_data['VehicleBrand'] == select_brand]
        else:
            pass
    with h8:
        list_custtype = raw_data['CustTypeDescription'].unique().tolist()
        list_custtype.insert(0, "Select Customer Type")
        select_custtype = h8.selectbox("Customer Type", list_custtype, key='custtype')
        if select_custtype != 'Select Customer Type':
            raw_data = raw_data[raw_data['CustTypeDescription'] == select_custtype]
        else:
            pass

    return raw_data