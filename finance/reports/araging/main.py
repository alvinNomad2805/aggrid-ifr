from cProfile import label
import streamlit as st
from reports.araging.functions import filter
from data import LoadData
from utils.alvinmelt import melt
from streamlit_extras.metric_cards import style_metric_cards
from reports.araging.charts.r2_summary_araging import summary_araging, summary_araging_invoice
from reports.araging.charts.r1_detail_araging import detail_argroup
from reports.araging.charts.r2_detail_araging import detail_brand, detail_profit_center
from reports.araging.charts.r3_detail_araging import detail_company, detail_customer
import datetime
import pandas as pd
from dateutil import parser
from utils.download import download_source
from utils.filter import financial_format

def ar_aging(userlogin, companies, brands):
    try:
        #Header
        st.markdown("# Aging Report")
        #Applying general filter
        raw_data = filter.applyfilter(companies, brands)
        data_for_customer = raw_data.copy()
        #Show last refresh time of loaded data
        refresh_time = LoadData.refresh_time("araging")
        st.sidebar.markdown(f'<p style="text-align:center;font-weight:bold;">Last Refresh Time : <br> {refresh_time}</p>',unsafe_allow_html=True)
        #showing charts
        
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

        tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "📊 Details", "1️⃣ Details - 3rd Party", "2️⃣ Details - Afiliated"])
        with tab1:
            #region : applying group by in raw_data
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
            #endregion

            sumofendingamount = int((raw_data_over_due_aging['BeginAmount'].sum()+raw_data_over_due_aging['SalesAmount'].sum())-
                                        (raw_data_over_due_aging['SalesCorrectionAmount'].sum()+raw_data_over_due_aging['PayAmount'].sum()+
                                        raw_data_over_due_aging['PayReturnAmount'].sum()+raw_data_over_due_aging['PayCorrectionAmount'].sum()))
            sumofnotoverdue = int(raw_data_over_due_aging['NotOverDueAmount'].sum()) 

            #region : metrics
            c11,c12,c13,c14 = st.columns([2,2,2,2])  
            with c11:
                pass
            with c12:
                st.metric('Sum of Ending Amount (Rp. Million)', financial_format(sumofendingamount/1000000))
                style_metric_cards()
            with c13:
                st.metric('Sum of Not Over Due (Rp. Million)', financial_format(sumofnotoverdue/1000000))
                style_metric_cards()
            with c14:
                pass
            #endregion

            #region : barchart
            st.subheader("AR Aging Over Due Ending Amount (Rp. Million)")
            chart_data = melt(raw_data_over_due_aging,id_var=['Days0to7','Days8to14','Days15to21','Days22to30','Days31to60','Days61to90','Days90'])
            summary_araging(chart_data)
            #endregion

            today = pd.to_datetime(datetime.datetime.now().date()) 

            raw_data = raw_data.copy()
            raw_data['today_date'] = today 
            raw_data['InvDate'] = raw_data['InvDate'].apply(lambda x: parser.parse(x).replace(tzinfo=None) if pd.notnull(x) else pd.NaT)
            raw_data['InvDate'] = pd.to_datetime(raw_data['InvDate'], errors='coerce')

            # Calculate the date difference
            raw_data['DateDiff'] = (raw_data['today_date'] - raw_data['InvDate']).dt.days

            # Define the bins and their labels
            bins = [0, 7, 14, 21, 30, 60, 90, float('inf')]
            labels = ['Days0to7', 'Days8to14', 'Days15to21', 'Days22to30', 'Days31to60', 'Days61to90', 'Days90']

            # Categorize the days into bins
            raw_data['category'] = pd.cut(raw_data['DateDiff'], bins=bins, labels=labels, right=False)
            
            raw_data_diff_invoice = raw_data.groupby(['category'], observed=True).agg({'BeginAmount':'sum',
                                                                        'SalesAmount':'sum',
                                                                        'SalesCorrectionAmount':'sum',
                                                                        'NotOverDueAmount':'sum',
                                                                        'PayAmount':'sum',
                                                                        'PayReturnAmount':'sum',
                                                                        'PayCorrectionAmount':'sum'}).reset_index()

            raw_data_diff_invoice.loc[:,'EndingAmount'] = raw_data_diff_invoice['BeginAmount']+raw_data_diff_invoice['SalesAmount']-raw_data_diff_invoice['SalesCorrectionAmount']+raw_data_diff_invoice['PayAmount']+raw_data_diff_invoice['PayReturnAmount']+raw_data_diff_invoice['PayCorrectionAmount']
            st.subheader("AR Aging Invoice (Rp. Million)")
            summary_araging_invoice(raw_data_diff_invoice)

        with tab2:
            raw_data = raw_data.groupby(['VehicleBrand',
                                    'ArGroupDescription',
                                    'ProfitCenterDescription',
                                    'CustTypeDescription',
                                    'CompanyName',
                                    'CustomerName']).agg({'BeginAmount':'sum',
                                                        'SalesAmount':'sum',
                                                        'SalesCorrectionAmount':'sum',
                                                        'NotOverDueAmount':'sum',
                                                        'PayAmount':'sum',
                                                        'PayReturnAmount':'sum',
                                                        'PayCorrectionAmount':'sum'}).reset_index()
            raw_data.loc[:,'EndingAmount'] = (raw_data['BeginAmount']+raw_data['SalesAmount'])-(raw_data['SalesCorrectionAmount']+raw_data['PayAmount']+raw_data['PayReturnAmount']+raw_data['PayCorrectionAmount'])
            
            st.subheader("Ending Amount by AR Group")
            detail_argroup(raw_data)

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Ending Amount by Brand (Rp. Million)")
                chart_data = raw_data.groupby('VehicleBrand')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=True)
                detail_brand(chart_data, label="ending_amount_by_brand")

            with c2:
                st.subheader("Ending Amount by Profit Center (Rp. Million)")
                chart_data = raw_data.groupby('ProfitCenterDescription')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=True)
                detail_profit_center(chart_data, label="ending_amount_by_profit_center")

            c1, c2 = st.columns(2)
            with c1:
                chart_data = raw_data.groupby('CompanyName')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=False)[:10]
                chart_data = chart_data.sort_values('EndingAmount', ascending=True)
                st.subheader(f"Top {len(chart_data)} Ending Amount by Company (Rp. Million)")
                detail_company(chart_data, label="ending_amount_by_company")

            with c2:
                chart_data = raw_data.groupby('CustomerName')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=False)[:10]
                chart_data = chart_data.sort_values('EndingAmount', ascending=True)
                st.subheader(f"Top {len(chart_data)} Ending Amount by Customer Name (Rp. Million)")
                detail_customer(chart_data, "EndingAmount", label="ending_amount_by_customer")

        with tab3:
            chart_raw_data = raw_data[raw_data['ArGroupDescription'] == 'Pihak Ke - 3']
            sumofendingamount = round(chart_raw_data['EndingAmount'].sum())

            chart_customer_data = data_for_customer[data_for_customer['ArGroupDescription'] == 'Pihak Ke - 3']
            chart_customer_data = chart_customer_data.groupby(['CustomerName']).agg({'Days31to60':'sum',
                                                                                    'Days61to90':'sum',
                                                                                    'Days90':'sum'}).reset_index()
            chart_customer_data['longest_overdue_amount'] = chart_customer_data['Days31to60'] + chart_customer_data['Days61to90'] + chart_customer_data['Days90']

            c11,c12,c13 = st.columns(3)  
            with c11:
                pass
            with c12:
                st.metric('Sum of Ending Amount Pihak Ke - 3 (Rp. Million)',value=financial_format(sumofendingamount/1000000))
                style_metric_cards()
            with c13:
                pass

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Ending Amount by Brand (Rp. Million)")
                chart_data = chart_raw_data.groupby('VehicleBrand')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=True)
                detail_brand(chart_data, label="ending_amount_by_brand_pihak_ketiga")

            with c2:
                st.subheader("Ending Amount by Profit Center (Rp. Million)")
                chart_data = chart_raw_data.groupby('ProfitCenterDescription')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=True)
                detail_profit_center(chart_data, label="ending_amount_by_profit_center_pihak_ketiga")

            c3, c4 = st.columns(2)
            with c3:
                chart_data = chart_raw_data.groupby('CompanyName')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=False)[:10]
                chart_data = chart_data.sort_values('EndingAmount', ascending=True)
                st.subheader(f"Top {len(chart_data)} Ending Amount by Company (Rp. Million)")
                detail_company(chart_data, label="ending_amount_by_company_pihak_ketiga")

            with c4:
                chart_data = chart_customer_data.groupby('CustomerName')['longest_overdue_amount'].sum().reset_index().sort_values('longest_overdue_amount', ascending=False)[:10]
                chart_data = chart_data.sort_values('longest_overdue_amount', ascending=True)
                st.subheader(f"Top {len(chart_data)} AR Overdue > 31 Days by Customer Name (Rp. Million)")
                detail_customer(chart_data, "longest_overdue_amount", label="longest_overdue_amount_pihak_ketiga")

        with tab4:
            chart_raw_data = raw_data[raw_data['ArGroupDescription'] == 'Afiliasi']
            sumofendingamount = round(chart_raw_data['EndingAmount'].sum())
            
            c11,c12,c13 = st.columns(3)  
            with c11:
                pass
            with c12:
                st.metric('Sum of Ending Amount Afiliasi (Rp. Million)',value=financial_format(sumofendingamount/1000000))
                style_metric_cards()
            with c13:
                pass

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Ending Amount by Brand (Rp. Million)")
                chart_data = chart_raw_data.groupby('VehicleBrand')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=True)
                detail_brand(chart_data, label="ending_amount_by_brand_afiliasi")

            with c2:
                st.subheader("Ending Amount by Profit Center (Rp. Million)")
                chart_data = chart_raw_data.groupby('ProfitCenterDescription')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=True)
                detail_profit_center(chart_data, label="ending_amount_by_profit_center_afiliasi")

            c3, c4 = st.columns(2)
            with c3:
                chart_data = chart_raw_data.groupby('CompanyName')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=False)[:10]
                chart_data = chart_data.sort_values('EndingAmount', ascending=True)
                st.subheader(f"Top {len(chart_data)} Ending Amount by Company (Rp. Million)")
                detail_company(chart_data, label="ending_amount_by_company_afiliasi")

            with c4:
                chart_data = chart_raw_data.groupby('CustomerName')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=False)[:10]
                chart_data = chart_data.sort_values('EndingAmount', ascending=True)
                st.subheader(f"Top {len(chart_data)} Ending Amount by Customer Name (Rp. Million)")
                detail_customer(chart_data, "EndingAmount", label="ending_amount_by_customer_afiliasi")

    except:
        st.error("Data is empty, please check database !!!")