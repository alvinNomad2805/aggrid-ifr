import os
import streamlit as st
import datetime
from data import LoadData
import calendar
import pandas as pd
import polars as pl
import numpy as np
from reports.ifr.functions.get_ytd import get_ytd

def applyfilter(companies, brands):
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
    with h2:
        list_month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        select_month = h2.selectbox("Month", list_month, index=default_month_index, key="month_start")
        month_dict = dict((v, k) for k, v in enumerate(calendar.month_name))
        selected_month = month_dict[select_month]   
        selected_month = "0"+ str(selected_month) if len(str(selected_month)) < 2 else str(selected_month)
    with h3:
        brands.insert(0, "ALL")
        select_brand = h3.selectbox("Brand", brands)
    with h4:
        pass

   # Console Filter
    data_company_console = pl.DataFrame(LoadData.load_data('/consolidation-company'))
    data_company_console = data_company_console.filter(pl.col('use_dms') == 'Yes')
    if companies != []:
        data_company_console = data_company_console.filter(pl.col('company_name').is_in(companies))
    list_company = data_company_console.filter(pl.col('level') == 1).get_column('company_name').unique().sort().to_list()

    h1,h2,h3,h4 = st.columns(4)
    with h1:
        level1 = data_company_console.filter((pl.col('level') == 1) & (pl.col('console_combine_name') != 'NA')).get_column('console_combine_name').unique().sort().to_list()
        level1.insert(0, "Select Level 1")
        level1_with_na = data_company_console.filter(pl.col('level') == 1).get_column('console_combine_name').unique().sort().to_list()
        level1_with_na.insert(0, "Select Level 1")
        select_concom_level1 = h1.selectbox('Company Filter - Level 1', level1, key='level1')
        if select_concom_level1 != 'Select Level 1':
            list_company = data_company_console.filter(pl.col('console_combine_name') == select_concom_level1).get_column('company_name').unique().sort().to_list()
        else:
            pass

    with h2:
        if select_concom_level1 != 'Select Level 1':
            parent_code = data_company_console.filter(pl.col('console_combine_name') == select_concom_level1).get_column('console_combine_code').unique()[0]
        else:
            parent_code = 0
        level2 = data_company_console.filter((pl.col('level') == 2) & (pl.col('parent_code') == parent_code)).get_column('console_combine_name').unique().sort().to_list()
        level2.insert(0, "Select Level 2")
        select_concom_level2 = h2.selectbox('Company Filter - Level 2', level2, key='level2')
        if select_concom_level2 != 'Select Level 2':
            list_company = data_company_console.filter(pl.col('console_combine_name') == select_concom_level2).get_column('company_name').unique().sort().to_list()
        else:
            pass
    
    with h3:
        if select_concom_level2 != 'Select Level 2':
            parent_code = data_company_console.filter(pl.col('console_combine_name') == select_concom_level2).get_column('console_combine_code').unique()[0]
        else:
            parent_code = 0
        level3 = data_company_console.filter((pl.col('level') == 3) & (pl.col('parent_code') == parent_code)).get_column('console_combine_name').unique().sort().to_list()
        level3.insert(0, "Select Level 3")
        select_concom_level3 = h3.selectbox('Company Filter - Level 3', level3, key='level3')
        if select_concom_level3 != 'Select Level 3':
            list_company = data_company_console.filter(pl.col('console_combine_name') == select_concom_level3).select('company_name').get_column('company_name').unique().sort().to_list()
        else:
            pass
    
    with h4:
        select_company = h4.selectbox('Company', list_company, key='company')
    
    return selected_month, select_year, select_brand, select_company