import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
from utils.filter import financial_format


def summary_profitloss_metrics(label, value, percentage):
    value = financial_format(value / 1000000)

    if percentage != None:
        percentage = financial_format(percentage * 100)
        st.metric(label,value=f"{value} - {percentage}%")
    else:
        st.metric(label,value=f"{value}")
    style_metric_cards()