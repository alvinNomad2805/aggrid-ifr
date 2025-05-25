import streamlit as st
from data import LoadData
from reports.profitloss.functions import filter, creategroup, preprocessing
import pandas as pd
import numpy as np
import datetime
from reports.profitloss.functions.createrangeaxis import create_range_axis
from reports.profitloss.charts.r1_summary_profitloss import summary_profitloss_metrics
from reports.profitloss.charts.r2_summary_profitloss import summary_profitloss_indicator
from reports.profitloss.charts.r3_summary_profitloss import summary_profitloss_grossprofit_year_bar, summary_profitloss_netoprprofit_year_bar
from reports.profitloss.charts.r4_summary_profitloss import summary_profitloss_netprofit_year_bar
from reports.profitloss.charts.r2_detail_profitloss import detail_profitloss_company, detail_profitloss_company_v2
from reports.profitloss.charts.r3_detail_profitloss import detail_profitloss_brand, detail_profitloss_brand_v2
from reports.profitloss.charts.r4_detail_profitloss import detail_profitloss_profitcenter, detail_profitloss_profitcenter_v2
from reports.profitloss.charts.r5_detail_profitloss import detail_profitloss_table
from reports.profitloss.charts.r6_detail_profitloss import detail_profitloss_profit_loss_statement
from reports.profitloss.charts.r7_detail_profitloss import detail_profitloss_company_brand
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:,.2f}'.format

def profit_loss_view(userlogin,companies,brands):
    raw_data = LoadData.load_data("/profit-loss-view?year=2024&month=06")
    raw_data_df = pd.DataFrame(raw_data)
    print(raw_data_df)

def profit_loss(userlogin, companies, brands):
    try:
        #Header
        st.markdown("# Profit and Loss Report")
        
        #Applying general filter
        raw_data, all_year, level, selection, data_company_console, selected, selected_month, select_company = filter.applyfilter(companies, brands)

        #Show last refresh time of loaded data
        refresh_time = LoadData.refresh_time("profit-loss")
        st.sidebar.markdown(f'<p style="text-align:center;font-weight:bold;">Last Refresh Time : <br> {refresh_time}</p>',unsafe_allow_html=True)

        #preprocessing
        raw_data = preprocessing.preprocessing(raw_data, data_company_console)
        all_year = preprocessing.preprocessing(all_year, data_company_console)

        # data calculation
        company_list = raw_data[['CompanyCode','CompanyName','CompanyAbbreviation']].drop_duplicates()

        raw_data_gross_profit = raw_data[raw_data['Group1'].isin(['4','5'])]
        raw_data_gross_profit = raw_data_gross_profit.groupby(['CompanyCode','CompanyName','CompanyAbbreviation'])['EndAmount'].sum().reset_index(name='Gross Profit')

        raw_data_netopr_profit = raw_data[raw_data['Group1'].isin(['4','5','6'])]
        raw_data_netopr_profit = raw_data_netopr_profit.groupby(['CompanyCode','CompanyName','CompanyAbbreviation'])['EndAmount'].sum().reset_index(name='Net Operating Profit')
        
        raw_data_net_profit = raw_data.groupby(['CompanyCode','CompanyName','CompanyAbbreviation'])['EndAmount'].sum().reset_index(name='Net Profit')
        
        profit_loss_summary = pd.merge(company_list, raw_data_gross_profit, how='left', on=['CompanyCode', 'CompanyName', 'CompanyAbbreviation'])
        profit_loss_summary = pd.merge(profit_loss_summary, raw_data_netopr_profit, how='left', on=['CompanyCode', 'CompanyName', 'CompanyAbbreviation'])
        profit_loss_summary = pd.merge(profit_loss_summary, raw_data_net_profit, how='left', on=['CompanyCode', 'CompanyName', 'CompanyAbbreviation'])
        profit_loss_summary.fillna({'Gross Profit': 0, 'Net Operating Profit': 0,'Net Profit': 0}, inplace=True)
        #end region

        #Create company list
        list_of_company = selection[level]
        if level != 3:
            company_list = data_company_console[data_company_console['console_combine_name'].isin(list_of_company)][['console_combine_name', 'company_name']]

            parent = raw_data['CompanyName'].unique().tolist()
            child = company_list['company_name'].unique().tolist()
            company_to_add = list(set(parent) - set(child))
            new_data = {'console_combine_name': company_to_add, 'company_name': company_to_add}
            new_data = pd.DataFrame(new_data)
            company_list = pd.concat([company_list, new_data], ignore_index=True)
            company_list.drop_duplicates(inplace=True)

            if company_list.empty or company_list['console_combine_name'].unique().tolist() == company_to_add:
                list_of_company = selection[3]
                company_list = data_company_console[data_company_console['company_name'].isin(list_of_company)][['console_combine_name', 'company_name']]
                company_list.loc[:,'console_combine_name'] = company_list['company_name']

        else:
            company_list = data_company_console[data_company_console['company_name'].isin(list_of_company)][['console_combine_name', 'company_name']]
            company_list.loc[:,'console_combine_name'] = company_list['company_name']
        #end region

        #showing charts
        tab1, tab2, tab3 = st.tabs(["📝 Summary", "📊 Profit Comparison", "📓 Profit and Loss Statement"])
        with tab1:
            raw_data_income_expense = raw_data.groupby(['AccountType'])['EndAmount'].sum().reset_index()
            income = np.abs(raw_data_income_expense[raw_data_income_expense['AccountType'] == 'I']['EndAmount'].sum())
            expense = np.abs(raw_data_income_expense[raw_data_income_expense['AccountType'] == 'E']['EndAmount'].sum())
            gross_profit = profit_loss_summary['Gross Profit'].sum()
            net_operating_profit = profit_loss_summary['Net Operating Profit'].sum()
            net_profit = profit_loss_summary['Net Profit'].sum()

            #region : metrics
            c11,c12,c13,c14,c15 = st.columns(5)  
            with c11:
                summary_profitloss_metrics('Income (Sales + Other Incomes)', income)
            with c12:
                summary_profitloss_metrics('Expense (COGS + Other Expenses)', expense)
            with c13:
                summary_profitloss_metrics('Gross Profit', gross_profit)
            with c14:
                summary_profitloss_metrics('Net Operating Profit', net_operating_profit)
            with c15:
                summary_profitloss_metrics('Net Profit', net_profit)
            #endregion

            #region : indicator
            c1, c2, c3 = st.columns(3)
            with c1:
                gross_profit = profit_loss_summary['Gross Profit'].sum()
                sales = raw_data[raw_data['Group1'] == '4']['EndAmount'].sum()
                percentage = gross_profit/sales * 100
                summary_profitloss_indicator("Gross Profit Margin", percentage)
            with c2:
                net_opr_profit = profit_loss_summary['Net Operating Profit'].sum()
                percentage = net_opr_profit/gross_profit * 100
                summary_profitloss_indicator("Net Operating Profit Margin", percentage)
            with c3:
                net_profit = profit_loss_summary['Net Profit'].sum()
                income = raw_data_income_expense[raw_data_income_expense['AccountType'] == 'I']['EndAmount'].sum()
                percentage = net_profit/income * 100
                summary_profitloss_indicator("Net Profit Margin", percentage)
            #end region
            
            # all year data calculation
            monthly = all_year[['PeriodYear', 'PeriodMonth', 'Month']].drop_duplicates()

            gross_profit_all_year = all_year[all_year['Group1'].isin(['4','5'])]
            gross_profit_all_year = gross_profit_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])['EndAmount'].sum().reset_index(name='Gross Profit')

            netopr_profit_all_year = all_year[all_year['Group1'].isin(['4','5','6'])]
            netopr_profit_all_year = netopr_profit_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])['EndAmount'].sum().reset_index(name='Net Operating Profit')
        
            net_profit_all_year = all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])['EndAmount'].sum().reset_index(name='Net Profit')
            
            profit_loss_summary_all_year = pd.merge(monthly, gross_profit_all_year, how='left', on=['PeriodYear', 'PeriodMonth', 'Month'])
            profit_loss_summary_all_year = pd.merge(profit_loss_summary_all_year, netopr_profit_all_year, how='left', on=['PeriodYear', 'PeriodMonth', 'Month'])
            profit_loss_summary_all_year = pd.merge(profit_loss_summary_all_year, net_profit_all_year, how='left', on=['PeriodYear', 'PeriodMonth', 'Month'])
            profit_loss_summary_all_year.fillna({'Gross Profit': 0, 'Net Operating Profit': 0, 'Net Profit': 0}, inplace=True)

            today = datetime.datetime.now()
            profit_loss_summary_all_year_this_year = profit_loss_summary_all_year[profit_loss_summary_all_year['PeriodYear'] == str(today.year)].sort_values(by='PeriodMonth')
            profit_loss_summary_all_year_last_year = profit_loss_summary_all_year[profit_loss_summary_all_year['PeriodYear'] == str(today.year - 1)].sort_values(by='PeriodMonth')
            #end region

            #region : year comparison
            st.subheader('This Year vs Last Year Gross Profit Comparison')
            summary_profitloss_grossprofit_year_bar(profit_loss_summary_all_year_this_year, profit_loss_summary_all_year_last_year)

            st.subheader('This Year vs Last Year Net Operating Profit Comparison')
            summary_profitloss_netoprprofit_year_bar(profit_loss_summary_all_year_this_year, profit_loss_summary_all_year_last_year)

            st.subheader('This Year vs Last Year Net Profit Comparison')
            summary_profitloss_netprofit_year_bar(profit_loss_summary_all_year_this_year, profit_loss_summary_all_year_last_year)
            #end region

        with tab2:
            #region : metrics
            c11,c12,c13,c14,c15 = st.columns([1,2,2,2,1])  
            with c11:
                pass
            with c12:
                summary_profitloss_metrics('Gross Profit', gross_profit)
            with c13:
                summary_profitloss_metrics('Net Operating Profit', net_opr_profit)
            with c14:
                summary_profitloss_metrics('Net Profit', net_profit)
            with c15:
                pass
            #endregion

            #region : by company
            chart_raw_data = pd.merge(company_list, profit_loss_summary, how='left', left_on='company_name', right_on='CompanyName')
            chart_raw_data.drop_duplicates(inplace=True)
            chart_raw_data.fillna({'Gross Profit': 0, 'Net Operating Profit': 0, 'Net Profit': 0}, inplace=True)
            chart_data_gross_profit = chart_raw_data.groupby('console_combine_name')['Gross Profit'].sum().reset_index().sort_values('Gross Profit', ascending=True)
            chart_data_netopr_profit = chart_raw_data.groupby('console_combine_name')['Net Operating Profit'].sum().reset_index().sort_values('Net Operating Profit', ascending=True)
            chart_data_net_profit = chart_raw_data.groupby('console_combine_name')['Net Profit'].sum().reset_index().sort_values('Net Profit', ascending=True)
            chart_data_gross_profit = chart_data_gross_profit[chart_data_gross_profit['Gross Profit'] != 0]
            chart_data_netopr_profit = chart_data_netopr_profit[chart_data_netopr_profit['Net Operating Profit'] != 0]
            chart_data_net_profit = chart_data_net_profit[chart_data_net_profit['Net Profit'] != 0]
            
            if select_company == 'Select Company':
                st.subheader("Profit Comparison by Company")
                detail_profitloss_company_v2(chart_data_gross_profit, chart_data_netopr_profit, chart_data_net_profit, "Gross Profit", "Net Operating Profit", "Net Profit")
            else:
                pass
            #end region

            #region : by brand
            brand_list = raw_data['Brand'].unique()
            brand_list = pd.DataFrame(brand_list, columns=['Brand'])

            raw_data_gross_profit = raw_data[raw_data['Group1'].isin(['4','5'])]
            raw_data_gross_profit = raw_data_gross_profit.groupby(["Brand"])['EndAmount'].sum().reset_index(name='Gross Profit')

            raw_data_netopr_profit = raw_data[raw_data['Group1'].isin(['4','5','6'])]
            raw_data_netopr_profit = raw_data_netopr_profit.groupby(["Brand"])['EndAmount'].sum().reset_index(name='Net Operating Profit')
        
            raw_data_net_profit = raw_data.groupby(["Brand"])['EndAmount'].sum().reset_index(name='Net Profit')
            
            profit_loss_summary = pd.merge(brand_list, raw_data_gross_profit, how='left', on=['Brand'])
            profit_loss_summary = pd.merge(profit_loss_summary, raw_data_netopr_profit, how='left', on=['Brand'])
            profit_loss_summary = pd.merge(profit_loss_summary, raw_data_net_profit, how='left', on=['Brand'])
            profit_loss_summary.fillna({'Gross Profit': 0, 'Net Operating Profit': 0, 'Net Profit': 0}, inplace=True)

            chart_data_gross_profit = profit_loss_summary.sort_values('Gross Profit', ascending=True)
            chart_data_netopr_profit = profit_loss_summary.sort_values('Net Operating Profit', ascending=True)
            chart_data_net_profit = profit_loss_summary.sort_values('Net Profit', ascending=True)
            chart_data_gross_profit = chart_data_gross_profit[chart_data_gross_profit['Gross Profit'] != 0]
            chart_data_netopr_profit = chart_data_netopr_profit[chart_data_netopr_profit['Net Operating Profit'] != 0]
            chart_data_net_profit = chart_data_net_profit[chart_data_net_profit['Net Profit'] != 0]
        
            st.subheader("Profit Comparison by Brand")
            detail_profitloss_brand_v2(chart_data_gross_profit, chart_data_netopr_profit, chart_data_net_profit, "Gross Profit", "Net Operating Profit", "Net Profit")
            #end region

            #region : by profit center
            profitcenter_list = raw_data['ProfitCenter'].unique()
            profitcenter_list = pd.DataFrame(profitcenter_list, columns=['ProfitCenter'])

            raw_data_gross_profit = raw_data[raw_data['Group1'].isin(['4','5'])]
            raw_data_gross_profit = raw_data_gross_profit.groupby(["ProfitCenter"])['EndAmount'].sum().reset_index(name='Gross Profit')

            raw_data_netopr_profit = raw_data[raw_data['Group1'].isin(['4','5','6'])]
            raw_data_netopr_profit = raw_data_netopr_profit.groupby(["ProfitCenter"])['EndAmount'].sum().reset_index(name='Net Operating Profit')
        
            raw_data_net_profit = raw_data.groupby(["ProfitCenter"])['EndAmount'].sum().reset_index(name='Net Profit')
            
            profit_loss_summary = pd.merge(profitcenter_list, raw_data_gross_profit, how='left', on=['ProfitCenter'])
            profit_loss_summary = pd.merge(profit_loss_summary, raw_data_netopr_profit, how='left', on=['ProfitCenter'])
            profit_loss_summary = pd.merge(profit_loss_summary, raw_data_net_profit, how='left', on=['ProfitCenter'])
            profit_loss_summary.fillna({'Gross Profit': 0, 'Net Operating Profit': 0, 'Net Profit': 0}, inplace=True)
            
            chart_data_gross_profit = profit_loss_summary.sort_values('Gross Profit', ascending=True)
            chart_data_netopr_profit = profit_loss_summary.sort_values('Net Operating Profit', ascending=True)
            chart_data_net_profit = profit_loss_summary.sort_values('Net Profit', ascending=True)
            chart_data_gross_profit = chart_data_gross_profit[chart_data_gross_profit['Gross Profit'] != 0]
            chart_data_netopr_profit = chart_data_netopr_profit[chart_data_netopr_profit['Net Operating Profit'] != 0]
            chart_data_net_profit = chart_data_net_profit[chart_data_net_profit['Net Profit'] != 0]
            
            st.subheader("Profit Comparison by Profit Center")
            detail_profitloss_profitcenter_v2(chart_data_gross_profit, chart_data_netopr_profit, chart_data_net_profit, "Gross Profit", "Net Operating Profit", "Net Profit")
            #end region

        with tab3:
            today = datetime.datetime.now()
            this_month = selected_month
            converted_month = int(this_month)
            if converted_month == 1:
                last_month = "12"
            else:
                last_month = "0" + str(converted_month - 1) if len(str(converted_month - 1)) < 2 else str(converted_month - 2)

            #region: table
            table_border = st.container(border=True)
            table_data = raw_data.copy()
            with table_border:
                #table filter
                c1, c2, c3 = st.columns(3)
                with c1:
                    group_list = table_data['Group'].sort_values().unique().tolist()
                    group_list.insert(0, 'Select Category')
                    group_filter = st.selectbox('Category', options=group_list)
                    if group_filter != 'Select Category':
                        table_data = table_data[table_data['Group'] == group_filter]
                with c2:
                    group2_list = table_data['Group2'].sort_values().unique().tolist()
                    group2_list.insert(0, 'Select Group')
                    group2_filter = st.selectbox('Group', options=group2_list)
                    if group2_filter != 'Select Group':
                        table_data = table_data[table_data['Group2'] == group2_filter]
                with c3:
                    account_list = table_data['AccountDescription'].sort_values().unique().tolist()
                    account_list.insert(0, 'Select Account')
                    account_filter = st.selectbox('Account', options=account_list)
                    if account_filter != 'Select Account':
                        table_data = table_data[table_data['AccountDescription'] == account_filter]

                raw_data_profit_loss_table = table_data.groupby(['Group', 'Group2', 'AccountDescription'])['EndAmount'].sum().unstack(level=['Group2', 'AccountDescription'])
                raw_data_profit_loss_table = raw_data_profit_loss_table.assign(Total=raw_data_profit_loss_table.sum(1))
                raw_data_profit_loss_table = raw_data_profit_loss_table.stack(level='Group2')
                raw_data_profit_loss_table = raw_data_profit_loss_table.assign(Total=raw_data_profit_loss_table.sum(1))
                raw_data_profit_loss_table = raw_data_profit_loss_table.stack(level='AccountDescription')
                raw_data_profit_loss_table = raw_data_profit_loss_table.reset_index(name='EndAmount')
                raw_data_profit_loss_table['EndAmount'] = raw_data_profit_loss_table['EndAmount'].apply(lambda x: 'Rp. {:,.2f}'.format(x))
                raw_data_profit_loss_table['is_total'] = raw_data_profit_loss_table.apply(lambda row: 'Total' in row.values, axis=1)
                for col in raw_data_profit_loss_table.columns[:-1]:
                    raw_data_profit_loss_table[col] = raw_data_profit_loss_table.apply(lambda row: f"<b>{row[col]}</b>" if row['is_total'] else row[col], axis=1)
                raw_data_profit_loss_table = raw_data_profit_loss_table[~((raw_data_profit_loss_table['Group2'] == '<b>Total</b>') &
                                                                        (raw_data_profit_loss_table['AccountDescription'] == '<b>Total</b>'))]

                detail_profitloss_table(raw_data_profit_loss_table)
            #end region

            #region: profit loss statement calculation
            monthly = all_year[['PeriodYear', 'PeriodMonth', 'Month']].drop_duplicates()

            sales_all_year = all_year[all_year['Group'] == '4 - SALES']
            sales_all_year = sales_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['DebitAmount', 'CreditAmount', 'EndAmount']].sum().reset_index()
            sales_all_year = sales_all_year.assign(SalesMtd = sales_all_year['CreditAmount'] - sales_all_year['DebitAmount'])
            sales_all_year = sales_all_year.assign(SalesYtd = sales_all_year['EndAmount'])
            sales_all_year = sales_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'SalesMtd', 'SalesYtd']]

            cogs_all_year = all_year[all_year['Group'] == '5 - COST OF GOOD SOLD']
            cogs_all_year = cogs_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['DebitAmount', 'CreditAmount', 'EndAmount']].sum().reset_index()
            cogs_all_year = cogs_all_year.assign(CogsMtd = cogs_all_year['CreditAmount'] - cogs_all_year['DebitAmount'])
            cogs_all_year = cogs_all_year.assign(CogsYtd = cogs_all_year['EndAmount'])
            cogs_all_year = cogs_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'CogsMtd', 'CogsYtd']]

            opex_all_year = all_year[all_year['Group'] == '6 - OPERATIONAL EXPENSE']
            opex_all_year = opex_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['DebitAmount', 'CreditAmount', 'EndAmount']].sum().reset_index()
            opex_all_year = opex_all_year.assign(OpexMtd = opex_all_year['CreditAmount'] - opex_all_year['DebitAmount'])
            opex_all_year = opex_all_year.assign(OpexYtd = opex_all_year['EndAmount'])
            opex_all_year = opex_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'OpexMtd', 'OpexYtd']]

            otherin_all_year = all_year[all_year['Group'] == '7 - OTHER INCOME']
            otherin_all_year = otherin_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['DebitAmount', 'CreditAmount', 'EndAmount']].sum().reset_index()
            otherin_all_year = otherin_all_year.assign(OtherinMtd = otherin_all_year['CreditAmount'] - otherin_all_year['DebitAmount'])
            otherin_all_year = otherin_all_year.assign(OtherinYtd = otherin_all_year['EndAmount'])
            otherin_all_year = otherin_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'OtherinMtd', 'OtherinYtd']]

            otherex_all_year = all_year[all_year['Group'] == '8 - OTHER EXPENSE']
            otherex_all_year = otherex_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['DebitAmount', 'CreditAmount', 'EndAmount']].sum().reset_index()
            otherex_all_year = otherex_all_year.assign(OtherexMtd = otherex_all_year['CreditAmount'] - otherex_all_year['DebitAmount'])
            otherex_all_year = otherex_all_year.assign(OtherexYtd = otherex_all_year['EndAmount'])
            otherex_all_year = otherex_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'OtherexMtd', 'OtherexYtd']]
            
            profit_loss_statement_all_year = pd.merge(monthly, sales_all_year, how='left', on=['PeriodYear', 'PeriodMonth', 'Month'])
            profit_loss_statement_all_year = pd.merge(profit_loss_statement_all_year, cogs_all_year, how='left', on=['PeriodYear', 'PeriodMonth', 'Month'])
            profit_loss_statement_all_year = pd.merge(profit_loss_statement_all_year, opex_all_year, how='left', on=['PeriodYear', 'PeriodMonth', 'Month'])
            profit_loss_statement_all_year = pd.merge(profit_loss_statement_all_year, otherin_all_year, how='left', on=['PeriodYear', 'PeriodMonth', 'Month'])
            profit_loss_statement_all_year = pd.merge(profit_loss_statement_all_year, otherex_all_year, how='left', on=['PeriodYear', 'PeriodMonth', 'Month'])
            profit_loss_statement_all_year.fillna({'SalesMtd': 0, 'SalesYtd': 0, 'CogsMtd': 0, 'CogsYtd': 0, 'OpexMtd': 0, 'OpexYtd': 0,
                                                   'OtherinMtd': 0, 'OtherinYtd': 0, 'OtherexMtd': 0, 'OtherexYtd': 0,}, inplace=True)
            #end region

            tab1, tab2, tab3, tab4, tab5 = st.tabs(["4️⃣ Sales", "5️⃣ Cost of Goods Sold", "6️⃣ Operational Expenses", "7️⃣ Other Incomes", "8️⃣ Other Expenses"])
            with tab1:
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_sales = profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                      (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['SalesMtd'].sum()
                    summary_profitloss_metrics('This Month Sales', this_month_sales)
                with c12:
                    last_month_sales = profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                      (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['SalesMtd'].sum()
                    summary_profitloss_metrics('Last Month Sales', last_month_sales)
                with c13:
                    ytd_sales = profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                               (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['SalesYtd'].sum()
                    summary_profitloss_metrics('YTD Sales', ytd_sales)
                with c14:
                    lytd_sales = profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                               (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['SalesYtd'].sum()
                    summary_profitloss_metrics('LYTD Sales', lytd_sales)
                #endregion

                st.subheader('This Year vs Last Year Sales Comparison')
                this_year_sales = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year)]
                this_year_sales = this_year_sales.groupby(['PeriodMonth', 'Month'])['SalesMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_sales = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year - 1)]
                last_year_sales = last_year_sales.groupby(['PeriodMonth', 'Month'])['SalesMtd'].sum().reset_index().sort_values(by='PeriodMonth')

                detail_profitloss_profit_loss_statement(this_year_sales, last_year_sales, 'Sales', 'SalesMtd')
                
                sales_data = raw_data[raw_data['Group'] == '4 - SALES']
                sales_data = sales_data.assign(SalesMtd = sales_data['CreditAmount'] - sales_data['DebitAmount'])
                sales_company = sales_data.groupby(['CompanyName'])['SalesMtd'].sum().reset_index(name='Sales Amount').sort_values(by='Sales Amount', ascending=False).head(10).sort_values(by='Sales Amount')
                sales_company = sales_company[sales_company['Sales Amount'] != 0]
                sales_brand = sales_data.groupby(['Brand'])['SalesMtd'].sum().reset_index(name='Sales Amount').sort_values(by='Sales Amount', ascending=False).head(10).sort_values(by='Sales Amount')
                sales_brand = sales_brand[sales_brand['Sales Amount'] != 0]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 Sales Amount by Company")
                    detail_profitloss_company_brand(sales_company, "Sales Amount", "CompanyName")

                with c2:
                    st.subheader("Top 10 Sales Amount by Brand")
                    detail_profitloss_company_brand(sales_brand, "Sales Amount", "Brand")

            with tab2:                
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_cogs = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                            (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['CogsMtd'].sum())
                    summary_profitloss_metrics('This Month COGS', this_month_cogs)
                with c12:
                    last_month_cogs = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                            (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['CogsMtd'].sum())
                    summary_profitloss_metrics('Last Month COGS', last_month_cogs)
                with c13:
                    ytd_cogs = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                     (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['CogsYtd'].sum())
                    summary_profitloss_metrics('YTD COGS', ytd_cogs)
                with c14:
                    lytd_cogs = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                      (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['CogsYtd'].sum())
                    summary_profitloss_metrics('LYTD COGS', lytd_cogs)
                #endregion

                st.subheader('This Year vs Last Year COGS Comparison')
                this_year_cogs = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year)]
                this_year_cogs = this_year_cogs.groupby(['PeriodMonth', 'Month'])['CogsMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_cogs = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year - 1)]
                last_year_cogs = last_year_cogs.groupby(['PeriodMonth', 'Month'])['CogsMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                detail_profitloss_profit_loss_statement(this_year_cogs, last_year_cogs, 'COGS', 'CogsMtd')

                cogs_data = raw_data[raw_data['Group'] == '5 - COST OF GOOD SOLD']
                cogs_data = cogs_data.assign(CogsMtd = np.abs(cogs_data['CreditAmount'] - cogs_data['DebitAmount']))
                cogs_company = cogs_data.groupby(['CompanyName'])['CogsMtd'].sum().reset_index(name='COGS Amount').sort_values(by='COGS Amount', ascending=False).head(10).sort_values(by='COGS Amount')
                cogs_company = cogs_company[cogs_company['COGS Amount'] != 0]
                cogs_brand = cogs_data.groupby(['Brand'])['CogsMtd'].sum().reset_index(name='COGS Amount').sort_values(by='COGS Amount', ascending=False).head(10).sort_values(by='COGS Amount')
                cogs_brand = cogs_brand[cogs_brand['COGS Amount'] != 0]

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 COGS Amount by Company")
                    detail_profitloss_company_brand(cogs_company, "COGS Amount", "CompanyName")

                with c2:
                    st.subheader("Top 10 COGS Amount by Brand")
                    detail_profitloss_company_brand(cogs_brand, "COGS Amount", "Brand")

            with tab3:
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_opex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                            (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OpexMtd'].sum())
                    summary_profitloss_metrics('This Month OPEX', this_month_opex)
                with c12:
                    last_month_opex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                            (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OpexMtd'].sum())
                    summary_profitloss_metrics('Last Month OPEX', last_month_opex)
                with c13:
                    ytd_opex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                     (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OpexYtd'].sum())
                    summary_profitloss_metrics('YTD OPEX', ytd_opex)
                with c14:
                    lytd_opex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                      (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OpexYtd'].sum())
                    summary_profitloss_metrics('LYTD OPEX', lytd_opex)
                #endregion

                st.subheader('This Year vs Last Year OPEX Comparison')
                this_year_opex = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year)]
                this_year_opex = this_year_opex.groupby(['PeriodMonth', 'Month'])['OpexMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_opex = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year - 1)]
                last_year_opex = last_year_opex.groupby(['PeriodMonth', 'Month'])['OpexMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                detail_profitloss_profit_loss_statement(this_year_opex, last_year_opex, 'OPEX', 'OpexMtd')

                opex_data = raw_data[raw_data['Group'] == '6 - OPERATIONAL EXPENSE'] 
                opex_data = opex_data.assign(OpexMtd = np.abs(opex_data['CreditAmount'] - opex_data['DebitAmount']))
                opex_company = opex_data.groupby(['CompanyName'])['OpexMtd'].sum().reset_index(name='OPEX Amount').sort_values(by='OPEX Amount', ascending=False).head(10).sort_values(by='OPEX Amount')
                opex_company = opex_company[opex_company['OPEX Amount'] != 0]
                opex_brand = opex_data.groupby(['Brand'])['OpexMtd'].sum().reset_index(name='OPEX Amount').sort_values(by='OPEX Amount', ascending=False).head(10).sort_values(by='OPEX Amount')
                opex_brand = opex_brand[opex_brand['OPEX Amount'] != 0]

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 OPEX Amount by Company")
                    detail_profitloss_company_brand(opex_company, "OPEX Amount", "CompanyName")

                with c2:
                    st.subheader("Top 10 OPEX Amount by Brand")
                    detail_profitloss_company_brand(opex_brand, "OPEX Amount", "Brand")

            with tab4:
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_otherin = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                               (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OtherinMtd'].sum())
                    summary_profitloss_metrics('This Month Other Income', this_month_otherin)
                with c12:
                    last_month_otherin = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                               (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OtherinMtd'].sum())
                    summary_profitloss_metrics('Last Month Other Income', last_month_otherin)
                with c13:
                    ytd_otherin = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                        (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OtherinYtd'].sum())
                    summary_profitloss_metrics('YTD Other Income', ytd_otherin)
                with c14:
                    lytd_otherin = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                         (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OtherinYtd'].sum())
                    summary_profitloss_metrics('LYTD Other Income', lytd_otherin)
                #endregion

                st.subheader('This Year vs Last Year Other Income Comparison')
                this_year_otherin = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year)]
                this_year_otherin = this_year_otherin.groupby(['PeriodMonth', 'Month'])['OtherinMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_otherin = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year - 1)]
                last_year_otherin = last_year_otherin.groupby(['PeriodMonth', 'Month'])['OtherinMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                detail_profitloss_profit_loss_statement(this_year_otherin, last_year_otherin, 'Other Income', 'OtherinMtd')

                otherin_data = raw_data[raw_data['Group'] == '7 - OTHER INCOME']
                otherin_data = otherin_data.assign(OtherinMtd = np.abs(otherin_data['CreditAmount'] - otherin_data['DebitAmount']))
                otherin_company = otherin_data.groupby(['CompanyName'])['OtherinMtd'].sum().reset_index(name='Other Income Amount').sort_values(by='Other Income Amount', ascending=False).head(10).sort_values(by='Other Income Amount')
                otherin_company = otherin_company[otherin_company['Other Income Amount'] != 0]
                otherin_brand = otherin_data.groupby(['Brand'])['OtherinMtd'].sum().reset_index(name='Other Income Amount').sort_values(by='Other Income Amount', ascending=False).head(10).sort_values(by='Other Income Amount')
                otherin_brand = otherin_brand[otherin_brand['Other Income Amount'] != 0]

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 Other Income Amount by Company")
                    detail_profitloss_company_brand(otherin_company, "Other Income Amount", "CompanyName")

                with c2:
                    st.subheader("Top 10 Other Income Amount by Brand")
                    detail_profitloss_company_brand(otherin_brand, "Other Income Amount", "Brand")

            with tab5:
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_otherex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                               (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OtherexMtd'].sum())
                    summary_profitloss_metrics('This Month Other Expense', this_month_otherex)
                with c12:
                    last_month_otherex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                               (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OtherexMtd'].sum())
                    summary_profitloss_metrics('Last Month Other Expense', last_month_otherex)
                with c13:
                    ytd_otherex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                        (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OtherexYtd'].sum())
                    summary_profitloss_metrics('YTD Other Expense', ytd_otherex)
                with c14:
                    lytd_otherex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(today.year)) &
                                                                         (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OtherexYtd'].sum())
                    summary_profitloss_metrics('LYTD Other Expense', lytd_otherex)
                #endregion

                st.subheader('This Year vs Last Year Other Expense Comparison')
                this_year_otherex = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year)]
                this_year_otherex = this_year_otherex.groupby(['PeriodMonth', 'Month'])['OtherexMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_otherex = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(today.year - 1)]
                last_year_otherex = last_year_otherex.groupby(['PeriodMonth', 'Month'])['OtherexMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                detail_profitloss_profit_loss_statement(this_year_otherex, last_year_otherex, 'Other Expense', 'OtherexMtd')

                otherex_data = raw_data[raw_data['Group'] == '8 - OTHER EXPENSE']
                otherex_data = otherex_data.assign(OtherexMtd = np.abs(otherex_data['CreditAmount'] - otherex_data['DebitAmount']))
                otherex_company = otherex_data.groupby(['CompanyName'])['OtherexMtd'].sum().reset_index(name='Other Expense Amount').sort_values(by='Other Expense Amount', ascending=False).head(10).sort_values(by='Other Expense Amount')
                otherex_company = otherex_company[otherex_company['Other Expense Amount'] != 0]
                otherex_brand = otherex_data.groupby(['Brand'])['OtherexMtd'].sum().reset_index(name='Other Expense Amount').sort_values(by='Other Expense Amount', ascending=False).head(10).sort_values(by='Other Expense Amount')
                otherex_brand = otherex_brand[otherex_brand['Other Expense Amount'] != 0]

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 Other Expense Amount by Company")
                    detail_profitloss_company_brand(otherex_company, "Other Expense Amount", "CompanyName")

                with c2:
                    st.subheader("Top 10 Other Expense Amount by Brand")
                    detail_profitloss_company_brand(otherex_brand, "Other Expense Amount", "Brand")

    except:
        st.error("Data is empty, please check database !!!")