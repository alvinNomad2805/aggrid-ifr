import streamlit as st
import pandas as pd
from utils.alvinmelt import melt
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from utils.filter import financial_format

def chart_summary(data_source_filtered_time, data_source_filtered):
    #region : applying group by in data source
    raw_data = data_source_filtered_time.groupby(['ConsolidationName',
                                                'CompanyName',
                                                'AccountDescription',
                                                'AccountTypeDescription']).agg({'BeginAmount':'sum',
                                                                                'DebitAmount':'sum',
                                                                                'CreditAmount':'sum',
                                                                                'EndingAmount':'sum'})
    #endregion
    
    #region : metrics
    c1,c2,c3,c4 = st.columns(4)
    sumofbeginamount = int(raw_data['BeginAmount'].sum())
    sumofendingamount = int(raw_data['EndingAmount'].sum())
    sumofdebitamount = int(raw_data['DebitAmount'].sum())
    sumofcreditamount = int(raw_data['CreditAmount'].sum())
    with c1:
        st.metric('Sum of Begin Amount', value=financial_format(sumofbeginamount))
        style_metric_cards()
    with c2:
        st.metric('Sum of Debit Amount', value=financial_format(sumofdebitamount))
        style_metric_cards()
    with c3:
        st.metric('Sum of Credit Amount', value=financial_format(sumofcreditamount))
        style_metric_cards()
    with c4:
        st.metric('Sum of Ending Amount',value=financial_format(sumofendingamount))
        style_metric_cards()
    #endregion

    #region : balance trend line
    trend_data = data_source_filtered.groupby(['PeriodYear','PeriodMonth'])[['BeginAmount', 'DebitAmount','CreditAmount', 'EndingAmount']].sum().reset_index()
    st.subheader(f"Balances Trend Line in {trend_data.at[0, 'PeriodYear']}")
    trace1 = go.Scatter(x=trend_data['PeriodMonth'], 
                        y=trend_data['CreditAmount'], 
                        mode='lines+markers', name='Credit Amount', 
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>Period Month: %{x}</b><br>Rp.%{y:,d}",)
    trace2 = go.Scatter(x=trend_data['PeriodMonth'], 
                        y=trend_data['DebitAmount'], 
                        mode='lines+markers', name='Debit Amount',
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>Period Month: %{x}</b><br>Rp.%{y:,d}",)

    fig = go.Figure()
    fig.add_trace(trace1)
    fig.add_trace(trace2)

    fig.update_layout(xaxis_title='Period Month', yaxis_title='Total Amount')
    fig.update_layout(yaxis_tickprefix = 'Rp. ', yaxis_tickformat = '')
    
    st.plotly_chart(fig, use_container_width=True)
    #endregion

    #region : proportion of account type amount pie chart and top 10 bar chart
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Total Debit Amount by Account Type")
        chart_raw_data = raw_data.groupby('AccountTypeDescription')['DebitAmount'].sum().reset_index().sort_values('DebitAmount', ascending=True)
        fig = go.Figure(go.Pie(labels=chart_raw_data['AccountTypeDescription'].tolist(), values=chart_raw_data['DebitAmount'].tolist()))
        fig.update_traces(textinfo='percent', textfont_size=20,
                                hovertemplate="<b>%{label}:</b> Rp.%{value:,d}", textposition='auto',
                                hoverlabel=dict(
                                        bgcolor="white",
                                        font_size=15
                                )).update_layout(height=370, margin=dict(t=50,b=50,l=0,r=0))
        fig.update_traces(textposition='auto')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader('Top 10 Account with Highest Debit Balance')
        chart_raw_data = raw_data.groupby('AccountDescription')['DebitAmount'].sum().reset_index().sort_values('DebitAmount', ascending=False)[:10]
        chart_raw_data = chart_raw_data.sort_values('DebitAmount', ascending=True)
        fig = go.Figure(go.Bar(
                x=chart_raw_data['DebitAmount'],
                y=chart_raw_data['AccountDescription'],
                orientation='h',
                text=chart_raw_data['DebitAmount'],
                texttemplate="Rp.%{x:,d}",
                textposition='auto',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=15
                ),
                hovertemplate="<b>%{y}</b><br>Rp.%{x:,d}",
                name=""))
        fig.update_layout(xaxis_tickprefix = 'Rp. ', xaxis_tickformat = '')
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Total Credit Amount by Account Type")
        chart_raw_data = raw_data.groupby('AccountTypeDescription')['CreditAmount'].sum().reset_index().sort_values('CreditAmount', ascending=True)
        fig = go.Figure(go.Pie(labels=chart_raw_data['AccountTypeDescription'].tolist(), values=chart_raw_data['CreditAmount'].tolist()))
        fig.update_traces(textinfo='percent', textfont_size=20,
                                hovertemplate="<b>%{label}:</b> Rp.%{value:,d}", textposition='auto',
                                hoverlabel=dict(
                                        bgcolor="white",
                                        font_size=15
                                )).update_layout(height=370, margin=dict(t=50,b=50,l=0,r=0))
        fig.update_traces(textposition='auto')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader('Top 10 Account with Highest Credit Balance')
        chart_raw_data = raw_data.groupby('AccountDescription')['CreditAmount'].sum().reset_index().sort_values('CreditAmount', ascending=False)[:10]
        chart_raw_data = chart_raw_data.sort_values('CreditAmount', ascending=True)
        fig = go.Figure(go.Bar(
                x=chart_raw_data['CreditAmount'],
                y=chart_raw_data['AccountDescription'],
                orientation='h',
                text=chart_raw_data['CreditAmount'],
                texttemplate="Rp.%{x:,d}",
                textposition='auto',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=15
                ),
                hovertemplate="<b>%{y}</b><br>Rp.%{x:,d}",
                name=""))
        fig.update_layout(xaxis_tickprefix = 'Rp. ', xaxis_tickformat = '')
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)
    #endregion