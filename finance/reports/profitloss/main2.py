from cProfile import label
import streamlit as st
from data import LoadData
from reports.profitloss.functions import filter, creategroup, preprocessing, processing
import pandas as pd
import numpy as np
import datetime, time
from reports.profitloss.functions.createrangeaxis import create_range_axis
from reports.profitloss.charts.r1_summary_profitloss import summary_profitloss_metrics
from reports.profitloss.charts.r2_summary_profitloss import summary_profitloss_indicator, summary_profitloss_scorecard
from reports.profitloss.charts.r3_summary_profitloss import summary_profitloss_grossprofit_year_bar, summary_profitloss_netoprprofit_year_bar
from reports.profitloss.charts.r4_summary_profitloss import summary_profitloss_netprofit_year_bar
from reports.profitloss.charts.r2_detail_profitloss import detail_profitloss_company, detail_profitloss_company_v2
from reports.profitloss.charts.r3_detail_profitloss import detail_profitloss_brand, detail_profitloss_brand_v2
from reports.profitloss.charts.r4_detail_profitloss import detail_profitloss_profitcenter, detail_profitloss_profitcenter_v2
from reports.profitloss.charts.r5_detail_profitloss import detail_profitloss_table
from reports.profitloss.charts.r6_detail_profitloss import detail_profitloss_profit_loss_statement
from reports.profitloss.charts.r7_detail_profitloss import detail_profitloss_company_brand
from utils.filter import financial_format
from utils.download import download_source

def profit_loss(userlogin, companies, brands):
    try:
        pd.set_option('display.max_columns', None)
        # pd.set_option('display.max_rows', None)
        pd.options.display.float_format = '{:,.2f}'.format

        start_time = time.time()
        #Header
        st.markdown("# Profit and Loss Report")
        
        #Applying general filter
        raw_data, all_year, level, selection, data_company_console, selected, select_year, selected_month, selected_month_num, select_company = filter.applyfilter(companies, brands)
        #Show last refresh time of loaded data
        refresh_time = LoadData.refresh_time("profit-loss")
        st.sidebar.markdown(f'<p style="text-align:center;font-weight:bold;">Last Refresh Time : <br> {refresh_time}</p>',unsafe_allow_html=True)

        # data calculation
        company_list = raw_data[['CompanyCode','CompanyName','CompanyAbbreviation']].drop_duplicates()
        summary_by_company = processing.calculate(raw_data, company_list, ['CompanyCode','CompanyName','CompanyAbbreviation'], "EndAmount")
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
        tab1, tab2, tab3 = st.tabs(["📝 Profit and Loss Summary", "📊 Profit Comparison", "📓 Profit and Loss Detail"])
        with tab1:
            income = np.abs(summary_by_company["income"].sum())
            cogs = np.abs(summary_by_company["cogs"].sum())
            expense = np.abs(summary_by_company["expense"].sum())
            other_income_expense = np.abs(summary_by_company["other_income_expense"].sum())
            gross_profit = summary_by_company['gross_profit'].sum()
            net_operating_profit = summary_by_company['net_operating_profit'].sum()
            net_profit = summary_by_company['net_profit'].sum()

            #region : metrics
            c11,c12,c13,c14,c15,c16 = st.columns((1,5,5,5,5,1))
            with c11:
                pass
            with c12:
                summary_profitloss_metrics('Income (Rp. Million)', income, None)
            with c13:
                summary_profitloss_metrics('COGS (Rp. Million)', cogs, None)
            with c14:
                summary_profitloss_metrics('Expense (Rp. Million)', expense, None)
            with c15:
                summary_profitloss_metrics('Other Income - Expense (Rp. Million)', other_income_expense, None)
            with c16:
                pass
            #endregion

            #region : indicator
            c1, c2, c3, c4, c5 = st.columns((1,4,4,4,1))
            with c1:
                pass
            with c2:
                percentage = gross_profit/income if income else 0
                summary_profitloss_metrics("Gross Profit", gross_profit, percentage)
            with c3:
                percentage = net_operating_profit/gross_profit if gross_profit else 0
                summary_profitloss_metrics("Net Operating Profit", net_operating_profit, percentage)
            with c4:
                percentage = net_profit/income if income else 0
                summary_profitloss_metrics("Net Profit Margin", net_profit, percentage)
            with c5:
                pass
            #end region
            
            # all year data calculation
            monthly = all_year[['PeriodYear', 'PeriodMonth', 'Month']].drop_duplicates()
            summary_by_all_year = processing.calculate(all_year, monthly, ['PeriodYear', 'PeriodMonth', 'Month'], "MutationAmount")
            
            profit_loss_summary_all_year_this_year = summary_by_all_year[summary_by_all_year['PeriodYear'] == str(select_year)].sort_values(by='PeriodMonth')
            profit_loss_summary_all_year_last_year = summary_by_all_year[summary_by_all_year['PeriodYear'] == str(select_year - 1)].sort_values(by='PeriodMonth')
            #end region

            #region : year comparison
            st.subheader('This Year vs Last Year Gross Profit Comparison (Rp. Million)')
            summary_profitloss_grossprofit_year_bar(profit_loss_summary_all_year_this_year, profit_loss_summary_all_year_last_year)

            st.subheader('This Year vs Last Year Net Operating Profit Comparison (Rp. Million)')
            summary_profitloss_netoprprofit_year_bar(profit_loss_summary_all_year_this_year, profit_loss_summary_all_year_last_year)

            st.subheader('This Year vs Last Year Net Profit Comparison (Rp. Million)')
            summary_profitloss_netprofit_year_bar(profit_loss_summary_all_year_this_year, profit_loss_summary_all_year_last_year)
            #end region

        with tab2:
            #region : metrics
            c11,c12,c13,c14,c15 = st.columns([1,2,2,2,1])  
            with c11:
                pass
            with c12:
                summary_profitloss_metrics('Gross Profit (Rp. Million)', gross_profit, None)
            with c13:
                summary_profitloss_metrics('Net Operating Profit (Rp. Million)', net_operating_profit, None)
            with c14:
                summary_profitloss_metrics('Net Profit (Rp. Million)', net_profit, None)
            with c15:
                pass
            #endregion

            #region : by company
            chart_raw_data = pd.merge(company_list, summary_by_company, how='left', left_on='company_name', right_on='CompanyName')
            chart_raw_data.drop_duplicates(inplace=True)
            chart_raw_data.fillna({'gross_profit': 0, 'net_operating_profit': 0, 'net_profit': 0}, inplace=True)

            chart_data_gross_profit = chart_raw_data.groupby('console_combine_name')['gross_profit'].sum().reset_index().sort_values('gross_profit', ascending=True)
            chart_data_netopr_profit = chart_raw_data.groupby('console_combine_name')['net_operating_profit'].sum().reset_index().sort_values('net_operating_profit', ascending=True)
            chart_data_net_profit = chart_raw_data.groupby('console_combine_name')['net_profit'].sum().reset_index().sort_values('net_profit', ascending=True)
            chart_data_gross_profit = chart_data_gross_profit[chart_data_gross_profit['gross_profit'] != 0]
            chart_data_netopr_profit = chart_data_netopr_profit[chart_data_netopr_profit['net_operating_profit'] != 0]
            chart_data_net_profit = chart_data_net_profit[chart_data_net_profit['net_profit'] != 0]
            
            if select_company == 'Select Company':
                st.subheader("Profit Comparison by Company (Rp. Million)")
                detail_profitloss_company_v2(chart_data_gross_profit, chart_data_netopr_profit, chart_data_net_profit, "gross_profit", "net_operating_profit", "net_profit")
            else:
                pass
            #end region
            
            #region : by brand
            brand_list = raw_data['Brand'].unique()
            brand_list = pd.DataFrame(brand_list, columns=['Brand'])
            summary_by_brand = processing.calculate(raw_data, brand_list, ["Brand"], "EndAmount")

            chart_data_gross_profit = summary_by_brand.sort_values('gross_profit', ascending=True)
            chart_data_netopr_profit = summary_by_brand.sort_values('net_operating_profit', ascending=True)
            chart_data_net_profit = summary_by_brand.sort_values('net_profit', ascending=True)
            chart_data_gross_profit = chart_data_gross_profit[chart_data_gross_profit['gross_profit'] != 0]
            chart_raw_data.fillna({'gross_profit': 0, 'net_operating_profit': 0, 'net_profit': 0}, inplace=True)
            chart_data_net_profit = chart_data_net_profit[chart_data_net_profit['net_profit'] != 0]

            #temp define brand
            passenger_premium = ['AUDI', 'LAND ROVER', 'JAGUAR', 'BENTLEY', 'MAXUS']
            r2 = ['YADEA', 'EMOTOR', 'SUZUKI_R2', 'HARLEY']
            truck = ['HINO', 'FOTON']
            all = ['AUDI', 'LAND ROVER', 'JAGUAR', 'BENTLEY', 'MAXUS', 'YADEA', 'EMOTOR', 'SUZUKI_R2', 'HARLEY','HINO', 'FOTON']
            
            st.subheader("Profit Comparison by Brand (Rp. Million)")
            b1, b2 = st.columns(2)
            with b1:
                st.subheader('Passenger Premium Brand')
                pp_gross_profit = chart_data_gross_profit[chart_data_gross_profit['Brand'].isin(passenger_premium)].copy()
                pp_netopr_profit = chart_data_netopr_profit[chart_data_netopr_profit['Brand'].isin(passenger_premium)].copy()
                pp_net_profit = chart_data_net_profit[chart_data_net_profit['Brand'].isin(passenger_premium)].copy()
                detail_profitloss_brand_v2(pp_gross_profit, pp_netopr_profit, pp_net_profit, "gross_profit", "net_operating_profit", "net_profit", label="passenger_premium_brand")
                
                st.subheader('R2 Brand')
                r2_gross_profit = chart_data_gross_profit[chart_data_gross_profit['Brand'].isin(r2)].copy()
                r2_netopr_profit = chart_data_netopr_profit[chart_data_netopr_profit['Brand'].isin(r2)].copy()
                r2_net_profit = chart_data_net_profit[chart_data_net_profit['Brand'].isin(r2)].copy()
                detail_profitloss_brand_v2(r2_gross_profit, r2_netopr_profit, r2_net_profit, "gross_profit", "net_operating_profit", "net_profit", label="r2_brand")
            with b2:
                st.subheader('Passenger Non-Premium Brand')
                pnp_gross_profit = chart_data_gross_profit[~chart_data_gross_profit['Brand'].isin(all)].copy()
                pnp_netopr_profit = chart_data_netopr_profit[~chart_data_netopr_profit['Brand'].isin(all)].copy()
                pnp_net_profit = chart_data_net_profit[~chart_data_net_profit['Brand'].isin(all)].copy()
                detail_profitloss_brand_v2(pnp_gross_profit, pnp_netopr_profit, pnp_net_profit, "gross_profit", "net_operating_profit", "net_profit", label="passenger_non_premium_brand")

                st.subheader('Truck Brand')
                truck_gross_profit = chart_data_gross_profit[chart_data_gross_profit['Brand'].isin(truck)].copy()
                truck_netopr_profit = chart_data_netopr_profit[chart_data_netopr_profit['Brand'].isin(truck)].copy()
                truck_net_profit = chart_data_net_profit[chart_data_net_profit['Brand'].isin(truck)].copy()
                detail_profitloss_brand_v2(truck_gross_profit, truck_netopr_profit, truck_net_profit, "gross_profit", "net_operating_profit", "net_profit", label="truck_brand")
            #end region

            #region : by profit center
            profitcenter_list = raw_data['ProfitCenter'].unique()
            profitcenter_list = pd.DataFrame(profitcenter_list, columns=['ProfitCenter'])
            summary_by_profit_center = processing.calculate(raw_data, profitcenter_list, ["ProfitCenter"], "EndAmount")
            
            chart_data_gross_profit = summary_by_profit_center.sort_values('gross_profit', ascending=True)
            chart_data_netopr_profit = summary_by_profit_center.sort_values('net_operating_profit', ascending=True)
            chart_data_net_profit = summary_by_profit_center.sort_values('net_profit', ascending=True)
            chart_data_gross_profit = chart_data_gross_profit[chart_data_gross_profit['gross_profit'] != 0]
            chart_data_netopr_profit = chart_data_netopr_profit[chart_data_netopr_profit['net_operating_profit'] != 0]
            chart_data_net_profit = chart_data_net_profit[chart_data_net_profit['net_profit'] != 0]
            
            st.subheader("Profit Comparison by Profit Center (Rp. Million)")
            detail_profitloss_profitcenter_v2(chart_data_gross_profit, chart_data_netopr_profit, chart_data_net_profit, "gross_profit", "net_operating_profit", "net_profit")
            #end region

        with tab3:
            # today = datetime.datetime.now()
            this_month = selected_month
            if selected_month_num == 1:
                last_month = "12"
            else:
                last_month = "0" + str(selected_month_num - 1) if len(str(selected_month_num - 1)) < 2 else str(selected_month_num - 1)

            #region: table
            table_border = st.container(border=True)
            table_data = raw_data.copy()
            table_data = table_data.sort_values(by="AccountNumber")
            table_data = table_data.assign(AccountDescription = table_data['AccountNumber'] + ' - ' + table_data["AccountDescription"])
            table_data = table_data[table_data["EndAmount"] != 0]
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

                table_data = table_data.groupby(['Group', 'Group2', 'AccountDescription'])['EndAmount'].sum()
                download_data = table_data.reset_index()
                raw_data_profit_loss_table = table_data.unstack(level=['Group2', 'AccountDescription'])
                raw_data_profit_loss_table = raw_data_profit_loss_table.assign(Total=raw_data_profit_loss_table.sum(1))
                raw_data_profit_loss_table = raw_data_profit_loss_table.stack(level='Group2', future_stack=True)
                raw_data_profit_loss_table = raw_data_profit_loss_table.assign(Total=raw_data_profit_loss_table.sum(1))
                raw_data_profit_loss_table = raw_data_profit_loss_table.stack(level='AccountDescription')
                raw_data_profit_loss_table = raw_data_profit_loss_table.reset_index(name='EndAmount')
                raw_data_profit_loss_table = raw_data_profit_loss_table[raw_data_profit_loss_table["EndAmount"] != 0]
                raw_data_profit_loss_table['EndAmount'] = raw_data_profit_loss_table['EndAmount'].apply(financial_format)
                raw_data_profit_loss_table['is_total'] = raw_data_profit_loss_table.apply(lambda row: 'Total' in row.values, axis=1)
                for col in raw_data_profit_loss_table.columns[:-1]:
                    raw_data_profit_loss_table[col] = raw_data_profit_loss_table.apply(lambda row: f"<b>{row[col]}</b>" if row['is_total'] else row[col], axis=1)
                raw_data_profit_loss_table = raw_data_profit_loss_table[~((raw_data_profit_loss_table['Group2'] == '<b>Total</b>') &
                                                                        (raw_data_profit_loss_table['AccountDescription'] == '<b>Total</b>'))]
                # raw_data_profit_loss_table = raw_data_profit_loss_table[~((raw_data_profit_loss_table['Group2'] == 'Total') &
                #                                                         (raw_data_profit_loss_table['AccountDescription'] == 'Total'))]
                detail_profitloss_table(raw_data_profit_loss_table)
                download_source([download_data], ['profit_loss'], 'Profit and Loss')
            #end region


            #region: profit loss statement calculation
            monthly = all_year[['PeriodYear', 'PeriodMonth', 'Month']].drop_duplicates()

            sales_all_year = all_year[all_year['Group'] == '4 - SALES']
            sales_all_year = sales_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['MutationAmount', 'EndAmount']].sum().reset_index()
            sales_all_year = sales_all_year.assign(SalesMtd = sales_all_year['MutationAmount'])
            sales_all_year = sales_all_year.assign(SalesYtd = sales_all_year['EndAmount'])
            sales_all_year = sales_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'SalesMtd', 'SalesYtd']]

            cogs_all_year = all_year[all_year['Group'] == '5 - COST OF GOOD SOLD']
            cogs_all_year = cogs_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['MutationAmount', 'EndAmount']].sum().reset_index()
            cogs_all_year = cogs_all_year.assign(CogsMtd = cogs_all_year['MutationAmount'])
            cogs_all_year = cogs_all_year.assign(CogsYtd = cogs_all_year['EndAmount'])
            cogs_all_year = cogs_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'CogsMtd', 'CogsYtd']]

            opex_all_year = all_year[all_year['Group'] == '6 - OPERATIONAL EXPENSE']
            opex_all_year = opex_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['MutationAmount', 'EndAmount']].sum().reset_index()
            opex_all_year = opex_all_year.assign(OpexMtd = opex_all_year['MutationAmount'])
            opex_all_year = opex_all_year.assign(OpexYtd = opex_all_year['EndAmount'])
            opex_all_year = opex_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'OpexMtd', 'OpexYtd']]

            otherin_all_year = all_year[all_year['Group'] == '7 - OTHER INCOME']
            otherin_all_year = otherin_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['MutationAmount', 'EndAmount']].sum().reset_index()
            otherin_all_year = otherin_all_year.assign(OtherinMtd = otherin_all_year['MutationAmount'])
            otherin_all_year = otherin_all_year.assign(OtherinYtd = otherin_all_year['EndAmount'])
            otherin_all_year = otherin_all_year[['PeriodYear', 'PeriodMonth', 'Month', 'OtherinMtd', 'OtherinYtd']]

            otherex_all_year = all_year[all_year['Group'] == '8 - OTHER EXPENSE']
            otherex_all_year = otherex_all_year.groupby(['PeriodYear', 'PeriodMonth', 'Month'])[['MutationAmount', 'EndAmount']].sum().reset_index()
            otherex_all_year = otherex_all_year.assign(OtherexMtd = otherex_all_year['MutationAmount'])
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
                    this_month_sales = profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                        (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['SalesMtd'].sum()
                    summary_profitloss_metrics('This Month Sales (Rp. Million)', this_month_sales, None)
                with c12:
                    last_month_sales = profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == (str(select_year) if last_month != '12' else str(select_year-1))) &
                                                                        (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['SalesMtd'].sum()
                    summary_profitloss_metrics('Last Month Sales (Rp. Million)', last_month_sales, None)
                with c13:
                    ytd_sales = profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['SalesYtd'].sum()
                    summary_profitloss_metrics('YTD Sales (Rp. Million)', ytd_sales, None)
                with c14:
                    lytd_sales = profit_loss_statement_all_year[(profit_loss_statement_all_year["PeriodYear"] == str(select_year-1)) &
                                                                (profit_loss_statement_all_year["PeriodMonth"] == this_month)]['SalesYtd'].sum()
                    summary_profitloss_metrics('LYTD Sales (Rp. Million)', lytd_sales, None)
                #endregion

                st.subheader('This Year vs Last Year Sales (Rp. Million) Comparison')
                this_year_sales = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year)]
                this_year_sales = this_year_sales.groupby(['PeriodMonth', 'Month'])['SalesMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_sales = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year - 1)]
                last_year_sales = last_year_sales.groupby(['PeriodMonth', 'Month'])['SalesMtd'].sum().reset_index().sort_values(by='PeriodMonth')

                detail_profitloss_profit_loss_statement(this_year_sales, last_year_sales, 'Sales', 'SalesMtd', label="this_year_vs_last_year_sales")
                
                sales_data = raw_data[raw_data['Group'] == '4 - SALES']
                sales_data = sales_data.assign(SalesMtd = sales_data['MutationAmount'])
                sales_company = sales_data.groupby(['CompanyName'])['SalesMtd'].sum().reset_index(name='Sales Amount').sort_values(by='Sales Amount', ascending=False).head(10).sort_values(by='Sales Amount')
                sales_company = sales_company[sales_company['Sales Amount'] != 0]
                sales_brand = sales_data.groupby(['Brand'])['SalesMtd'].sum().reset_index(name='Sales Amount').sort_values(by='Sales Amount', ascending=False).head(10).sort_values(by='Sales Amount')
                sales_brand = sales_brand[sales_brand['Sales Amount'] != 0]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 Sales Amount (Rp. Million) by Company")
                    detail_profitloss_company_brand(sales_company, "Sales Amount", "CompanyName", label="top_10_sales_amount_by_company")

                with c2:
                    st.subheader("Top 10 Sales Amount (Rp. Million) by Brand")
                    detail_profitloss_company_brand(sales_brand, "Sales Amount", "Brand", label="top_10_sales_amount_by_brand")

            with tab2:                
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_cogs = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                            (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['CogsMtd'].sum())
                    summary_profitloss_metrics('This Month COGS (Rp. Million)', this_month_cogs, None)
                with c12:
                    last_month_cogs = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == (str(select_year) if last_month != '12' else str(select_year-1))) &
                                                                            (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['CogsMtd'].sum())
                    summary_profitloss_metrics('Last Month COGS (Rp. Million)', last_month_cogs, None)
                with c13:
                    ytd_cogs = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                        (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['CogsYtd'].sum())
                    summary_profitloss_metrics('YTD COGS (Rp. Million)', ytd_cogs, None)
                with c14:
                    lytd_cogs = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year["PeriodYear"] == str(select_year-1)) &
                                                                      (profit_loss_statement_all_year["PeriodMonth"] == this_month)]['CogsYtd'].sum())
                    summary_profitloss_metrics('LYTD COGS (Rp. Million)', lytd_cogs, None)
                #endregion

                st.subheader('This Year vs Last Year COGS (Rp. Million) Comparison')
                this_year_cogs = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year)]
                this_year_cogs = this_year_cogs.groupby(['PeriodMonth', 'Month'])['CogsMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_cogs = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year - 1)]
                last_year_cogs = last_year_cogs.groupby(['PeriodMonth', 'Month'])['CogsMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                detail_profitloss_profit_loss_statement(this_year_cogs, last_year_cogs, 'COGS', 'CogsMtd', label="this_year_vs_last_year_cogs")

                cogs_data = raw_data[raw_data['Group'] == '5 - COST OF GOOD SOLD']
                cogs_data = cogs_data.assign(CogsMtd = np.abs(cogs_data['MutationAmount']))
                cogs_company = cogs_data.groupby(['CompanyName'])['CogsMtd'].sum().reset_index(name='COGS Amount').sort_values(by='COGS Amount', ascending=False).head(10).sort_values(by='COGS Amount')
                cogs_company = cogs_company[cogs_company['COGS Amount'] != 0]
                cogs_brand = cogs_data.groupby(['Brand'])['CogsMtd'].sum().reset_index(name='COGS Amount').sort_values(by='COGS Amount', ascending=False).head(10).sort_values(by='COGS Amount')
                cogs_brand = cogs_brand[cogs_brand['COGS Amount'] != 0]

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 COGS Amount (Rp. Million) by Company")
                    detail_profitloss_company_brand(cogs_company, "COGS Amount", "CompanyName", label="top_10_cogs_amount_by_company")

                with c2:
                    st.subheader("Top 10 COGS Amount (Rp. Million) by Brand")
                    detail_profitloss_company_brand(cogs_brand, "COGS Amount", "Brand", label="top_10_cogs_amount_by_brand")

            with tab3:
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_opex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                            (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OpexMtd'].sum())
                    summary_profitloss_metrics('This Month OPEX (Rp. Million)', this_month_opex, None)
                with c12:
                    last_month_opex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == (str(select_year) if last_month != '12' else str(select_year-1))) &
                                                                            (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OpexMtd'].sum())
                    summary_profitloss_metrics('Last Month OPEX (Rp. Million)', last_month_opex, None)
                with c13:
                    ytd_opex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                        (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OpexYtd'].sum())
                    summary_profitloss_metrics('YTD OPEX (Rp. Million)', ytd_opex, None)
                with c14:
                    lytd_opex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year["PeriodYear"] == str(select_year-1)) &
                                                                      (profit_loss_statement_all_year["PeriodMonth"] == this_month)]['OpexYtd'].sum())
                    summary_profitloss_metrics('LYTD OPEX (Rp. Million)', lytd_opex, None)
                #endregion

                st.subheader('This Year vs Last Year OPEX (Rp. Million) Comparison')
                this_year_opex = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year)]
                this_year_opex = this_year_opex.groupby(['PeriodMonth', 'Month'])['OpexMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_opex = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year - 1)]
                last_year_opex = last_year_opex.groupby(['PeriodMonth', 'Month'])['OpexMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                detail_profitloss_profit_loss_statement(this_year_opex, last_year_opex, 'OPEX', 'OpexMtd', label="this_year_vs_last_year_opex")

                opex_data = raw_data[raw_data['Group'] == '6 - OPERATIONAL EXPENSE'] 
                opex_data = opex_data.assign(OpexMtd = np.abs(opex_data['MutationAmount']))
                opex_company = opex_data.groupby(['CompanyName'])['OpexMtd'].sum().reset_index(name='OPEX Amount').sort_values(by='OPEX Amount', ascending=False).head(10).sort_values(by='OPEX Amount')
                opex_company = opex_company[opex_company['OPEX Amount'] != 0]
                opex_brand = opex_data.groupby(['Brand'])['OpexMtd'].sum().reset_index(name='OPEX Amount').sort_values(by='OPEX Amount', ascending=False).head(10).sort_values(by='OPEX Amount')
                opex_brand = opex_brand[opex_brand['OPEX Amount'] != 0]

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 OPEX Amount (Rp. Million) by Company")
                    detail_profitloss_company_brand(opex_company, "OPEX Amount", "CompanyName", label="top_10_opex_amount_by_company")

                with c2:
                    st.subheader("Top 10 OPEX Amount (Rp. Million) by Brand")
                    detail_profitloss_company_brand(opex_brand, "OPEX Amount", "Brand", label="top_10_opex_amount_by_brand")

            with tab4:
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_otherin = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                                (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OtherinMtd'].sum())
                    summary_profitloss_metrics('This Month Other Income (Rp. Million)', this_month_otherin, None)
                with c12:
                    last_month_otherin = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == (str(select_year) if last_month != '12' else str(select_year-1))) &
                                                                                (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OtherinMtd'].sum())
                    summary_profitloss_metrics('Last Month Other Income (Rp. Million)', last_month_otherin, None)
                with c13:
                    ytd_otherin = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                        (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OtherinYtd'].sum())
                    summary_profitloss_metrics('YTD Other Income (Rp. Million)', ytd_otherin, None)
                with c14:
                    lytd_otherin = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year["PeriodYear"] == str(select_year-1)) &
                                                                         (profit_loss_statement_all_year["PeriodMonth"] == this_month)]['OtherinYtd'].sum())
                    summary_profitloss_metrics('LYTD Other Income (Rp. Million)', lytd_otherin, None)
                #endregion

                st.subheader('This Year vs Last Year Other Income (Rp. Million) Comparison')
                this_year_otherin = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year)]
                this_year_otherin = this_year_otherin.groupby(['PeriodMonth', 'Month'])['OtherinMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_otherin = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year - 1)]
                last_year_otherin = last_year_otherin.groupby(['PeriodMonth', 'Month'])['OtherinMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                detail_profitloss_profit_loss_statement(this_year_otherin, last_year_otherin, 'Other Income', 'OtherinMtd', label="this_year_vs_last_year_other_income")

                otherin_data = raw_data[raw_data['Group'] == '7 - OTHER INCOME']
                otherin_data = otherin_data.assign(OtherinMtd = otherin_data['MutationAmount'])
                otherin_company = otherin_data.groupby(['CompanyName'])['OtherinMtd'].sum().reset_index(name='Other Income Amount').sort_values(by='Other Income Amount', ascending=False).head(10).sort_values(by='Other Income Amount')
                otherin_company = otherin_company[otherin_company['Other Income Amount'] != 0]
                otherin_brand = otherin_data.groupby(['Brand'])['OtherinMtd'].sum().reset_index(name='Other Income Amount').sort_values(by='Other Income Amount', ascending=False).head(10).sort_values(by='Other Income Amount')
                otherin_brand = otherin_brand[otherin_brand['Other Income Amount'] != 0]

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 Other Income Amount (Rp. Million) by Company")
                    detail_profitloss_company_brand(otherin_company, "Other Income Amount", "CompanyName", label="top_10_other_income_amount_by_company")

                with c2:
                    st.subheader("Top 10 Other Income Amount (Rp. Million) by Brand")
                    detail_profitloss_company_brand(otherin_brand, "Other Income Amount", "Brand", label="top_10_other_income_amount_by_brand")

            with tab5:
                #region : metrics
                c11,c12,c13,c14 = st.columns(4)  
                with c11:
                    this_month_otherex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                                (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OtherexMtd'].sum())
                    summary_profitloss_metrics('This Month Other Expense (Rp. Million)', this_month_otherex, None)
                with c12:
                    last_month_otherex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == (str(select_year) if last_month != '12' else str(select_year-1))) &
                                                                                (profit_loss_statement_all_year['PeriodMonth'] == last_month)]['OtherexMtd'].sum())
                    summary_profitloss_metrics('Last Month Other Expense (Rp. Million)', last_month_otherex, None)
                with c13:
                    ytd_otherex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year['PeriodYear'] == str(select_year)) &
                                                                        (profit_loss_statement_all_year['PeriodMonth'] == this_month)]['OtherexYtd'].sum())
                    summary_profitloss_metrics('YTD Other Expense (Rp. Million)', ytd_otherex, None)
                with c14:
                    lytd_otherex = np.abs(profit_loss_statement_all_year[(profit_loss_statement_all_year["PeriodYear"] == str(select_year-1)) &
                                                                         (profit_loss_statement_all_year["PeriodMonth"] == this_month)]['OtherexYtd'].sum())
                    summary_profitloss_metrics('LYTD Other Expense (Rp. Million)', lytd_otherex, None)
                #endregion

                st.subheader('This Year vs Last Year Other Expense (Rp. Million) Comparison')
                this_year_otherex = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year)]
                this_year_otherex = this_year_otherex.groupby(['PeriodMonth', 'Month'])['OtherexMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                last_year_otherex = profit_loss_statement_all_year[profit_loss_statement_all_year['PeriodYear'] == str(select_year - 1)]
                last_year_otherex = last_year_otherex.groupby(['PeriodMonth', 'Month'])['OtherexMtd'].sum().reset_index().sort_values(by='PeriodMonth')
                detail_profitloss_profit_loss_statement(this_year_otherex, last_year_otherex, 'Other Expense', 'OtherexMtd', label="this_year_vs_last_year_other_expense")

                otherex_data = raw_data[raw_data['Group'] == '8 - OTHER EXPENSE']
                otherex_data = otherex_data.assign(OtherexMtd = np.abs(otherex_data['MutationAmount']))
                otherex_company = otherex_data.groupby(['CompanyName'])['OtherexMtd'].sum().reset_index(name='Other Expense Amount').sort_values(by='Other Expense Amount', ascending=False).head(10).sort_values(by='Other Expense Amount')
                otherex_company = otherex_company[otherex_company['Other Expense Amount'] != 0]
                otherex_brand = otherex_data.groupby(['Brand'])['OtherexMtd'].sum().reset_index(name='Other Expense Amount').sort_values(by='Other Expense Amount', ascending=False).head(10).sort_values(by='Other Expense Amount')
                otherex_brand = otherex_brand[otherex_brand['Other Expense Amount'] != 0]

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("Top 10 Other Expense Amount (Rp. Million) by Company")
                    detail_profitloss_company_brand(otherex_company, "Other Expense Amount", "CompanyName", label="top_10_other_expense_amount_by_company")

                with c2:
                    st.subheader("Top 10 Other Expense Amount (Rp. Million) by Brand")
                    detail_profitloss_company_brand(otherex_brand, "Other Expense Amount", "Brand", label="top_10_other_expense_amount_by_brand")

    # end_time = time.time()
    # st.write(end_time - start_time)
    except Exception as err:
        st.error("Data is empty, please check database !!!")