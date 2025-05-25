import streamlit as st
from data.LoadData import refresh_time
from reports.balancesheet.functions import filter,preprocessing
from reports.balancesheet.functions.creategroup import create_group_fixed
from reports.balancesheet.charts import summary_page,detail_page,ratio_analysis
from reports.profitloss.functions import preprocessing as plpreprocessing

def check_group_asset(val):
    if val/1 > 0:
        return "Asset"
    else:
        return "Accumulation Depreciation"
    
def balance_sheet(userlogin, companies, brands):
    try:
        #Header
        st.markdown("# Balance Sheet")
        #Applying general filter
        raw_data, level, selection, data_company_console, selected, selected_month,default_companies, pl_raw_data = filter.applyfilter(companies,brands)

        if default_companies != []:
            default_companies = default_companies[1:]
            all_companies = data_company_console[data_company_console['console_combine_name'].isin(default_companies)]
        else:
            all_companies = []
        
        #Show last refresh time of loaded data
        time_to_refresh = refresh_time('balance-sheet')
        st.sidebar.markdown(f'<p style="text-align:center;font-weight:bold;">Last Refresh Time : <br> {time_to_refresh}</p>',unsafe_allow_html=True)

        #preprocessing
        raw_data = preprocessing.preprocessing(raw_data)
        pl_raw_data = plpreprocessing.preprocessing(pl_raw_data, data_company_console)
        if level == 0:
            raw_data = raw_data[raw_data['CompanyName'].isin(all_companies['company_name'])]
            pl_raw_data = pl_raw_data[pl_raw_data['CompanyName'].isin(all_companies['company_name'])]

        st.divider()
        ratio_data = raw_data.copy()
    
        tab_summary, tab_detail, tab_ratio = st.tabs(['Summary','Detail','Ratio Analysis'])
        with tab_summary:
            summary_page.summary(raw_data)

        with tab_detail:
            results = create_group_fixed(raw_data)
            results['GroupAssets'] = results['EndAmount'].apply(check_group_asset)
            results = results[['CompanyCode','CompanyName','FAGroup','AccountDescription','GroupAssets','BeginAmount','EndAmount']]
            detail_page.detail(raw_data,ratio_data,results)

        with tab_ratio:
            ratio_analysis.displ_ratio(ratio_data,pl_raw_data)

    except Exception as err:
        st.error("Data is Empty, Please Check")

