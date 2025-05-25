from utils.caching import parquet_by_monthly
import streamlit as st
# import pandas as pd
import polars as pl
import plotly.graph_objects as go
from utils.filter import financial_format

def main_tab_cash_flow_management(selected_month,
                                  selected_year,
                                  selected_company,
                                  selected_brand):
    empty_data_ar_aging_overdue = pl.DataFrame(schema={
        'CompanyCode' : pl.Int64,
        'CompanyName' : pl.Utf8,
        'CompanyAbbreviation' : pl.Utf8,
        'ProfitCenterCode' : pl.Utf8,
        'ProfitCenter' : pl.Utf8,
        'Brand' : pl.Utf8,
        'PeriodYear' : pl.Utf8,
        'PeriodMonth' : pl.Utf8,
        'Aging2BaseAmount' : pl.Float64,
        'Aging3BaseAmount' : pl.Float64,
        'Aging4BaseAmount' : pl.Float64,
    })

    empty_data_ap_aging_overdue = pl.DataFrame(schema={
        'CompanyCode' : pl.Int64,
        'CompanyName' : pl.Utf8,
        'CompanyAbbreviation' : pl.Utf8,
        'ProfitCenterCode' : pl.Utf8,
        'ProfitCenter' : pl.Utf8,
        'Brand' : pl.Utf8,
        'PeriodYear' : pl.Utf8,
        'PeriodMonth' : pl.Utf8,
        'Aging2Amount' : pl.Float64,
        'Aging3Amount' : pl.Float64,
        'Aging4Amount' : pl.Float64,
    })

    #AR Overdue
    raw_data_ar_aging_overdue = parquet_by_monthly(selected_year, selected_month, 
                                                    f"reports/ifr/parquet/ifr-ar-aging-overdue_{selected_year}_{selected_month}_{selected_company}.parquet",
                                                    f"/ifr-ar-aging-overdue?period_year={selected_year}&period_month={selected_month}&company_name={selected_company}")
    if raw_data_ar_aging_overdue.is_empty():
        raw_data_ar_aging_overdue = empty_data_ar_aging_overdue
    if selected_brand != 'ALL':
        raw_data_ar_aging_overdue = raw_data_ar_aging_overdue.filter(pl.col('Brand') == selected_brand)
    
    categories_ar = ['AR Overdue > 30 days - Unit', 'AR Overdue > 30 days - Workshop', 'AR Overdue > 30 days - Body Repair']
    raw_data_ar_aging_overdue = raw_data_ar_aging_overdue.with_columns(['Aging2BaseAmount', 'Aging3BaseAmount', 'Aging4BaseAmount']).fill_null(0)
    raw_data_ar_aging_overdue = raw_data_ar_aging_overdue.with_columns((pl.col('Aging2BaseAmount') +  
                                                                        pl.col('Aging3BaseAmount') + 
                                                                        pl.col('Aging4BaseAmount')).alias('OverdueAmount'))

    unit_actual_ar = raw_data_ar_aging_overdue.filter((pl.col('ProfitCenterCode') == '00001') &
                                                (pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    workshop_actual_ar = raw_data_ar_aging_overdue.filter((pl.col('ProfitCenterCode') == '00002') &
                                                    (pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    body_repair_actual_ar = raw_data_ar_aging_overdue.filter((pl.col('ProfitCenterCode') == '00003') &
                                                        (pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    unit_actual_last_month_ar = raw_data_ar_aging_overdue.filter((pl.col('ProfitCenterCode') == '00001') &
                                                            ~(pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    workshop_actual_last_month_ar = raw_data_ar_aging_overdue.filter((pl.col('ProfitCenterCode') == '00002') &
                                                                ~(pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    body_repair_actual_last_month_ar = raw_data_ar_aging_overdue.filter((pl.col('ProfitCenterCode') == '00003') &
                                                                ~(pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    

    # empty_data_ap_aging_overdue = pl.DataFrame(
    #     columns=['CompanyCode', 'CompanyName', 'CompanyAbbreviation', 'ProfitCenterCode',
    #     'ProfitCenter', 'Brand', 'PeriodYear', 'PeriodMonth',
    #     'Aging2Amount', 'Aging3Amount', 'Aging4Amount']
    #     )
    
    #AP Overdue
    raw_data_ap_aging_overdue = parquet_by_monthly(selected_year, selected_month, 
                                                    f"reports/ifr/parquet/ifr-ap-aging-overdue_{selected_year}_{selected_month}_{selected_company}.parquet",
                                                    f"/ifr-ap-aging-overdue?period_year={str(selected_year)}&period_month={selected_month}&company_name={selected_company}")
    if raw_data_ap_aging_overdue.is_empty():
        raw_data_ap_aging_overdue = empty_data_ap_aging_overdue
    if selected_brand != 'ALL':
        raw_data_ap_aging_overdue = raw_data_ap_aging_overdue.filter(pl.col('Brand') == selected_brand)
    categories_ap = ['AP Overdue > 30 days - Unit', 'AP Overdue > 30 days - Workshop', 'AP Overdue > 30 days - Body Repair']
    raw_data_ap_aging_overdue = raw_data_ap_aging_overdue.with_columns(['Aging2Amount', 'Aging3Amount', 'Aging4Amount']).fill_null(0)
    raw_data_ap_aging_overdue = raw_data_ap_aging_overdue.with_columns((pl.col('Aging2Amount') + 
                                                                        pl.col('Aging3Amount') + 
                                                                        pl.col('Aging4Amount')).alias('OverdueAmount'))

    unit_actual_ap = raw_data_ap_aging_overdue.filter((pl.col('ProfitCenterCode') == '00001') &
                                                (pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    workshop_actual_ap = raw_data_ap_aging_overdue.filter((pl.col('ProfitCenterCode') == '00002') &
                                                    (pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    body_repair_actual_ap = raw_data_ap_aging_overdue.filter((pl.col('ProfitCenterCode') == '00003') &
                                                        (pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    unit_actual_last_month_ap = raw_data_ap_aging_overdue.filter((pl.col('ProfitCenterCode') == '00001') &
                                                            ~(pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    workshop_actual_last_month_ap = raw_data_ap_aging_overdue.filter((pl.col('ProfitCenterCode') == '00002') &
                                                                ~(pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    body_repair_actual_last_month_ap = raw_data_ap_aging_overdue.filter((pl.col('ProfitCenterCode') == '00003') &
                                                                ~(pl.col('PeriodMonth').str.contains(selected_month)))['OverdueAmount'].sum()
    
    max_range = max(unit_actual_ar, workshop_actual_ar, body_repair_actual_ar, unit_actual_last_month_ar, workshop_actual_last_month_ar, body_repair_actual_last_month_ar,
                    unit_actual_ap, workshop_actual_ap, body_repair_actual_ap, unit_actual_last_month_ap, workshop_actual_last_month_ap, body_repair_actual_last_month_ap)
    max_range = max_range + (max_range * 0.10)

    min_range = min(unit_actual_ar, workshop_actual_ar, body_repair_actual_ar, unit_actual_last_month_ar, workshop_actual_last_month_ar, body_repair_actual_last_month_ar,
                    unit_actual_ap, workshop_actual_ap, body_repair_actual_ap, unit_actual_last_month_ap, workshop_actual_last_month_ap, body_repair_actual_last_month_ap)
    min_range = min_range + (min_range * 0.10)

    st.markdown('<h2 class="section-title">Account Receivable</h2>',unsafe_allow_html=True)
    actual = [unit_actual_ar, workshop_actual_ar, body_repair_actual_ar]
    last_month = [unit_actual_last_month_ar, workshop_actual_last_month_ar, body_repair_actual_last_month_ar]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories_ar,
        y=actual,
        name='Actual',
        textposition='auto',
        text=[financial_format(i/1000000) for i in actual],
        hoverlabel=dict(
            bgcolor="white",
            font_size=15
        ),
        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
    )
    fig.add_trace(go.Bar(
        x=categories_ar,
        y=last_month,
        name='Last Month',
        textposition='auto',
        text=[financial_format(i/1000000) for i in last_month],
        hoverlabel=dict(
            bgcolor="white",
            font_size=15
        ),
        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
    )
    fig.update_layout(
        barmode='group',
        xaxis_title='',
        yaxis_title='AR Amount (Rp. Million)',
        legend_title='',
        template='simple_white',
        yaxis_tickprefix = 'Rp. ', 
        yaxis_tickformat = '',
        font = dict(size=15),
        yaxis=dict(tickfont=dict(size=15)),
        xaxis=dict(tickfont=dict(size=15))
    )
    fig.update_yaxes(
        range=[min_range, max_range]
    )
    st.plotly_chart(fig, use_container_width=True,key="chart_1")
    
    st.markdown('<h2 class="section-title">Account Payable</h2>',unsafe_allow_html=True)
    actual = [unit_actual_ap, workshop_actual_ap, body_repair_actual_ap]
    last_month = [unit_actual_last_month_ap, workshop_actual_last_month_ap, body_repair_actual_last_month_ap]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories_ap,
        y=actual,
        name='Actual',
        textposition='auto',
        text=[financial_format(i/1000000) for i in actual],
        hoverlabel=dict(
            bgcolor="white",
            font_size=15
        ),
        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
    )
    fig.add_trace(go.Bar(
        x=categories_ap,
        y=last_month,
        name='Last Month',
        textposition='auto',
        text=[financial_format(i/1000000) for i in last_month],
        hoverlabel=dict(
            bgcolor="white",
            font_size=15
        ),
        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
    )
    fig.update_layout(
        barmode='group',
        xaxis_title='',
        yaxis_title='AP Amount (Rp. Million)',
        legend_title='',
        template='simple_white',
        yaxis_tickprefix = 'Rp. ', 
        yaxis_tickformat = '',
        font = dict(size=15),
        yaxis=dict(tickfont=dict(size=15)),
        xaxis=dict(tickfont=dict(size=15))
    )
    fig.update_yaxes(
        range=[min_range, max_range]
    )
    st.plotly_chart(fig, use_container_width=True,key="chart_2")