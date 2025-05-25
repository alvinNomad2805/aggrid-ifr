import streamlit as st
import plotly.graph_objects as go
from utils.filter import financial_format

def summary_profitloss_netprofit_year_bar(data_source_this_year, data_source_last_year):
    data_source_this_year = data_source_this_year.assign(net_profit_text = data_source_this_year['net_profit']/1000000)
    data_source_this_year["net_profit_text"] =  data_source_this_year["net_profit_text"].apply(financial_format)

    data_source_last_year = data_source_last_year.assign(net_profit_text = data_source_last_year['net_profit']/1000000)
    data_source_last_year["net_profit_text"] =  data_source_last_year["net_profit_text"].apply(financial_format)

    fig = go.Figure(data=[
        go.Bar(name='Net Profit of This Year', 
                y=data_source_this_year['net_profit'],
                x=data_source_this_year['Month'],
                text=data_source_this_year['net_profit_text'],
                textangle=-90,
                textposition='auto',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=20
                ),
                hovertemplate="<b>%{x}</b><br>Rp.%{text}"),
        go.Bar(name='Net Profit of Last Year', 
                y=data_source_last_year['net_profit'],
                x=data_source_last_year['Month'],
                text=data_source_last_year['net_profit_text'],
                textangle=-90,
                textposition='auto',
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=20
                ),
                hovertemplate="<b>%{x}</b><br>Rp.%{text}")
    ])
    fig.update_layout(barmode='group', yaxis_tickprefix = 'Rp. ', yaxis_tickformat = '', height=550, uniformtext_minsize=15, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)