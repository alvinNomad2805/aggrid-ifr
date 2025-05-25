from utils.caching import parquet
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import polars as pl
import plotly.graph_objects as go
from utils.filter import financial_format

def stock_management_tab(company_name, selected_brand):
    col1, col2 = st.columns(2)
    raw_data_df = parquet(f"reports/ifr/parquet/ifr-stock-management_{company_name}.parquet",
                            f"/ifr-stock-management?company_name={company_name}")
    
    if raw_data_df.is_empty():
        empty_raw_data = pl.DataFrame(schema={
                'VehicleBrand': pl.Utf8,
                'ModelCode': pl.Utf8,
                'ModelDescription': pl.Utf8,
                'StockOwnByDealer': pl.Utf8,
                'AgingDays': pl.Int64,
                'Amount': pl.Float64,
        })
        raw_data_df = empty_raw_data

    if selected_brand != 'ALL':
        raw_data_df = raw_data_df.filter(pl.col('VehicleBrand') == selected_brand)

    stock_less_30 = raw_data_df.filter(pl.col('AgingDays') < 30)
    stock_30_60 = raw_data_df.filter((pl.col('AgingDays') >= 30) &
                            (pl.col('AgingDays') <= 60))
    stock_60_90 = raw_data_df.filter((pl.col('AgingDays') >= 60) &
                            (pl.col('AgingDays') <= 90))
    stock_more_30 = raw_data_df.filter(pl.col('AgingDays') > 90)

    with col1:
        col1.markdown('<h2 class="section-title">Stock Unit Quantity</h2>',unsafe_allow_html=True)
        group_aging = ["< 30 Days","30 - 60 Days","60 - 90 Days","> 90 Days"]
        stock_unit_data = [stock_less_30['Amount'].count(),stock_30_60['Amount'].count(),stock_60_90['Amount'].count(),stock_more_30['Amount'].count()]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=group_aging,
                y=stock_unit_data,
                width=0.6,
                name="",
                textposition='auto',
                texttemplate="%{y:,d} Unit",
                text=stock_unit_data,
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=15
                ),
                hovertemplate="<b>%{x}</b> : %{y:,d} Unit")
            )
        fig.update_layout(
            title="Stock Unit Aging",
            xaxis_title="Aging Categories",
            yaxis_title="Unit",
            font = dict(size=15),
            yaxis=dict(tickfont=dict(size=15)),
            xaxis=dict(tickfont=dict(size=15))
        )
        col1.plotly_chart(fig,use_container_width=True,key="stock_unit_aging")
    
    with col2:
        col2.markdown('<h2 class="section-title">Stock Unit Amount</h2>',unsafe_allow_html=True)
        inventory_unit_data = [stock_less_30['Amount'].sum(),stock_30_60['Amount'].sum(),stock_60_90['Amount'].sum(),stock_more_30['Amount'].sum()]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=group_aging,
                y=inventory_unit_data,
                width=0.6,
                name="",
                textposition='auto',
                text=[financial_format(i/1000000) for i in inventory_unit_data],
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=15
                ),
                hovertemplate="<b>%{x}</b> : Rp.%{y:,.2f}")
            )
        fig.update_layout(
            title="Stock Unit Aging",
            xaxis_title="Aging Categories",
            yaxis_title="Amount (Rp. Million)",
            font = dict(size=15),
            yaxis=dict(tickfont=dict(size=15)),
            xaxis=dict(tickfont=dict(size=15))
        )
        col2.plotly_chart(fig,use_container_width=True,key="stock_amount_aging")