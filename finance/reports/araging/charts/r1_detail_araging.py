import streamlit as st
import plotly.graph_objects as go

def detail_argroup(chart_data):
    fig = go.Figure(go.Pie(labels=chart_data['ArGroupDescription'].tolist(), values=chart_data['EndingAmount'].tolist()))
    fig.update_traces(textinfo='percent', textfont_size=20,
                            hovertemplate="<b>%{label}:</b> Rp.%{value:,d}", textposition='auto',
                            hoverlabel=dict(
                                    bgcolor="white",
                                    font_size=15
                            )).update_layout(height=370, margin=dict(t=50,b=50,l=0,r=0))
    fig.update_traces(textposition='auto')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True, key="detail_argroup")