import streamlit as st
import math
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from reports.balancesheet.functions.currencyformat import finance_format
from utils.filter import financial_format
import numpy as np

def summary(raw_data):
    t1,t2,t3 = st.columns(3)
    with t1:
        raw_data_asset = raw_data[raw_data['AccountType'].str.contains('A')]
        raw_data_asset = (raw_data_asset['EndAmount'].sum())/1000000000
        t1.metric(label="Asset",value=f"Rp. {finance_format(raw_data_asset,'B')}")
        style_metric_cards()
    with t2:
        raw_data_liability = raw_data[raw_data['AccountType'].str.contains('L')]
        raw_data_liability = raw_data_liability['EndAmount'].sum()/1000000000
        t2.metric(label="Lialibility",value=f"Rp. {finance_format(raw_data_liability,'B')}")
        style_metric_cards()
    with t3:
        raw_data_equity = raw_data[raw_data['AccountType'].str.contains('E')]
        raw_data_equity = raw_data_equity['EndAmount'].sum()/1000000000
        t3.metric(label="Equity",value=f"Rp. {finance_format(raw_data_equity,'B')}")
        style_metric_cards
    

    st.divider()

    c1,c2 = st.columns(2)
    with c1:
        st.subheader("Top 10 Company Assets - Current")
        data_assets_current = raw_data[raw_data['Groupdesc2']=='11 - Current Assets']
        data_assets_amount_current = (data_assets_current[['CompanyName','CompanyCode','BeginAmount','EndAmount']]).groupby(by=["CompanyName"]).sum().reset_index()

        comp_assets = go.Figure()

        data_assets_amount_current = data_assets_amount_current.sort_values(by=['BeginAmount'],ascending=False).reset_index()
        comp_assets.add_trace(
            go.Bar(
                x = data_assets_amount_current['BeginAmount'][:10],
                y = data_assets_amount_current['CompanyName'][:10],
                orientation="h",
                marker=dict(color="blue"),
                name = "Begin Amount",
                text = finance_format(data_assets_amount_current['BeginAmount'][:20]/1000000,"M"),
                textposition = 'auto'
            )
        )

        comp_assets.add_trace(
            go.Bar(
                x = data_assets_amount_current['EndAmount'][:10],
                y = data_assets_amount_current['CompanyName'][:10],
                orientation="h",
                marker=dict(color="red"),
                name = "Ending Amount",
                text = finance_format(data_assets_amount_current['EndAmount'][:20]/1000000000,"B"),
                textposition = 'auto'
            )
        )

        comp_assets.update_layout(
            yaxis = dict(autorange='reversed'),
            yaxis_title = dict(text='Companies',font=dict(size=15)),
            xaxis_title = dict(text='Amount',font=dict(size=15)),
            height = 1200,
            font = dict(
                size = 14,
            ),
            showlegend=True,
        )

        st.plotly_chart(comp_assets,use_container_width=True, key='company_assets_current')
    
    with c2:
        st.subheader("Top 10 Company Assets - Non Current")
        data_assets_non_current = raw_data[raw_data['Groupdesc2'] == '12 - Non Current Assets']
        data_assets_amount_non_current = (data_assets_non_current[['CompanyName','CompanyCode','BeginAmount','EndAmount']]).groupby(by=["CompanyName"]).sum().reset_index()

        comp_assets_non = go.Figure()

        data_assets_amount_non_current = data_assets_amount_non_current.sort_values(by=['BeginAmount'],ascending=False).reset_index()
        comp_assets_non.add_trace(
            go.Bar(
                x = data_assets_amount_non_current['BeginAmount'][:10],
                y = data_assets_amount_non_current['CompanyName'][:10],
                orientation="h",
                marker=dict(color="blue"),
                name = "Begin Amount",
                text = finance_format(data_assets_amount_non_current['BeginAmount'][:20]/1000000000,"B"),
                textposition = 'auto'
            )
        )

        comp_assets_non.add_trace(
            go.Bar(
                x = data_assets_amount_non_current['EndAmount'][:10],
                y = data_assets_amount_non_current['CompanyName'][:10],
                orientation="h",
                marker=dict(color="red"),
                name = "Ending Amount",
                text = finance_format(data_assets_amount_non_current['EndAmount'][:20]/1000000000,"B"),
                textposition = 'auto'
            )
        )

        comp_assets_non.update_layout(
            yaxis = dict(autorange='reversed'),
            yaxis_title = dict(text='Companies',font=dict(size=15)),
            xaxis_title = dict(text='Amount',font=dict(size=15)),
            height = 1200,
            font = dict(
                size = 14,
            ),
            showlegend=True,
        )

        st.plotly_chart(comp_assets_non,use_container_width=True, key='company_assets_non_current')
    
    st.divider()
    
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("Top 10 Company Liabilities - Current")
        data_liabilities_current = raw_data[raw_data['Groupdesc2']=='21 - Current Liabilities']
        data_liabiities_amount_current = (data_liabilities_current[['CompanyName','CompanyCode','BeginAmount','EndAmount']]).groupby(by=["CompanyName"]).sum().reset_index()
        data_liabilities_amount_current = data_liabiities_amount_current.sort_values(by=['BeginAmount'],ascending=False).reset_index()

        comp_assets = go.Figure()
        comp_assets.add_trace(
            go.Bar(
                x = data_liabilities_amount_current['BeginAmount'][:10],
                y = data_liabilities_amount_current['CompanyName'][:10],
                orientation="h",
                marker=dict(color="blue"),
                name = "Begin Amount",
                text = finance_format(data_liabilities_amount_current['BeginAmount'][:20]/1000000,"M"),
                textposition = 'auto'
            )
        )

        comp_assets.add_trace(
            go.Bar(
                x = data_liabilities_amount_current['EndAmount'][:10],
                y = data_liabilities_amount_current['CompanyName'][:10],
                orientation="h",
                marker=dict(color="red"),
                name = "Ending Amount",
                text = finance_format(data_liabilities_amount_current['EndAmount'][:20]/1000000000,"B"),
                textposition = 'auto'
            )
        )

        comp_assets.update_layout(
            # yaxis = dict(autorange='reversed'),
            yaxis_title = dict(text='Companies',font=dict(size=15)),
            xaxis_title = dict(text='Amount',font=dict(size=15)),
            height = 1200,
            font = dict(
                size = 14,
            ),
            showlegend=True,
        )

        st.plotly_chart(comp_assets,use_container_width=True, key='company_liabilities_current')
    
    st.divider()


    with c2:
        st.subheader("Top 10 Company Liabilities - Non Current")
        data_liabilities_non_current = raw_data[raw_data['Groupdesc2'] == '22 - Non-current Liabilities']
        data_liabilities_amount_non_current = (data_liabilities_non_current[['CompanyName','CompanyCode','BeginAmount','EndAmount']]).groupby(by=["CompanyName"]).sum().reset_index()
        data_liabilities_amount_non_current = data_liabilities_amount_non_current.sort_values(by=['BeginAmount'],ascending=False).reset_index()

        
        comp_assets_non = go.Figure()
        comp_assets_non.add_trace(
            go.Bar(
                x = data_liabilities_amount_non_current['BeginAmount'][:10],
                y = data_liabilities_amount_non_current['CompanyName'][:10],
                orientation="h",
                marker=dict(color="blue"),
                name = "Begin Amount",
                text = finance_format(data_liabilities_amount_non_current['BeginAmount'][:20]/1000000000,"B"),
                textposition = 'auto'
            )
        )

        comp_assets_non.add_trace(
            go.Bar(
                x = data_liabilities_amount_non_current['EndAmount'][:10],
                y = data_liabilities_amount_non_current['CompanyName'][:10],
                orientation="h",
                marker=dict(color="red"),
                name = "Ending Amount",
                text = finance_format(data_liabilities_amount_non_current['EndAmount'][:20]/1000000000,"B"),
                textposition = 'auto'
            )
        )

        comp_assets_non.update_layout(
            # yaxis = dict(autorange='reversed'),
            yaxis_title = dict(text='Companies',font=dict(size=15)),
            xaxis_title = dict(text='Amount',font=dict(size=15)),
            height = 1200,
            font = dict(
                size = 14,
            ),
            showlegend=True,
        )

        st.plotly_chart(comp_assets_non,use_container_width=True, key='company_liabilities_non_current')

    st.subheader("Top 10 Company Capital End Amount")

    print('check capital')
    print(raw_data.head)
    capital_data = (raw_data[(raw_data['AccountNumber2'] == '3110') | (raw_data['AccountNumber2'] == '3210') | (raw_data['AccountNumber2'] == '3520')]).copy()
    
    capital_data = capital_data[['CompanyName','EndAmount']]
    capital_data_amount = (capital_data.groupby(by=['CompanyName']).sum()).reset_index()
    capital_data_amount = capital_data_amount.sort_values(by=['EndAmount'],ascending=True).reset_index()
    
    capital_fig = go.Figure()

    capital_fig.add_trace(
        go.Bar(
            x = -1 * capital_data_amount['EndAmount'][:10],
            y = capital_data_amount['CompanyName'][:10],
            orientation="h",
            marker=dict(color="blue"),
            name = "Capital End Amount",
            text = finance_format(capital_data_amount['EndAmount'][:10]/1000000000,"B"),
            textposition = 'auto'
        )
    )


    capital_fig.update_layout(
        yaxis = dict(autorange='reversed'),
        yaxis_title = dict(text='Companies',font=dict(size=15)),
        xaxis_title = dict(text='End Amount',font=dict(size=15)),
        height = 800,
        font = dict(
            size = 14,
        )  
    )

    st.plotly_chart(capital_fig,use_container_width=True, key='company_capital_end_amount')