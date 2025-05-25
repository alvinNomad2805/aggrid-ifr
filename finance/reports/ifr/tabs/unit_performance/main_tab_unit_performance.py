import pandas as pd
import polars as pl
from utils.caching import parquet_by_yearly
import streamlit as st
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from utils.timefunction import month_to_proceed
from utils.filter import financial_format

def main_unit_performance(raw_data_income_statement,
                          raw_data_income_statement_last_year,
                          raw_data_income_budget,
                          selected_year,
                          selected_month,
                          selected_company,
                          selected_brand):
    
    raw_data_income_statement = raw_data_income_statement.with_columns(((pl.col("DebitAmount") - pl.col("CreditAmount")) * -1).alias('mutation'))
    raw_data_income_statement_last_year = raw_data_income_statement_last_year.with_columns(((pl.col("DebitAmount") - pl.col("CreditAmount")) * -1).alias('mutation'))
    
    gross_profit = raw_data_income_statement.filter(pl.col('Group1').is_in(['4', '5']))
    gross_profit_actual = gross_profit.filter(pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum()

    # #YTD
    # gross_profit_last_year = raw_data_income_statement_last_year[raw_data_income_statement_last_year['Group1'].isin(['4', '5'])]
    # income_budget_gross_profit = raw_data_income_budget[raw_data_income_budget['Group1'].isin(['4', '5'])]

    #Unit Performance
    raw_data_unit_sales = parquet_by_yearly(selected_year,
                                            f"reports/ifr/parquet/ifr-unit-performance_{selected_year}_{selected_company}.parquet",
                                            f"/ifr-unit-performance?company_name={selected_company}&year={(selected_year)}")
    raw_data_unit_sales_lytd = parquet_by_yearly(selected_year-1,
                                            f"reports/ifr/parquet/ifr-unit-performance_{selected_year-1}_{selected_company}.parquet",
                                            f"/ifr-unit-performance?company_name={selected_company}&year={(selected_year-1)}")
    if selected_brand != 'ALL':
        raw_data_unit_sales = raw_data_unit_sales.filter(pl.col('VehicleBrand') == selected_brand)
    if selected_brand != 'ALL':
        raw_data_unit_sales_lytd = raw_data_unit_sales_lytd.filter(pl.col('VehicleBrand') == selected_brand)

    empty_sales = pl.DataFrame(
        schema={
            'SalesRegionCode': pl.Utf8,
            'AfterSalesRegionCode': pl.Utf8, 
            'KodeCompany': pl.Int64,
            'CompanyAbbreviation': pl.Utf8, 
            'NamaCompany': pl.Utf8, 
            'APMCompany': pl.Boolean, 
            'RegionName': pl.Utf8,
            'ModelDescription': pl.Utf8, 
            'VariantDescription': pl.Utf8,
            "ColourDescription": pl.Utf8,
            'UnitCategory': pl.Utf8, 
            'InvSysNo': pl.Int64,
            'InvLineNo': pl.Int64, 
            'TanggalInvoice': pl.Utf8, 
            'TanggalJatuhTempoInvoice': pl.Utf8,
            'NomorInvoice': pl.Utf8, 
            'TipeInvoice': pl.Utf8, 
            'TipeTransaksi': pl.Utf8, 
            'BillCode': pl.Utf8, 
            'TipeAR': pl.Utf8,
            'TanggalFPajak': pl.Utf8, 
            'NomorFPajak': pl.Utf8, 
            'CostCenter': pl.Utf8, 
            'ProfitCenter': pl.Utf8,
            'TipeDokReferensi': pl.Utf8, 
            'NomorDokReferensi': pl.Utf8, 
            'NomorSPM': pl.Utf8, 
            'NIKSales': pl.Utf8,
            'NamaSales': pl.Utf8, 
            'NIKSalesHead': pl.Utf8, 
            'NamaSalesHead': pl.Utf8, 
            'NIKKacab': pl.Utf8, 
            'NamaKacab': pl.Utf8,
            'STNKNama': pl.Utf8, 
            'STNKTanggalLahir': pl.Utf8, 
            'STNKMobilePhone': pl.Utf8, 
            'STNKIDType': pl.Utf8,
            'STNKIDNo': pl.Utf8, 
            'BillToKodeCustomer': pl.Utf8, 
            'BillToNama': pl.Utf8, 
            'BillToMobilePhone': pl.Utf8,
            'BillToTanggalLahir': pl.Utf8, 
            'BillToIDType': pl.Utf8, 
            'BillToIDNo': pl.Utf8, 
            'FundType': pl.Utf8,
            'FundTypeDescription': pl.Utf8, 
            'KodeSupplierLeasing': pl.Utf8,
            "LeasingSupplierName": pl.Utf8,
            'DPLeasing': pl.Int64,
            'TenorLeasing': pl.Int64, 
            'NomorChassis': pl.Utf8, 
            'NomorEngine': pl.Utf8, 
            'ItemGroup': pl.Utf8, 
            'KodeItem': pl.Utf8,
            'NamaItem': pl.Utf8, 
            'ItemLineType': pl.Utf8, 
            'JobType': pl.Utf8, 
            'Qty': pl.Int64, 
            'Price': pl.Int64, 
            'DiskonItem': pl.Int64,
            'COGSItem': pl.Int64, 
            'TotalCOGSItem': pl.Int64, 
            'MediatorFee': pl.Int64, 
            'OfftheroadAmount': pl.Int64,
            'DiscountAmount': pl.Int64, 
            'OfftheroadNetAmount': pl.Int64, 
            'BBNAmount': pl.Int64, 
            'PPNBM': pl.Int64,
            'PPh22Amount': pl.Int64,
            'COGSUnit': pl.Int64, 
            'COGSAccessories': pl.Int64, 
            'COGSTransport': pl.Int64, 
            'Total': pl.Int64,
            'TotalDP': pl.Int64, 
            'TotalVATDP': pl.Int64, 
            'TotalDPAfterVAT': pl.Int64, 
            'TotalDiscount': pl.Int64,
            'TotalAfterDiscount': pl.Float64, 
            'TotalVAT': pl.Int64, 
            'TotalAfterVAT': pl.Int64, 
            'ApmCustomerName': pl.Utf8, 
            'VehicleBrand': pl.Utf8,
        }
    )
   
    if raw_data_unit_sales.is_empty():
        raw_data_unit_sales = empty_sales
    if raw_data_unit_sales_lytd.is_empty():
        raw_data_unit_sales_lytd = empty_sales

    #Unit Sales
    st.markdown('<h2 class="section-title">Unit Performance</h2>',unsafe_allow_html=True)

    categories = ['Sales Volume Unit', 'Gross Profit Unit']

    raw_data_unit_sales = raw_data_unit_sales.with_columns(pl.col("TanggalInvoice").str.to_datetime())
    raw_data_unit_sales = raw_data_unit_sales.with_columns(pl.col("TanggalInvoice").dt.month().alias("PeriodMonth"))
    raw_data_unit_sales = raw_data_unit_sales.with_columns(pl.col("TanggalInvoice").dt.month().cast(pl.Utf8).str.zfill(2).alias("PeriodMonth"))

    raw_data_unit_sales_lytd = raw_data_unit_sales_lytd.with_columns(pl.col("TanggalInvoice").str.to_datetime())
    raw_data_unit_sales_lytd = raw_data_unit_sales_lytd.with_columns(pl.col("TanggalInvoice").dt.month().alias("PeriodMonth"))
    raw_data_unit_sales_lytd = raw_data_unit_sales_lytd.with_columns(pl.col("TanggalInvoice").dt.month().cast(pl.Utf8).str.zfill(2).alias("PeriodMonth"))

    #get last month
    month_int = int(selected_month)
    previous_month_int = (month_int - 1) if month_int > 1 else 12
    previous_month_str = f'{previous_month_int:02}'

    sales_volume_actual = raw_data_unit_sales.filter(pl.col('PeriodMonth').str.contains(selected_month))['Qty'].sum()
    sales_volume_last_month = raw_data_unit_sales.filter(pl.col('PeriodMonth').str.contains(previous_month_str))['Qty'].sum()

    sales_volume_ytd = raw_data_unit_sales.filter(pl.col('PeriodMonth') <= selected_month)['Qty'].sum()
    sales_volume_lytd = raw_data_unit_sales_lytd.filter(pl.col('PeriodMonth') <= selected_month)['Qty'].sum()

    max_range = max(sales_volume_actual, sales_volume_last_month, sales_volume_ytd, sales_volume_lytd)
    max_range = max_range + (max_range * 0.10)

    min_range = min(sales_volume_actual, sales_volume_last_month, sales_volume_ytd, sales_volume_lytd)
    min_range = min_range + (min_range * 0.10)
    
    col1, col2 = st.columns(2)
    with col1:
        actual = [sales_volume_actual]
        last_month = [sales_volume_last_month]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=actual,
            width=0.2,
            name='Actual',
            textposition='auto',
            text=str(actual[0]),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ))
        )
        fig.add_trace(go.Bar(
            x=categories,
            y=last_month,
            width=0.2,
            name='Last Month',
            textposition='auto',
            text=str(last_month[0]),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ))
        )
        fig.update_layout(
            barmode='group',
            bargap = 0.6,
            xaxis_title='',
            yaxis_title='Sales Volume',
            legend_title='',
            template='simple_white',
            yaxis_tickformat = '',
            title = 'Current Unit Sales',
            font = dict(size=15),
            yaxis=dict(tickfont=dict(size=15)),
            xaxis=dict(tickfont=dict(size=15)),
        )
        fig.update_yaxes(
            range=[min_range, max_range]
        )
        col1.plotly_chart(fig, use_container_width=True,key="Current Unit Sales")
    with col2:
        actual_YTD = [sales_volume_ytd]
        last_year_YTD = [sales_volume_lytd]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=actual_YTD,
            width=0.2,
            name='Actual YTD',
            textposition='auto',
            text=str(actual_YTD[0]),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ))
        )
        fig.add_trace(go.Bar(
            x=categories,
            y=last_year_YTD,
            width=0.2,
            name='Last Year',
            textposition='auto',
            text=str(last_year_YTD[0]),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ))
        )
        fig.update_layout(
            barmode='group',
            bargap = 0.6,
            xaxis_title='',
            yaxis_title='Sales Volume',
            legend_title='',
            template='simple_white',
            yaxis_tickformat = '',
            title = 'YTD Unit Sales',
            font = dict(size=15),
            yaxis=dict(tickfont=dict(size=15)),
            xaxis=dict(tickfont=dict(size=15))
        )
        fig.update_yaxes(
            range=[min_range, max_range]
        )
        col2.plotly_chart(fig, use_container_width=True,key="YTD Unit Sales")

    #Gross Profit Unit
    st.markdown('<h2 class="section-title">Gross Profit (Loss) - Unit</h2>',unsafe_allow_html=True)
    raw_data_income_statement_unit = raw_data_income_statement.filter(pl.col('ProfitCenter').str.contains('Car Sales'))
    gross_profit_unit = raw_data_income_statement_unit.filter(pl.col('Group1').is_in(['4', '5']))
    gross_profit_unit_actual = gross_profit_unit.filter(pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum()
    gross_profit_unit_prev = gross_profit_unit.filter(~pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum()

    if raw_data_income_budget.is_empty():
        empty_data_income_budget = pl.DataFrame(
            schema={
                'CompanyCode': pl.Int64,
                'CompanyName': pl.Utf8, 
                'CompanyAbbreviation': pl.Utf8, 
                'PeriodYear': pl.Utf8,
                'PeriodMonth': pl.Utf8, 
                'AccountNumber': pl.Utf8, 
                'AccountDescription': pl.Utf8, 
                'AccountType': pl.Utf8,
                'Group1': pl.Utf8, 
                'DebitAmount': pl.Int64, 
                'CreditAmount': pl.Int64, 
                'Brand': pl.Utf8, 
                'ProfitCenterCode': pl.Utf8,
                'ProfitCenter': pl.Utf8, 
                'CompanArGroupyCode': pl.Utf8,
            }
        )
        raw_data_income_budget = empty_data_income_budget
    raw_data_income_budget = raw_data_income_budget.with_columns(((pl.col("DebitAmount") - pl.col("CreditAmount")) * -1).alias('mutation'))

    income_budget_gross_profit_unit = raw_data_income_budget.filter(pl.col('Group1').is_in(['4', '5']))
    income_budget_gross_profit_unit = income_budget_gross_profit_unit.filter(pl.col('ProfitCenter').str.contains('Car Sales'))
    income_budget_gross_profit_unit = income_budget_gross_profit_unit.filter(pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum()
    if income_budget_gross_profit_unit != 0:
        percent_budget_gross_profit_unit = round(gross_profit_unit_actual / income_budget_gross_profit_unit * 100, 2)
    else:
        percent_budget_gross_profit_unit = 0
        
    gross_profit_unit_last_year = raw_data_income_statement_last_year.filter(pl.col('ProfitCenter').str.contains('Car Sales'))
    gross_profit_unit_last_year = gross_profit_unit_last_year.filter(pl.col('Group1').is_in(['4', '5']))
    gross_profit_unit_ytd = gross_profit_unit.filter(pl.col('PeriodMonth').str.contains(selected_month))['EndAmount'].sum()
    gross_profit_unit_prev_year = gross_profit_unit_last_year.filter(pl.col('PeriodMonth').str.contains(selected_month))['EndAmount'].sum()

    income_budget_gross_profit_unit_ytd = raw_data_income_budget.filter(pl.col('Group1').is_in(['4', '5']))
    income_budget_gross_profit_unit_ytd = income_budget_gross_profit_unit_ytd.filter(pl.col('ProfitCenter').str.contains('Car Sales'))
    income_budget_gross_profit_unit_ytd = income_budget_gross_profit_unit_ytd.filter(pl.col('PeriodMonth').is_in(month_to_proceed(selected_month)))['mutation'].sum()
    if income_budget_gross_profit_unit_ytd != 0:
        percent_budget_gross_profit_unit_ytd = round(gross_profit_unit_ytd / income_budget_gross_profit_unit_ytd * 100, 2)
    else:
        percent_budget_gross_profit_unit_ytd = 0

    max_range = max(gross_profit_unit_actual, gross_profit_unit_prev, gross_profit_unit_ytd, gross_profit_unit_prev_year)
    max_range = max_range + (max_range * 0.10)

    min_range = min(gross_profit_actual, gross_profit_unit_prev, gross_profit_unit_ytd, gross_profit_unit_prev_year)
    min_range = min_range + (min_range * 0.10)

    col1, col2, col3, col4, col5, col6 = st.columns((1,2,1,1,2,1))
    with col1:
        pass
    with col2:
        col2.metric('% Current Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_unit)}%")
        style_metric_cards()
    with col3:
        pass
    with col4:
        pass
    with col5:
        col5.metric('% YTD Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_unit_ytd)}%")
        style_metric_cards()
    with col6:
        pass

    categories = ["Gross Profit (Loss) Unit"]
    col1,col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=[gross_profit_unit_actual],
            name='Actual',
            textposition='auto',
            text=financial_format(gross_profit_unit_actual/1000000),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ),
            hovertemplate="<b>%{x}</b><br>Rp.%{text}")
        )
        fig.add_trace(go.Bar(
            x=categories,
            y=[income_budget_gross_profit_unit],
            name='Budget',
            textposition='auto',
            text=financial_format(income_budget_gross_profit_unit/1000000),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ),
            hovertemplate="<b>%{x}</b><br>Rp.%{text}")
        )
        fig.add_trace(go.Bar(
            x=categories,
            y=[gross_profit_unit_prev],
            name='Last Month',
            textposition='auto',
            text=financial_format(gross_profit_unit_prev/1000000),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ),
            hovertemplate="<b>%{x}</b><br>Rp.%{text}")
        )
        fig.update_layout(
            barmode='group',
            xaxis_title='',
            yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
            legend_title='',
            template='simple_white',
            yaxis_tickprefix = 'Rp. ', 
            yaxis_tickformat = '',
            title = 'Current Gross Profit (Loss) Unit (Rp. Million)',
            font = dict(size=15),
            yaxis=dict(tickfont=dict(size=15)),
            xaxis=dict(tickfont=dict(size=15))
        )
        fig.update_yaxes(
            range=[min_range, max_range]
        )
        col1.plotly_chart(fig,use_container_width=True,key="Current Gross Profit (Loss) Unit (Rp. Million)")

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories,
            y=[gross_profit_unit_ytd],
            name='Actual YTD',
            textposition='auto',
            text=financial_format(gross_profit_unit_ytd/1000000),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ),
            hovertemplate="<b>%{x}</b><br>Rp.%{text}")
        )
        fig.add_trace(go.Bar(
            x=categories,
            y=[income_budget_gross_profit_unit_ytd],
            name='Budget YTD',
            textposition='auto',
            text=financial_format(income_budget_gross_profit_unit_ytd/1000000),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ),
            hovertemplate="<b>%{x}</b><br>Rp.%{text}")
        )
        fig.add_trace(go.Bar(
            x=categories,
            y=[gross_profit_unit_prev_year],
            name='Last Year',
            textposition='auto',
            text=financial_format(gross_profit_unit_prev_year/1000000),
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ),
            hovertemplate="<b>%{x}</b><br>Rp.%{text}")
        )
        fig.update_layout(
            barmode='group',
            xaxis_title='',
            yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
            legend_title='',
            template='simple_white',
            yaxis_tickprefix = 'Rp. ', 
            yaxis_tickformat = '',
            title = 'YTD Gross Profit (Loss) Unit (Rp. Million)',
            font = dict(size=15),
            yaxis=dict(tickfont=dict(size=15)),
            xaxis=dict(tickfont=dict(size=15))
        )
        fig.update_yaxes(
            range=[min_range, max_range]
        )
        col2.plotly_chart(fig,use_container_width=True,key="YTD Gross Profit (Loss) Unit (Rp. Million)")