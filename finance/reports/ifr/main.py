import streamlit as st
import polars as pl
import pandas as pd
from reports.ifr.functions import filter2
from reports.ifr.tabs.income_statement_tab.main_tab_income_statement import income_statement
from reports.ifr.tabs.unit_performance.main_tab_unit_performance import main_unit_performance
from reports.ifr.tabs.aftersales_performance_tab import main_tab_aftersales_performance
from reports.ifr.tabs.cash_flow_management_tab.main_cash_flow_management import main_tab_cash_flow_management
from reports.ifr.tabs.stock_management_tab import main_tab
from data import LoadData
from utils.timefunction import month_to_proceed


def internet_financial_reporting(userlogin, companies, brands):
    try:
        #Header
        st.markdown("# Indomobil Financial Report")

        #Applying general filter
        selected_month,selected_year, selected_brand, selected_company = filter2.applyfilter(companies, brands)
        #Show last refresh time of loaded data

        refresh_time = LoadData.refresh_time("ifr")
        st.sidebar.markdown(f'<p style="text-align:center;font-weight:bold;"> Last Refresh Time : <br> {refresh_time}</p>',unsafe_allow_html=True)

        # Load main APIs
        raw_data_income_statement = LoadData.load_data(f"/ifr-income-statement?period_year={selected_year}&period_month={selected_month}&company_name={selected_company}")
        raw_data_income_statement_last_year = LoadData.load_data(f"/ifr-income-statement?period_year={selected_year-1}&period_month={selected_month}&company_name={selected_company}")
        raw_data_income_budget = LoadData.load_data(f"/ifr-income-budget?period_year={selected_year}&period_month={selected_month}&company_name={selected_company}")
        raw_data_income_budget_last_year = LoadData.load_data(f"/ifr-income-budget?period_year={selected_year-1}&period_month={selected_month}&company_name={selected_company}")
        # Create Dataframe
        raw_data_income_statement = pl.DataFrame(raw_data_income_statement['Data'])
        raw_data_income_statement_last_year = pl.DataFrame(raw_data_income_statement_last_year['Data'])
        raw_data_income_budget = pl.DataFrame(raw_data_income_budget['Data'])
        raw_data_income_budget_last_year = pl.DataFrame(raw_data_income_budget_last_year['Data'])

        # Create empty columns if dataframe is empty
        if raw_data_income_statement.is_empty():
            empty_data_income_statement = pl.DataFrame(schema={
                "CompanyCode": pl.Int64,
                "CompanyName": pl.Utf8,
                "CompanyAbbreviation": pl.Utf8,
                "PeriodYear": pl.Utf8,
                "PeriodMonth": pl.Utf8,
                "AccountNumber": pl.Utf8,
                "AccountDescription": pl.Utf8,
                "AccountType": pl.Utf8,
                "Group1": pl.Utf8,
                "BeginAmount": pl.Float64,
                "DebitAmount": pl.Float64,
                "CreditAmount": pl.Float64,
                "EndAmount": pl.Float64,
                "Brand": pl.Utf8,
                "ProfitCenter": pl.Utf8,
                "ProfitCenterCode": pl.Utf8,
                "ArGroup": pl.Utf8,
            })
            raw_data_income_statement = empty_data_income_statement
        if raw_data_income_statement_last_year.is_empty():
            empty_data_income_statement_last_year = pl.DataFrame(schema={
                "CompanyCode": pl.Int64,
                "CompanyName": pl.Utf8,
                "CompanyAbbreviation": pl.Utf8,
                "PeriodYear": pl.Utf8,
                "PeriodMonth": pl.Utf8,
                "AccountNumber": pl.Utf8,
                "AccountDescription": pl.Utf8,
                "AccountType": pl.Utf8,
                "Group1": pl.Utf8,
                "BeginAmount": pl.Float64,
                "DebitAmount": pl.Float64,
                "CreditAmount": pl.Float64,
                "EndAmount": pl.Float64,
                "Brand": pl.Utf8,
                "ProfitCenter": pl.Utf8,
                "ProfitCenterCode": pl.Utf8,
                "ArGroup": pl.Utf8,
            })
            raw_data_income_statement_last_year = empty_data_income_statement_last_year
        if raw_data_income_budget.is_empty():
            empty_data_income_budget = pl.DataFrame(schema={
                "CompanyCode": pl.Int64,
                "CompanyName": pl.Utf8,
                "CompanyAbbreviation": pl.Utf8,
                "PeriodYear": pl.Utf8,
                "PeriodMonth": pl.Utf8,
                "AccountNumber": pl.Utf8,
                "AccountDescription": pl.Utf8,
                "AccountType": pl.Utf8,
                "Group1": pl.Utf8,
                "DebitAmount": pl.Float64,
                "CreditAmount": pl.Float64,
                "Brand": pl.Utf8,
                "ProfitCenterCode": pl.Utf8,
                "ProfitCenter": pl.Utf8,
                "ArGroup": pl.Utf8,
            })
            raw_data_income_budget = empty_data_income_budget
        if raw_data_income_budget_last_year.is_empty():
            empty_data_income_budget_last_year = pl.DataFrame(schema={
                "CompanyCode": pl.Int64,
                "CompanyName": pl.Utf8,
                "CompanyAbbreviation": pl.Utf8,
                "PeriodYear": pl.Int32,
                "PeriodMonth": pl.Int32,
                "AccountNumber": pl.Utf8,
                "AccountDescription": pl.Utf8,
                "AccountType": pl.Utf8,
                "Group1": pl.Utf8,
                "DebitAmount": pl.Int64,
                "CreditAmount": pl.Int64,
                "Brand": pl.Utf8,
                "ProfitCenterCode": pl.Utf8,
                "ProfitCenter": pl.Utf8,
                "ArGroup": pl.Utf8,
            })
            raw_data_income_budget_last_year = empty_data_income_budget_last_year

        raw_data_income_statement = raw_data_income_statement.with_columns(pl.col('Brand').str.strip_chars().str.to_uppercase())
        if selected_brand != 'ALL':
            raw_data_income_statement = raw_data_income_statement.filter(pl.col("Brand") == selected_brand)
        raw_data_income_statement_last_year = raw_data_income_statement_last_year.with_columns(pl.col('Brand').str.strip_chars().str.to_uppercase())
        if selected_brand != 'ALL':
            raw_data_income_statement_last_year = raw_data_income_statement_last_year.filter(pl.col("Brand") == selected_brand)
        raw_data_income_budget = raw_data_income_budget.with_columns(pl.col('Brand').str.strip_chars().str.to_uppercase())
        if selected_brand != 'ALL':
            raw_data_income_budget = raw_data_income_budget.filter(pl.col("Brand") == selected_brand)
        raw_data_income_budget_last_year = raw_data_income_budget_last_year.with_columns(pl.col('Brand').str.strip_chars().str.to_uppercase())
        if selected_brand != 'ALL':
            raw_data_income_budget_last_year = raw_data_income_budget_last_year.filter(pl.col("Brand") == selected_brand)
        
        # Tabs for each report
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["1️⃣ Income Statement", "2️⃣ Unit Performance", "3️⃣ Stock Management", "4️⃣ Aftersales Performance", "5️⃣ Cash Flow Management"])
        with tab1:
            income_statement(raw_data_income_statement,
                             raw_data_income_statement_last_year,
                             raw_data_income_budget,
                             raw_data_income_budget_last_year,
                             selected_month,
                             selected_brand)
        with tab2:
            main_unit_performance(raw_data_income_statement,
                                  raw_data_income_statement_last_year,
                                  raw_data_income_budget,
                                  selected_year,
                                  selected_month,
                                  selected_company,
                                  selected_brand)

        with tab3:
            main_tab.stock_management_tab(selected_company, selected_brand)

        with tab4:
            raw_data_income_statement = raw_data_income_statement.with_columns(((pl.col('DebitAmount') - pl.col('CreditAmount')) * -1).alias('mutation'))
            raw_data_income_statement_last_year = raw_data_income_statement_last_year.with_columns(((pl.col('DebitAmount') - pl.col('CreditAmount')) * -1).alias('mutation'))
            raw_data_income_budget = raw_data_income_budget.with_columns(((pl.col('DebitAmount') - pl.col('CreditAmount')) * -1).alias('mutation'))
            raw_data_income_budget_last_year = raw_data_income_budget_last_year.with_columns(((pl.col('DebitAmount') - pl.col('CreditAmount')) * -1).alias('mutation'))

            gross_profit = raw_data_income_statement.filter(pl.col('Group1').is_in(['4', '5']))
            gross_profit_last_year = raw_data_income_statement_last_year.filter(pl.col('Group1').is_in(['4', '5']))
            income_budget_gross_profit = raw_data_income_budget.filter(pl.col('Group1').is_in(['4', '5']))

            main_tab_aftersales_performance.main_tab_aftersales_performance(selected_year,
                                                                            selected_month,
                                                                            selected_company,
                                                                            selected_brand,
                                                                            gross_profit,
                                                                            gross_profit_last_year,
                                                                            income_budget_gross_profit,
                                                                            month_to_proceed(selected_month))
            
        with tab5:
            main_tab_cash_flow_management(selected_month,
                                          selected_year,
                                          selected_company,
                                          selected_brand)
    except Exception as err:
        st.error(err)
        st.write(err)