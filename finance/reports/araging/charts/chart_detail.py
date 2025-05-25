import streamlit as st
import plotly.graph_objects as go

def chart_detail(data_source):
        raw_data = data_source.groupby(['VehicleBrand',
                                    'ArGroupDescription',
                                    'ProfitCenterDescription',
                                    'CustTypeDescription',
                                    'CompanyName',
                                    'CustomerName']).agg({'BeginAmount':'sum',
                                                        'SalesAmount':'sum',
                                                        'SalesCorrectionAmount':'sum',
                                                        'NotOverDueAmount':'sum',
                                                        'PayAmount':'sum',
                                                        'PayReturnAmount':'sum',
                                                        'PayCorrectionAmount':'sum'}).reset_index()
        raw_data.loc[:,'EndingAmount'] = (raw_data['BeginAmount']+raw_data['SalesAmount'])-(raw_data['SalesCorrectionAmount']+raw_data['PayAmount']+raw_data['PayReturnAmount']+raw_data['PayCorrectionAmount'])
        
        st.subheader("Ending Amount by AR Group")
        fig = go.Figure(go.Pie(labels=raw_data['ArGroupDescription'].tolist(), values=raw_data['EndingAmount'].tolist()))
        fig.update_traces(textinfo='percent', textfont_size=20,
                                hovertemplate="<b>%{label}:</b> Rp.%{value:,d}", textposition='auto',
                                hoverlabel=dict(
                                        bgcolor="white",
                                        font_size=15
                                )).update_layout(height=370, margin=dict(t=50,b=50,l=0,r=0))
        fig.update_traces(textposition='auto')
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True, key="chart_detail_1")

        h1, h2 = st.columns(2)
        with h1:
                st.subheader("Ending Amount by Brand")
                chart_raw_data = raw_data.groupby('VehicleBrand')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=True)
                fig = go.Figure(go.Bar(
                                x=chart_raw_data['EndingAmount'],
                                y=chart_raw_data['VehicleBrand'],
                                orientation='h',
                                text=chart_raw_data['EndingAmount'],
                                texttemplate="Rp.%{value:,d}",
                                textposition='auto',
                                hoverlabel=dict(
                                        bgcolor="white",
                                        font_size=15
                                ),
                                hovertemplate="<b>%{y}</b><br>Rp.%{value:,d}",
                                name=""))
                fig.update_layout(height=800)
                st.plotly_chart(fig, theme='streamlit', use_container_width=True, key = "chart_detail_2")
        with h2:
                st.subheader("Ending Amount by Profit Center")
                chart_raw_data = raw_data.groupby('ProfitCenterDescription')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=True)
                fig = go.Figure(go.Bar(
                                x=chart_raw_data['EndingAmount'],
                                y=chart_raw_data['ProfitCenterDescription'],
                                orientation='h',
                                text=chart_raw_data['EndingAmount'],
                                texttemplate="Rp.%{value:,d}",
                                textposition='auto',
                                hoverlabel=dict(
                                        bgcolor="white",
                                        font_size=15
                                ),
                                hovertemplate="<b>%{y}</b><br>Rp.%{value:,d}",
                                name=""))
                fig.update_layout(height=800)
                st.plotly_chart(fig, theme='streamlit', use_container_width=True, key = "chart_detail_3")

        h1, h2 = st.columns(2)
        with h1:
                chart_raw_data = raw_data.groupby('CompanyName')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=False)[:10]
                chart_raw_data = chart_raw_data.sort_values('EndingAmount', ascending=True)
                st.subheader(f"Top {len(chart_raw_data)} Ending Amount by Company")
                fig = go.Figure(go.Bar(
                                x=chart_raw_data['EndingAmount'],
                                y=chart_raw_data['CompanyName'],
                                orientation='h',
                                text=chart_raw_data['EndingAmount'],
                                texttemplate="Rp.%{value:,d}",
                                textposition='auto',
                                hoverlabel=dict(
                                        bgcolor="white",
                                        font_size=15
                                ),
                                hovertemplate="<b>%{y}</b><br>Rp.%{value:,d}",
                                name=""))
                fig.update_layout(height=800)
                st.plotly_chart(fig, theme='streamlit', use_container_width=True, key = "chart_detail_4")
        with h2:
                chart_raw_data = raw_data.groupby('CustomerName')['EndingAmount'].sum().reset_index().sort_values('EndingAmount', ascending=False)[:10]
                chart_raw_data = chart_raw_data.sort_values('EndingAmount', ascending=True)
                st.subheader(f"Top {len(chart_raw_data)} Ending Amount by Customer Name")
                fig = go.Figure(go.Bar(
                                x=chart_raw_data['EndingAmount'],
                                y=chart_raw_data['CustomerName'],
                                orientation='h',
                                text=chart_raw_data['EndingAmount'],
                                texttemplate="Rp.%{value:,d}",
                                textposition='auto',
                                hoverlabel=dict(
                                        bgcolor="white",
                                        font_size=15
                                ),
                                hovertemplate="<b>%{y}</b><br>Rp.%{value:,d}",
                                name=""))
                fig.update_layout(height=800)
                st.plotly_chart(fig, theme = 'streamlit', use_container_width=True, key="chart_detail")