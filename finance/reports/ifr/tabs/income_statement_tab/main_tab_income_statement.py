import polars as pl
import streamlit as st
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go
from utils.filter import financial_format

def income_statement(raw_data_income_statement,
                    raw_data_income_statement_last_year,
                    raw_data_income_budget,
                    raw_data_income_budget_last_year,
                    selected_month,
                    selected_brand):

    raw_data_income_statement = raw_data_income_statement.with_columns(((pl.col("DebitAmount") - pl.col("CreditAmount")) * -1).alias("mutation"))
    raw_data_income_statement_last_year = raw_data_income_statement_last_year.with_columns(((pl.col("DebitAmount") - pl.col("CreditAmount")) * -1).alias("mutation"))
    raw_data_income_budget = raw_data_income_budget.with_columns(((pl.col("DebitAmount") - pl.col("CreditAmount")) * -1).alias("mutation"))
    raw_data_income_budget_last_year = raw_data_income_budget_last_year.with_columns(((pl.col("DebitAmount") - pl.col("CreditAmount")) * -1).alias("mutation"))
    
    categories = ['Gross Profit (Loss)', 'OPEX', 'Operational Profit (Loss)']
    
    raw_data_income_statement = raw_data_income_statement.filter(pl.col('Brand') == selected_brand) if selected_brand != 'ALL' else raw_data_income_statement
    raw_data_income_statement_last_year = raw_data_income_statement_last_year.filter(pl.col('Brand') == selected_brand) if selected_brand != 'ALL' else raw_data_income_statement_last_year
    raw_data_income_budget = raw_data_income_budget.filter(pl.col('Brand') == selected_brand) if selected_brand != 'ALL' else raw_data_income_budget
    raw_data_income_budget_last_year = raw_data_income_budget_last_year.filter(pl.col('Brand') == selected_brand) if selected_brand != 'ALL' else raw_data_income_budget_last_year 

    #current
    gross_profit = raw_data_income_statement.filter(pl.col('Group1').is_in(['4', '5']))
    gross_profit_actual = gross_profit.filter(pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum()

    gross_profit_last_month = gross_profit.filter(~pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum()

    opex = raw_data_income_statement.filter(pl.col('Group1').is_in(['6']))
    opex_actual = np.abs(opex.filter(pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum())
    opex_last_month = np.abs(opex.filter(~pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum())

    operational_profit_actual = gross_profit_actual - opex_actual
    operational_profit_last_month = gross_profit_last_month - opex_last_month

    income_budget_gross_profit = raw_data_income_budget.filter(pl.col('Group1').is_in(['4', '5']))
    income_budget_gross_profit_actual = income_budget_gross_profit.filter(pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum()

    income_budget_opex = raw_data_income_budget.filter(pl.col('Group1').is_in(['6']))
    income_budget_opex_actual = np.abs(income_budget_opex.filter(pl.col('PeriodMonth').str.contains(selected_month))['mutation'].sum())

    income_budget_operational_profit_actual = income_budget_gross_profit_actual - income_budget_opex_actual

    if income_budget_gross_profit_actual != 0:
        percent_budget_gross_profit = round(gross_profit_actual / income_budget_gross_profit_actual * 100, 2)
    else:
        percent_budget_gross_profit = 0
    if income_budget_opex_actual != 0:
        percent_budget_opex = round(opex_actual / income_budget_opex_actual * 100, 2)
    else: 
        percent_budget_opex = 0
    if income_budget_operational_profit_actual != 0:
        percent_budget_operational = round(operational_profit_actual / income_budget_operational_profit_actual * 100, 2)
    else:
        percent_budget_operational = 0

    #YTD
    gross_profit_last_year = raw_data_income_statement_last_year.filter(pl.col('Group1').is_in(['4', '5']))
    gross_profit_actual_YTD = gross_profit.filter(pl.col('PeriodMonth').str.contains(selected_month))['EndAmount'].sum()
    gross_profit_last_year_YTD = gross_profit_last_year.filter(pl.col('PeriodMonth').str.contains(selected_month))['EndAmount'].sum()

    opex_last_year = raw_data_income_statement_last_year.filter(pl.col('Group1').is_in(['6']))
    opex_actual_YTD = np.abs(opex.filter(pl.col('PeriodMonth').str.contains(selected_month))['EndAmount'].sum())
    opex_last_year_YTD = np.abs(opex_last_year.filter(~pl.col('PeriodMonth').str.contains(selected_month))['EndAmount'].sum())

    operational_profit_actual_YTD = gross_profit_actual_YTD - opex_actual_YTD
    operational_profit_last_year_YTD = gross_profit_last_year_YTD - opex_last_year_YTD

    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    index_selected = month_list.index(selected_month)
    month_to_proceed = month_list[:index_selected+1]

    income_budget_gross_profit_ytd = income_budget_gross_profit.filter(pl.col('PeriodMonth').is_in(month_to_proceed))['mutation'].sum()
    income_budget_opex_ytd = np.abs(income_budget_opex.filter(pl.col('PeriodMonth').is_in(month_to_proceed))['mutation'].sum())
    income_budget_operational_profit_ytd = income_budget_gross_profit_ytd - income_budget_opex_ytd

    if income_budget_gross_profit_ytd != 0:
        percent_budget_gross_profit_ytd = round(gross_profit_actual_YTD / income_budget_gross_profit_ytd * 100, 2)
    else:
        percent_budget_gross_profit_ytd = 0
    if income_budget_opex_ytd != 0:
        percent_budget_opex_ytd = round(opex_actual_YTD / income_budget_opex_ytd * 100, 2)
    else:
        percent_budget_opex_ytd = 0
    if income_budget_operational_profit_ytd != 0:
        percent_budget_operational_ytd = round(operational_profit_actual_YTD / income_budget_operational_profit_ytd * 100, 2)
    else:
        percent_budget_operational_ytd = 0

    max_range = max(gross_profit_actual, opex_actual, operational_profit_actual, gross_profit_last_month, opex_last_month, operational_profit_last_month,
                    gross_profit_actual_YTD, opex_actual_YTD, operational_profit_actual_YTD, gross_profit_last_year_YTD, opex_last_year_YTD, operational_profit_last_year_YTD)
    max_range = max_range + (max_range * 0.10)

    min_range = min(gross_profit_actual, opex_actual, operational_profit_actual, gross_profit_last_month, opex_last_month, operational_profit_last_month,
                    gross_profit_actual_YTD, opex_actual_YTD, operational_profit_actual_YTD, gross_profit_last_year_YTD, opex_last_year_YTD, operational_profit_last_year_YTD)
    min_range = min_range + (min_range * 0.10)

    st.markdown('<h2 class="section-title">Current Profit (Loss)</h2>',unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns((1,2,2,2,1))
    with col1:
        pass
    with col2:
        col2.metric('% Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit)}%")
        style_metric_cards()
    with col3:
        col3.metric('% OPEX Budget',value=f"{financial_format(percent_budget_opex)}%")
        style_metric_cards()
    with col4:
        col4.metric('% Operational Profit (Loss) Budget',value=f"{financial_format(percent_budget_operational)}%")
        style_metric_cards()
    with col5:
        pass

    actual = [gross_profit_actual, opex_actual, operational_profit_actual]
    last_month = [gross_profit_last_month, opex_last_month, operational_profit_last_month]
    budget = [income_budget_gross_profit_actual, income_budget_opex_actual, income_budget_operational_profit_actual]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
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
        x=categories,
        y=budget,
        name='Budget',
        textposition='auto',
        text=[financial_format(i/1000000) for i in budget],
        hoverlabel=dict(
            bgcolor="white",
            font_size=15
        ),
        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
    )
    fig.add_trace(go.Bar(
        x=categories,
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
        yaxis_title='Profit (Loss) Amount (Rp. Million)',
        legend_title='',
        template='simple_white',
        yaxis_tickprefix = 'Rp. ', 
        yaxis_tickformat = '',
        title = 'Current Profit (Loss) (Rp. Million)',
        font = dict(size=15),
        yaxis=dict(tickfont=dict(size=15)),
        xaxis=dict(tickfont=dict(size=15))
    )
    fig.update_yaxes(
        # range=[min_range, max_range],
        showgrid=True
    )
    st.plotly_chart(fig, use_container_width=True,key="Current Profit (Loss) (Rp. Million)")
    
    st.markdown('<h2 class="section-title">YTD Profit (Loss)</h2>',unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns((1,2,2,2,1))
    with col1:
        pass
    with col2:
        col2.metric('% Gross Profit (Loss) Budget YTD',value=f"{financial_format(percent_budget_gross_profit_ytd)}%")
        style_metric_cards()
    with col3:
        col3.metric('% OPEX Budget YTD',value=f"{financial_format(percent_budget_opex_ytd)}%")
        style_metric_cards()
    with col4:
        col4.metric('% Operational Profit (Loss) Budget YTD',value=f"{financial_format(percent_budget_operational_ytd)}%")
        style_metric_cards()
    with col5:
        pass

    actual_YTD = [gross_profit_actual_YTD, opex_actual_YTD, operational_profit_actual_YTD]
    last_year_YTD = [gross_profit_last_year_YTD, opex_last_year_YTD, operational_profit_last_year_YTD]
    budget_YTD = [income_budget_gross_profit_ytd, income_budget_opex_ytd, income_budget_operational_profit_ytd]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=actual_YTD,
        name='Actual',
        textposition='auto',
        text=[financial_format(i/1000000) for i in actual_YTD],
        hoverlabel=dict(
            bgcolor="white",
            font_size=15
        ),
        hovertemplate="<b>%{x}</b><br>Rp.%{y:,.2f}")
    )
    fig.add_trace(go.Bar(
        x=categories,
        y=budget_YTD,
        name='Budget',
        textposition='auto',
        text=[financial_format(i/1000000) for i in budget_YTD],
        hoverlabel=dict(
            bgcolor="white",
            font_size=15
        ),
        hovertemplate="<b>%{x}</b><br>Rp.%{y:,.2f}")
    )
    fig.add_trace(go.Bar(
        x=categories,
        y=last_year_YTD,
        name='Last Year',
        textposition='auto',
        text=[financial_format(i/1000000) for i in last_year_YTD],
        hoverlabel=dict(
            bgcolor="white",
            font_size=15
        ),
        hovertemplate="<b>%{x}</b><br>Rp.%{y:,.2f}")
    )
    fig.update_layout(
        barmode='group',
        xaxis_title='',
        yaxis_title='Profit (Loss) Amount (Rp. Million)',
        legend_title='',
        template='simple_white',
        yaxis_tickprefix = 'Rp. ', 
        yaxis_tickformat = '',
        title = 'YTD Profit (Loss) (Rp. Million)',
        font = dict(size=15),
        yaxis=dict(tickfont=dict(size=15)),
        xaxis=dict(tickfont=dict(size=15))
    )
    fig.update_yaxes(
        # range=[min_range, max_range],
        showgrid=True
    )
    st.plotly_chart(fig, use_container_width=True,key="YTD Profit (Loss) (Rp. Million)")