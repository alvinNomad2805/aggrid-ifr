import streamlit as st
import plotly.graph_objects as go
from utils.filter import financial_format

def detail_profitloss_company_brand(data_source, field, company_brand):
    fig = go.Figure(
        go.Bar(name=field, 
            x=data_source[field],
            y=data_source[company_brand],
            orientation='h',
            text=[financial_format(i/1000000) for i in data_source[field]],
            textposition='auto',
            textangle=0,
            hoverlabel=dict(
                bgcolor="white",
                font_size=15
            ),
            hovertemplate="<b>%{y}</b><br>Rp.%{value:,.2f}")
    )
    fig.update_layout(xaxis_tickprefix = 'Rp. ', xaxis_tickformat = '', height=800,
                        uniformtext_minsize=15, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)