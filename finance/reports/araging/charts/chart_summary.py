import streamlit as st
import pandas as pd
from utils.alvinmelt import melt
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
# from streamlit_plotly_events import plotly_events
from utils.filter import financial_format

def chart_summary(data_source):
    #region : applying group by in data source
    raw_data_over_due_aging = data_source.groupby(['CompanyConsole',
                                            'ConsolidationName',
                                            'CompanyCode',
                                            'CompanyName',
                                            'CompanyAbbreviation']).agg({'BeginAmount':'sum',
                                                                         'SalesAmount':'sum',
                                                                         'SalesCorrectionAmount':'sum',
                                                                         'NotOverDueAmount':'sum',
                                                                         'PayAmount':'sum',
                                                                         'PayReturnAmount':'sum',
                                                                         'PayCorrectionAmount':'sum',
                                                                         'Days0to7':'sum',
                                                                        'Days8to14':'sum',
                                                                        'Days15to21':'sum',
                                                                        'Days22to30':'sum',
                                                                        'Days31to60':'sum',
                                                                        'Days61to90':'sum',
                                                                        'Days90':'sum'})
    #endregion
    
    #region : metrics
    c11,c12,c13,c14 = st.columns([1,2,2,1])
    sumofendingamount = int((raw_data_over_due_aging['BeginAmount'].sum()+raw_data_over_due_aging['SalesAmount'].sum())-
                                (raw_data_over_due_aging['SalesCorrectionAmount'].sum()+raw_data_over_due_aging['PayAmount'].sum()+
                                raw_data_over_due_aging['PayReturnAmount'].sum()+raw_data_over_due_aging['PayCorrectionAmount'].sum()))
    sumofnotoverdue = int(raw_data_over_due_aging['NotOverDueAmount'].sum())  
    with c11:
        pass
    with c12:
        st.metric('Sum of Ending Amount',value=financial_format(sumofendingamount))
        style_metric_cards()
    with c13:
        st.metric('Sum of Not Over Due',financial_format(sumofnotoverdue))
        style_metric_cards()
    with c14:
        pass
    #endregion
    
    #region : barchart
    st.subheader("AR Aging Over Due Ending Amount")
    data_hasil = raw_data_over_due_aging
    results = melt(data_hasil,id_var=['Days0to7','Days8to14','Days15to21','Days22to30','Days31to60','Days61to90','Days90'])
    fig = go.Figure(
        data=[go.Bar(
            x=results['variable'], y=results['value'],
            text=[financial_format(int(i)) for i in results['value']],
            textposition='auto',
        )])
    # events = plotly_events(fig)
    fig.update_layout(yaxis_tickprefix = 'Rp. ', yaxis_tickformat = '')
    fig.update_layout(yaxis=dict(tickfont=dict(size=12)),
                      xaxis=dict(tickfont=dict(size=14),
                                 tickmode = 'array',
                                 tickvals = ['Days0to7','Days8to14','Days15to21','Days22to30','Days31to60','Days61to90','Days90'],
                                 ticktext=['0-7 days','8-14 days','15-21 days','22-30 days','31-60 days','61-90 days','> 90 days'])),
    st.plotly_chart(fig,use_container_width=True, key = "chart_summary")
    #endregion