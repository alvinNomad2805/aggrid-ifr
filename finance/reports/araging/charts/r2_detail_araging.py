import streamlit as st
import plotly.graph_objects as go
from utils.filter import financial_format

def detail_brand(chart_data,label=""):
    fig = go.Figure(go.Bar(
                    x=chart_data['EndingAmount'],
                    y=chart_data['VehicleBrand'],
                    orientation='h',
                    text=[financial_format(i/1000000) for i in chart_data['EndingAmount']],
                    textposition='auto',
                    textangle=0,
                    hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                    ),
                    hovertemplate="<b>%{y}</b><br>Rp.%{value:,d}",
                    width=0.5,
                    name=""))
    fig.update_layout(xaxis_tickprefix = 'Rp. ', xaxis_tickformat = '', yaxis=dict(tickfont=dict(size=15)), xaxis=dict(tickfont=dict(size=15)))
    fig.update_layout(height=800, font=dict(size=15))
    st.plotly_chart(fig, theme = 'streamlit', use_container_width=True, key=f"detail_brand_{label}")


def detail_profit_center(chart_data, label=""):
    fig = go.Figure(go.Bar(
                    x=chart_data['EndingAmount'],
                    y=chart_data['ProfitCenterDescription'],
                    orientation='h',
                    text=[financial_format(i/1000000) for i in chart_data['EndingAmount']],
                    textposition='auto',
                    textangle=0,
                    hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                    ),
                    hovertemplate="<b>%{y}</b><br>Rp.%{value:,d}",
                    width=0.5,
                    name=""))
    fig.update_layout(xaxis_tickprefix = 'Rp. ', xaxis_tickformat = '', yaxis=dict(tickfont=dict(size=15)), xaxis=dict(tickfont=dict(size=15)))
    fig.update_layout(height=800, font=dict(size=15), uniformtext=dict(minsize=15, mode='hide'))
    st.plotly_chart(fig, theme = 'streamlit', use_container_width=True, key=f"detail_profit_center_{label}")