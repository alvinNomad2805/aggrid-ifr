import streamlit as st
import pandas as pd
from data.LoadData import load_data_users, post_logging
from reports.araging import main as main_araging
from reports.ifr import main as main_ifr
from reports.profitloss import main2 as main_profitloss
from reports.balancesheet import main as main_balance_sheet
from reports.ifr import main as main_ifr
from reports.ifr_full_report import IFR as ifr_full_report

def mainpage(userlogin,statusrole):
    with open('./assets/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    try:
        #Navigation
        st.sidebar.link_button("Sales Dashboard","https://ies-sales.indomobil.co.id/")
        st.sidebar.link_button("Aftersales Dashboard","https://ies-aftersales.indomobil.co.id/")

        # create the sidebar for filter and change page
        st.sidebar.subheader(f"User : {userlogin}")
        st.sidebar.image("./assets/indomobilGroup.png", width=200)
        st.sidebar.header("Indomobil Dashboard")
            
        page_names_to_function = {
            "AR Aging":main_araging.ar_aging,
            "Profit and Loss":main_profitloss.profit_loss,
            "Balance Sheet":main_balance_sheet.balance_sheet,
            "IFR":main_ifr.internet_financial_reporting,
            "IFR Full Report": ifr_full_report.ifr_full_report,
        }
        
        #read data user from back-end
        data_user_role = load_data_users(f"/user-access-finance?levelup={1}&role={statusrole}&username={userlogin}")
        data_user_role = data_user_role['Data']
        data_user_role = pd.DataFrame(data_user_role)
        data_user_role = data_user_role[data_user_role['PageModule'] == 'Finance']

        page_list = data_user_role[['PageIndex', 'PageName']].sort_values('PageIndex', ascending=True)
        page_list = page_list['PageName'].unique()
        company_list = data_user_role['CompanyFinanceFilter'].unique().tolist()
        brand_list = data_user_role[data_user_role['BrandName'] != 'VW']
        brand_list = brand_list['BrandName'].unique().tolist()

        if statusrole == 'ADMIN':
            company_list = []
            page_list = page_names_to_function.keys()

        page_change = st.sidebar.selectbox('Dashboard Page',page_list,key="page")
        module='finance'
        brand_selector=''
        logger_success = post_logging(module, page_change, brand_selector, userlogin, statusrole)
        if not logger_success:
            print("Logging failed")
        else:
            pass
        page_names_to_function[page_change](userlogin, company_list, brand_list)
    except Exception as err:
        raise st.error(err)
