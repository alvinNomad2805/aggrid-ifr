import streamlit as st
import plotly.graph_objects as go
from utils.filter import financial_format

def detail_profitloss_brand(data_source, field, range_axis):
    fig = go.Figure(
        go.Bar(name=field, 
            x=data_source[field],
            y=data_source['Brand'],
            orientation='h',
            text=data_source[field],
            texttemplate="Rp.%{value:,.2f}",
            textposition='auto',
            hoverlabel=dict(
                    bgcolor="white",
                    font_size=15
            ),
            hovertemplate="<b>%{y}</b><br>Rp.%{value:,.2f}"),
            # marker_color = chart_data_gross_profit['Color']
            # marker = dict(color = chart_data_gross_profit['Color'])
        )
    fig.update_layout(xaxis_tickprefizx = 'Rp. ', xaxis_tickformat = '', height=800,
                        uniformtext_minsize=8, uniformtext_mode='hide',
                        xaxis=dict(range=[-range_axis, range_axis]))
    st.plotly_chart(fig, use_container_width=True)

def detail_profitloss_brand_v2(data_source1, data_source2, data_source3, field1, field2, field3, label=""):
    for data_source, field in zip([data_source1, data_source2, data_source3], [field1, field2, field3]):
        field_text = field + "_text"
        data_source[field_text] = data_source[field]/1000000
        data_source[field_text] =  data_source[field_text].apply(financial_format)

    fig = go.Figure(data=[
        go.Bar(name='Gross Profit (Rp. Million)', 
                x=data_source1[field1], 
                y=data_source1['Brand'],
                orientation='h',
                text=data_source1[field1 + "_text"],
                textposition='auto',
                hoverlabel=dict(bgcolor="white",font_size=15),
                hovertemplate="<b>%{y}</b><br>Rp.%{text}"
                ),
        go.Bar(name='Net Operating Profit (Rp. Million)', 
                x=data_source2[field2], 
                y=data_source2['Brand'],
                orientation='h',
                text=data_source2[field2 + "_text"],
                textposition='auto',
                hoverlabel=dict(bgcolor="white",font_size=15),
                hovertemplate="<b>%{y}</b><br>Rp.%{text}",
                ),
        go.Bar(name='Net Profit (Rp. Million)', 
                x=data_source3[field3], 
                y=data_source3['Brand'],
                orientation='h',
                text=data_source3[field3 + "_text"],
                textposition='auto',
                hoverlabel=dict(bgcolor="white",font_size=15),
                hovertemplate="<b>%{y}</b><br>Rp.%{text}",
                )])
    # Change the bar mode
    fig.update_layout(barmode='group', height=800, yaxis=dict(showgrid=True), font=dict(size=15),uniformtext_minsize=15, uniformtext_mode='show',)
    fig.update_traces(textangle=0)
    st.plotly_chart(fig, use_container_width=True, key=f"detail_profitloss_brand_v2{label}")
