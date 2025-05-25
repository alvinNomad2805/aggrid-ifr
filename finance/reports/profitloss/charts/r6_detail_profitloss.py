import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.filter import financial_format

def detail_profitloss_profit_loss_statement(data_source_this_year, data_source_last_year, title, field, label=""):
    fig = go.Figure(data=[
        go.Bar(name=f'{title} of This Year', 
            y=np.abs(data_source_this_year[field]),
            x=data_source_this_year['Month'],
            text=[financial_format(np.abs(i/1000000)) for i in data_source_this_year[field]],
            textangle=-90,
            textposition='auto',
            hoverlabel=dict(
                    bgcolor="white",
                    font_size=15
            ),
            hovertemplate="<b>%{x}</b><br>Rp.%{y:,.2f}"),
        go.Bar(name=f'{title} of Last Year', 
            y=np.abs(data_source_last_year[field]),
            x=data_source_last_year['Month'],
            text=[financial_format(np.abs(i/1000000)) for i in data_source_last_year[field]],
            textangle=-90,
            textposition='auto',
            hoverlabel=dict(
                    bgcolor="white",
                    font_size=15
            ),
            hovertemplate="<b>%{x}</b><br>Rp.%{y:,.2f}")
    ])
    fig.update_layout(barmode='group', yaxis_tickprefix = 'Rp. ', yaxis_tickformat = '', height=600, uniformtext_minsize=15, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True,key=f"detail_profitloss_profit_loss_statement{label}")
