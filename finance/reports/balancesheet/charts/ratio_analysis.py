import streamlit as st
from reports.balancesheet.functions.currencyformat import finance_format
from utils.filter import financial_format
import numpy as np

def displ_ratio(raw_data, pl_raw_data):
    st.markdown('<h2 class="section-title">Financial Ratio Summary</h2>',unsafe_allow_html=True)
    r1s1,r1s2,r1s3 = st.columns(3)
    sales = pl_raw_data[pl_raw_data['Group1'] == '4']["EndAmount"].sum()
    with r1s1:
        current_assets = raw_data[raw_data['Groupdesc2'].str.contains('11')]
        current_assets_amount = abs(np.sum(current_assets['EndAmount'].values))
        current_liabilities = raw_data[raw_data['Groupdesc2'].str.contains('21')]
        current_liabilities_amount = abs(np.sum(current_liabilities['EndAmount'].values))
        current_ratio = (current_assets_amount/current_liabilities_amount if current_liabilities_amount else 0) * 100
        st.metric("Current Ratio",value="%.2f" %(current_ratio) + " %")
    with r1s2:
        cash_and_bank = raw_data[raw_data['Groupdesc3'].str.contains('1101')]
        cash_and_bank_amount = abs(np.sum(cash_and_bank['EndAmount'].values))
        deposit = raw_data[raw_data['Groupdesc3'].str.contains('1102')]
        deposit_amount = abs(np.sum(deposit['EndAmount'].values))
        investment = raw_data[raw_data['Groupdesc3'].str.contains('1103')]
        investment_amount = abs(np.sum(investment['EndAmount'].values))
        ar_trade = raw_data[raw_data['Groupdesc3'].str.contains('1110')]
        ar_trade_amount = np.sum(ar_trade['EndAmount'].values)
        ar_non_trade = raw_data[raw_data['Groupdesc3'].str.contains('1120')]
        ar_non_trade_amount = abs(np.sum(ar_non_trade['EndAmount'].values))

        ap_trade = raw_data[raw_data['Groupdesc3'].str.contains('2110')]
        ap_trade_amount = abs(np.sum(ap_trade['EndAmount'].values))
        ap_non_trade = raw_data[raw_data['Groupdesc3'].str.contains('2120')]
        ap_non_trade_amount = abs(np.sum(ap_non_trade['EndAmount'].values))

        numerator = cash_and_bank_amount + deposit_amount + investment_amount + ar_trade_amount + ar_non_trade_amount
        denumerator = ap_trade_amount + ap_non_trade_amount
        st.metric("Quick Ratio",value="%.2f" %((numerator/denumerator)*100) + " %" if denumerator else "0.00 %")
    with r1s3:
        cr_numerator = cash_and_bank_amount + deposit_amount + investment_amount
        cr_denumerator = ap_trade_amount + ap_non_trade_amount
        st.metric("Cash Ratio",value="%.2f" %((cr_numerator/cr_denumerator)*100) + " %" if cr_denumerator else "0.00 %")
    
    st.divider()

    r2s1,r2s2,r2s3 = st.columns(3)
    with r2s1:
        receivable_turnover = (sales / (ap_trade_amount + ap_non_trade_amount))*100 if (ap_trade_amount + ap_non_trade_amount) else 0
        st.metric("Receivable Turnover",value="%.2f" %(receivable_turnover) + " %")
    with r2s2:
        inv = raw_data[raw_data['Groupdesc3'].str.contains('1150')]
        inv_amount = abs(inv['EndAmount'].sum())
        inv_prod = raw_data[raw_data['Groupdesc3'].str.contains('1152')]
        inv_prod_amount = abs(inv_prod['EndAmount'].sum())
        good_in_trans = raw_data[raw_data['Groupdesc3'].str.contains('1158')]
        good_in_trans_amount = abs(good_in_trans['EndAmount'].sum())
        stock_allow = raw_data[raw_data['Groupdesc3'].str.contains('1159')]
        stock_allow_amount = stock_allow['EndAmount'].sum()
        inv_numerator = inv_amount + inv_prod_amount + stock_allow_amount
        if inv_numerator == 0:
            inv_numerator = 0.00000000000000000000000000000001
        st.metric("Inventory Turnover",value=finance_format((sales/inv_numerator)*100,"%"))
    with r2s3:
        fa = raw_data[raw_data['Groupdesc3'].str.contains('1210')]
        fa_amount = abs(fa['EndAmount'].sum())
        acc_dep_ass = raw_data[raw_data['Groupdesc3'].str.contains('1211')]
        acc_dep_ass_amount = acc_dep_ass['EndAmount'].sum()

        fa_turnover = fa_amount + acc_dep_ass_amount
        st.metric("Fixed Assets Turnover",value="%.2f" %((sales/fa_turnover)*100) + " %" if fa_turnover else "0.00 %")
    
    r3s1,r3s2 = st.columns(2)
    if sales == 0:
        get_res = 0
    else:
        get_res = (ar_trade_amount+ar_non_trade_amount)*365/sales
    with r3s1:  
        st.metric("Avg. Collection Turnover",value="%.2f" %((get_res)*100) + " %")
    with r3s2:
        working_capital_turnover = (sales / (current_assets_amount - current_liabilities_amount) * 100) if (current_assets_amount - current_liabilities_amount) else 0
        st.metric("Working Capital Turnover", value=f"{finance_format(working_capital_turnover, '%')}")
        # st.metric("Working Capital Turnover",value=f"{finance_format((sales/(current_assets_amount-current_liabilities_amount)*100),'%')}")

    st.divider()
    r4s1,r4s2,r4s3 = st.columns(3)
    with r4s1:
        cogs = pl_raw_data[pl_raw_data["Group1"] == '5']["EndAmount"].sum()
        if sales == 0:
            get_res = 0
        else:
            get_res = (sales + cogs)/sales
        st.metric("Gross Profit Margin",value=f"{financial_format(get_res * 100)} %")
    with r4s2:
        opex = pl_raw_data[pl_raw_data['Group1'] == '6']["EndAmount"].sum()
        other_in_ex = pl_raw_data[~pl_raw_data['Group1'].isin(['4', '5', '6'])]["EndAmount"].sum()
        if sales == 0:
            get_res = 0
        else:
            get_res = (sales + cogs + opex + other_in_ex)/sales
        st.metric("Net Profit Margin",value=f"{financial_format(get_res * 100)} %")
    with r4s3:
        if sales == 0:
            get_res = 0
        else:
            get_res = (sales + cogs + opex) / sales
        st.metric("Operating Income Ratio",value=f"{financial_format( get_res* 100)} %")

    st.divider()

    ss1,ss2,ss3 = st.columns(3)
    with ss1:
        assets = raw_data[raw_data['Groupdesc1'] == '1 - ASSETS']["EndAmount"].sum()
        minus_var = pl_raw_data[pl_raw_data['Group2'].isin([
            "81 - Tax Expense", 
            "82 - Deffered Tax", 
            "91 - Minority share of non-controlling interests",
            "94 - Recognition of the fair value of assets when transferred",
            "95 - Comprehensive income"])]["EndAmount"].sum()
        earning_power_of_total_investment = (sales + cogs + opex + other_in_ex - minus_var)/assets * 100 if assets else 0
        st.metric("Earning Power of Total Investment",value=f"{financial_format(earning_power_of_total_investment)} %")
    with ss2:
        return_on_investment = (sales + cogs + opex + other_in_ex)/assets * 100 if assets else 0
        st.metric("Return on Investment",value=f"{financial_format(return_on_investment)} %")
    with ss3:
        equity = raw_data[raw_data['Groupdesc1'] == '3 - EQUITY']["EndAmount"].sum()
        return_on_equity = (sales + cogs + opex + other_in_ex)/equity * 100 if equity else 0
        st.metric("Return on Equity",value=f"{financial_format(return_on_equity)} %")

    st.divider()
    st.markdown('<h2 class="section-title">Ratio Analysis Formula (%)</h2>',unsafe_allow_html=True)
    st.image("./assets/ratio-analysis-formula.png",use_container_width =True)
    
    st.divider()