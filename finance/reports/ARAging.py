import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import datetime
from data import LoadData
import calendar
from utils.filter import financial_format

def rr_aging(userlogin, companies):
    # try:
        st.markdown("# Aging Report")
        
        h1,h2,h3,h4 = st.columns(4)
        today = datetime.datetime.now()
        if today.month - 1 == 0:
            default_month_index = 11
            default_year = today.year - 1
        else:
            default_month_index = today.month - 2
            default_year = today.year

        with h1:
            list_year = [today.year, today.year - 1]
            select_year = h1.selectbox("Year", list_year, index=list_year.index(default_year), key="year")
        with h2:
            list_month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            select_month = h2.selectbox("Month Start", list_month, index=default_month_index, key="month_start")

            month_dict = dict((v, k) for k, v in enumerate(calendar.month_name))
            selected_month = month_dict[select_month]
            selected_month = "0"+ str(selected_month) if len(str(selected_month)) < 2 else selected_month
            raw_data = pd.DataFrame(LoadData.load_data(f"/araging?year={select_year}&month={selected_month}"))
        with h3:
            console = ["Select Consolidation"]
            list_consolidation = raw_data['ConsolidationName'].unique().tolist()
            for csl in list_consolidation:
                console.append(csl)
            select_company_console = h3.selectbox("Consolidation", console, key='consolidation_company')
            raw_data = raw_data[raw_data["ConsolidationName"] == (select_company_console)] if select_company_console != 'Select Consolidation' else raw_data
        with h4:
            company = ["Select Company"]
            list_company = raw_data['CompanyName'].unique().tolist()
            for comp in list_company:
                company.append(comp)
            select_company_console = h4.selectbox("Company", company, key='company')
            raw_data = raw_data[raw_data["CompanyName"] == select_company_console] if select_company_console != 'Select Company' else raw_data

        h1,h2,h3,h4 = st.columns(4)
        with h1:
            argroup = ["Select AR Group"]
            list_argroup = raw_data['ArGroupDescription'].unique().tolist()
            for ar in list_argroup:
                argroup.append(ar)
            select_argroup = h1.selectbox("AR Group", argroup, key='argroup')
            raw_data = raw_data[raw_data['ArGroupDescription'] == select_argroup] if select_argroup != 'Select AR Group' else raw_data
        with h2:
            profitcenter = ["Select Profit Center"]
            list_profitcenter = raw_data['ProfitCenterDescription'].unique().tolist()
            for pc in list_profitcenter:
                profitcenter.append(pc)
            select_profitcenter = h2.selectbox("Profit Center", profitcenter, key='profitcenter')
            raw_data = raw_data[raw_data['ProfitCenterDescription'] == select_profitcenter] if select_profitcenter != 'Select Profit Center' else raw_data
        with h3:
            brand = ["Select Brand"]
            list_brand = raw_data['VehicleBrand'].unique().tolist()
            for br in list_brand:
                brand.append(br)
            select_brand = h3.selectbox("Brand", brand, key='brand')
            raw_data = raw_data[raw_data['VehicleBrand'] == select_brand] if select_brand != 'Select Brand' else raw_data
        with h4:
            custtype = ["Select Customer Type"]
            list_custtype = raw_data['CustTypeDescription'].unique().tolist()
            for ct in list_custtype:
                custtype.append(ct)
            select_custtype = h4.selectbox("Customer Type", custtype, key='custtype')
            raw_data = raw_data[raw_data['CustTypeDescription'] == select_custtype] if select_custtype != 'Select Customer Type' else raw_data
        st.divider()

        raw_data_over_due_aging = raw_data.groupby(['CompanyConsole',
                                            'ConsolidationName',
                                            'CompanyCode',
                                            'CompanyName',
                                            'CompanyAbbreviation']).agg({'BeginAmount':'sum',
                                                                         'SalesAmount':'sum',
                                                                         'SalesCorrectionAmount':'sum',
                                                                         'NotOverDueAmount':'sum',
                                                                         'PayAmount':'sum',
                                                                         'PayReturnAmount':'sum',
                                                                         'PayCorrectionAmount':'sum',
                                                                         'Days0to7':'sum',
                                                                        'Days8to14':'sum',
                                                                        'Days15to21':'sum',
                                                                        'Days22to30':'sum',
                                                                        'Days31to60':'sum',
                                                                        'Days61to90':'sum',
                                                                        'Days90':'sum'})

        #Chart 1st Row
        c11,c12 = st.columns([1,2])
        with c11:
            sumofendingamount = int((raw_data_over_due_aging['BeginAmount'].sum()+raw_data_over_due_aging['SalesAmount'].sum())-
                                    (raw_data_over_due_aging['SalesCorrectionAmount'].sum()+raw_data_over_due_aging['PayAmount'].sum()+
                                    raw_data_over_due_aging['PayReturnAmount'].sum()+raw_data_over_due_aging['PayCorrectionAmount'].sum()))
            sumofnotoverdue = int(raw_data_over_due_aging['NotOverDueAmount'].sum())
            st.metric('Sum of Ending Amount',value=financial_format(sumofendingamount))
            st.metric('Sum of Not Over Due',financial_format(sumofnotoverdue))
            style_metric_cards()
        with c12:
            pass

    # except:
    #     st.error("Data is empty, please check database !!!")