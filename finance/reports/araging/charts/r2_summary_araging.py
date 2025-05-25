import streamlit as st
import plotly.graph_objects as go
from utils.filter import financial_format

def summary_araging(chart_data):
    fig = go.Figure(
        data=[go.Bar(
            x=chart_data['variable'], y=chart_data['value'],
            text=[financial_format(i/1000000) for i in chart_data['value']],
            textposition='auto',
            width=0.5
        )])
    fig.update_layout(yaxis_tickprefix = 'Rp. ', yaxis_tickformat = '', font=dict(size=15))
    fig.update_layout(yaxis=dict(tickfont=dict(size=12)),
                    xaxis=dict(tickfont=dict(size=14),
                                tickmode = 'array',
                                tickvals = ['Days0to7','Days8to14','Days15to21','Days22to30','Days31to60','Days61to90','Days90'],
                                ticktext=['0-7 days','8-14 days','15-21 days','22-30 days','31-60 days','61-90 days','> 90 days'])),
    st.plotly_chart(fig,use_container_width=True, key = "summary_araging")

def summary_araging_invoice(chart_data):
    fig = go.Figure(
        data=[go.Bar(
            x=chart_data['category'],
            y=chart_data['EndingAmount'],
            text=[financial_format(i/1000000) for i in chart_data['EndingAmount']],
            textposition='auto',
            width=0.5
        )]
    )
    fig.update_layout(yaxis_tickprefix = 'Rp. ', yaxis_tickformat = '', font=dict(size=15))
    fig.update_layout(yaxis=dict(tickfont=dict(size=12)),
                    xaxis=dict(tickfont=dict(size=14),
                                tickmode = 'array',
                                tickvals = ['Days0to7','Days8to14','Days15to21','Days22to30','Days31to60','Days61to90','Days90'],
                                ticktext=['0-7 days','8-14 days','15-21 days','22-30 days','31-60 days','61-90 days','> 90 days']))
    st.plotly_chart(fig, use_container_width=True, key="summary_araging_invoice")
