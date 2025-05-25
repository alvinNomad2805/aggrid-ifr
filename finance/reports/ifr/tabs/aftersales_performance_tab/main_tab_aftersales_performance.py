from utils.caching import parquet, parquet_by_monthly, parquet_by_yearly
import streamlit as st
from data.LoadData import load_data
import pandas as pd
import polars as pl
import datetime
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from utils.filter import financial_format

def main_tab_aftersales_performance(selected_year,
                                    selected_month,
                                    selected_company,
                                    selected_brand,
                                    gross_profit,
                                    gross_profit_last_year,
                                    income_budget_gross_profit, 
                                    month_to_proceed):
    #00002 : workshop | 00003 : body repair | 00004 : accessories | 00005 : sparepart
    unit_entry_ifr = parquet_by_yearly(selected_year,
                                        f"reports/ifr/parquet/ifr-unit-entry_{selected_year}_{selected_company}.parquet",
                                        f"/ifr-unit-entry?period_year={selected_year}&company_name={selected_company}")
    t1,t2,t3,t4 = st.tabs(["Workshop","Body Repair","Accessories","Sparepart"])
    with t1:
        t1.markdown('<h2 class="section-title">Workshop - Unit Entry</h2>',unsafe_allow_html=True)
        unit_entry_ifr_df = unit_entry_ifr

        if unit_entry_ifr_df.is_empty():
            empty_unit_entry_df = pl.DataFrame(schema={
                    'RegionalName': pl.Utf8,
                    'CompanyName': pl.Utf8,
                    'CompanyAbbreviation': pl.Utf8,
                    'WoType': pl.Utf8,
                    'ModelCode': pl.Utf8,
                    'ModelDescription': pl.Utf8,
                    'VariantCode': pl.Utf8,
                    'VariantDescription': pl.Utf8,
                    'WoSysNo': pl.Utf8,
                    'VehicleBrand': pl.Utf8,
                    'JobTypeValue': pl.Utf8,
                    'JobTypeDescription': pl.Utf8,
                    'CostProfitCenterCode': pl.Utf8,
                    'InvoiceDate': pl.Utf8,
                })         
            unit_entry_ifr_df = empty_unit_entry_df

        if selected_brand != 'ALL':
            # unit_entry_ifr_df = unit_entry_ifr_df[unit_entry_ifr_df['VehicleBrand'] == selected_brand]
            unit_entry_ifr_df = unit_entry_ifr_df.filter(pl.col('VehicleBrand') == selected_brand)
        # unit_entry_ifr_df = unit_entry_ifr_df[unit_entry_ifr_df['CostProfitCenterCode'] == '00002']
        unit_entry_ifr_df = unit_entry_ifr_df.filter(pl.col('CostProfitCenterCode') == '00002')
        # unit_entry_ifr_df["PeriodMonth"] = pl.to_datetime(unit_entry_ifr_df['InvoiceDate']).dt.month
        # Filter and print the first matching row
        # st.write(unit_entry_ifr_df.filter(pl.col('InvoiceDate').is_not_null()).head(1))
        unit_entry_ifr_df = unit_entry_ifr_df.with_columns(
            pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%SZ").dt.month().alias("PeriodMonth")
        )
        
        unit_entry_ifr_df = unit_entry_ifr_df.with_columns(
            pl.col("JobTypeDescription").str.replace("Job Type For ", "").alias("JobTypeDescription")
        )

        # st.write(unit_entry_ifr_df.schema)

        # unit_entry_ifr_df.loc[~unit_entry_ifr_df["JobTypeDescription"].isin(["Periodical Maintenance", "General Repair", "Free Service Inspection", "Warranty"]), "JobTypeDescription"] = "Others"
        unit_entry_ifr_df = unit_entry_ifr_df.with_columns(
            pl.when(~pl.col("JobTypeDescription").is_in([
                "Periodical Maintenance", 
                "General Repair", 
                "Free Service Inspection", 
                "Warranty"
                ]))
            .then(pl.lit("Others"))
            .otherwise(pl.col("JobTypeDescription"))
            .alias("JobTypeDescription")
        )

        # unit_entry_ifr_df = unit_entry_ifr_df[~unit_entry_ifr_df["WoType"].isin(["Internal", "Affiliated"])]
        unit_entry_ifr_df = unit_entry_ifr_df.filter(~pl.col("WoType").is_in(["Internal", "Affiliated"]))
        # current_unit_entry = unit_entry_ifr_df[unit_entry_ifr_df['InvoiceDate'].str.contains(f"{selected_year}-{selected_month}")]
        current_unit_entry = unit_entry_ifr_df.filter(pl.col('InvoiceDate').str.contains(f"{selected_year}-{selected_month}"))
        get_current_month = datetime.datetime.now().month
        # -2 because current month setting in filter is prev month
        if get_current_month > 10:
            prev_month = str(get_current_month-2)
        else:
            prev_month = "0"+str(get_current_month-2)
        # prev_unit_entry = unit_entry_ifr_df[unit_entry_ifr_df['InvoiceDate'].str.contains(f"{selected_year}-{prev_month}")]
        prev_unit_entry = unit_entry_ifr_df.filter(pl.col('InvoiceDate').str.contains(f"{selected_year}-{prev_month}"))
        
        # total_current_unit_entry = current_unit_entry.groupby(["JobTypeDescription"])['WoSysNo'].nunique().reset_index(name="total_unit_entry").sort_values(by="JobTypeDescription")
        total_current_unit_entry = (
            current_unit_entry
            .group_by("JobTypeDescription")
            .agg(pl.col("WoSysNo").n_unique().alias("total_unit_entry"))
            .sort("JobTypeDescription")
        )

        # total_prev_unit_entry = prev_unit_entry.groupby(["JobTypeDescription"])['WoSysNo'].nunique().reset_index(name="total_unit_entry").sort_values(by="JobTypeDescription")
        total_prev_unit_entry = (
            prev_unit_entry
            .group_by("JobTypeDescription")
            .agg(pl.col("WoSysNo").n_unique().alias("total_unit_entry"))
            .sort("JobTypeDescription")
        )
        # unit_entry_ifr_df_ytd = unit_entry_ifr_df[unit_entry_ifr_df['PeriodMonth'] <= get_current_month-1]
        unit_entry_ifr_df_ytd = unit_entry_ifr_df.filter(pl.col('PeriodMonth') <= get_current_month-1)
        # current_unit_entry_ifr_df_ytd = unit_entry_ifr_df_ytd.groupby(["JobTypeDescription"])['WoSysNo'].nunique().reset_index(name="total_unit_entry").sort_values(by="JobTypeDescription")
        current_unit_entry_ifr_df_ytd = (
            unit_entry_ifr_df_ytd
            .group_by("JobTypeDescription")
            .agg(pl.col("WoSysNo").n_unique().alias("total_unit_entry"))
            .sort("JobTypeDescription")
        )

        tc1,tc2 = t1.columns(2)
        with tc1:
            tc1.subheader("Current")
            fig = go.Figure(data=[
            go.Bar(name='Actual', 
                    x=total_current_unit_entry["total_unit_entry"], 
                    y=total_current_unit_entry['JobTypeDescription'],
                    orientation='h',
                    text=total_current_unit_entry["total_unit_entry"],
                    texttemplate="%{text:,d}",
                    textposition='auto',
                    hoverlabel=dict(bgcolor="white",font_size=15),
                    hovertemplate="<b>%{y}</b><br>%{x:,d}"
                    ),
            go.Bar(name='Last Month', 
                    x=total_prev_unit_entry["total_unit_entry"], 
                    y=total_prev_unit_entry['JobTypeDescription'],
                    orientation='h',
                    text=total_prev_unit_entry["total_unit_entry"],
                    texttemplate="%{text:,d}",
                    textposition='auto',
                    hoverlabel=dict(bgcolor="white",font_size=15),
                    hovertemplate="<b>%{y}</b><br>%{x:,d}",
                    )])
            # Change the bar mode
            fig.update_layout(barmode='group', yaxis=dict(showgrid=True), font=dict(size=15),uniformtext_minsize=15, uniformtext_mode='show',xaxis_title='Unit', yaxis_title='',)
            fig.update_yaxes(categoryorder='category ascending')
            fig.update_traces(textangle=0)
            tc1.plotly_chart(fig, use_container_width=True,key="Current")
        
        get_current_year = datetime.datetime.now().year
        last_year_unit_entry_ifr = load_data(f"/ifr-unit-entry?period_year={str(get_current_year-1)}&company_name={selected_company}")
        last_year_unit_entry_ifr_df = pl.DataFrame(last_year_unit_entry_ifr['Data'])
        if last_year_unit_entry_ifr_df.is_empty():
            empty_unit_entry_df = pl.DataFrame(
                schema = {
                    'RegionalName': pl.Utf8,
                    'CompanyName': pl.Utf8,
                    'CompanyAbbreviation': pl.Utf8,
                    'WoType': pl.Utf8,
                    'ModelCode': pl.Utf8,
                    'ModelDescription': pl.Utf8,
                    'VariantCode': pl.Utf8,
                    'VariantDescription': pl.Utf8,
                    'WoSysNo': pl.Utf8,
                    'VehicleBrand': pl.Utf8,
                    'JobTypeValue': pl.Utf8,
                    'JobTypeDescription': pl.Utf8,
                    'CostProfitCenterCode': pl.Utf8,
                    'InvoiceDate': pl.Utf8,
                }
            )
            last_year_unit_entry_ifr_df = empty_unit_entry_df
        
        if selected_brand != 'ALL':
            # last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df[last_year_unit_entry_ifr_df['VehicleBrand'] == selected_brand]
            last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df.filter(pl.col('VehicleBrand') == selected_brand)
        # last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df[last_year_unit_entry_ifr_df['CostProfitCenterCode'] == '00002']
        last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df.filter(pl.col('CostProfitCenterCode') == '00002')
        # last_year_unit_entry_ifr_df["PeriodMonth"] = pl.to_datetime(last_year_unit_entry_ifr_df['InvoiceDate']).dt.month
        last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df.with_columns(
            pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%SZ").dt.month().alias("PeriodMonth")
        )

        # last_year_unit_entry_ifr_df.loc[:,'JobTypeDescription'] = last_year_unit_entry_ifr_df['JobTypeDescription'].apply(lambda x: x.replace("Job Type For ", ""))
        last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df.with_columns(
            pl.col("JobTypeDescription").str.replace("Job Type For ", "").alias("JobTypeDescription")
        )
        # last_year_unit_entry_ifr_df.loc[~last_year_unit_entry_ifr_df["JobTypeDescription"].isin(["Periodical Maintenance", "General Repair", "Free Service Inspection", "Warranty"]), "JobTypeDescription"] = "Others"
        last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df.with_columns(
            pl.when(~pl.col("JobTypeDescription").is_in([
                "Periodical Maintenance", 
                "General Repair", 
                "Free Service Inspection", 
                "Warranty"
                ]))
            .then(pl.lit("Others"))
            .otherwise(pl.col("JobTypeDescription"))
            .alias("JobTypeDescription")
        )
        # last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df[~last_year_unit_entry_ifr_df["WoType"].isin(["Internal", "Affiliated"])]
        last_year_unit_entry_ifr_df = last_year_unit_entry_ifr_df.filter(~pl.col("WoType").is_in(["Internal", "Affiliated"]))

        # last_year_unit_entry_ifr_df_ytd = last_year_unit_entry_ifr_df[last_year_unit_entry_ifr_df['PeriodMonth'] <= get_current_month]
        last_year_unit_entry_ifr_df_ytd = last_year_unit_entry_ifr_df.filter(pl.col('PeriodMonth') <= get_current_month-1)
        # last_year_unit_entry_ifr_df_ytd = last_year_unit_entry_ifr_df.groupby(["JobTypeDescription"])['WoSysNo'].nunique().reset_index(name="total_unit_entry").sort_values(by="JobTypeDescription")
        last_year_unit_entry_ifr_df_ytd = (
            last_year_unit_entry_ifr_df_ytd
            .group_by("JobTypeDescription")
            .agg(pl.col("WoSysNo").n_unique().alias("total_unit_entry"))
            .sort("JobTypeDescription")
        )

        with tc2:
            tc2.subheader("YTD")
            fig = go.Figure(data=[
            go.Bar(name='Actual', 
                    x=current_unit_entry_ifr_df_ytd["total_unit_entry"], 
                    y=current_unit_entry_ifr_df_ytd['JobTypeDescription'],
                    orientation='h',
                    text=current_unit_entry_ifr_df_ytd["total_unit_entry"],
                    texttemplate="%{text:,d}",
                    textposition='auto',
                    hoverlabel=dict(bgcolor="white",font_size=15),
                    hovertemplate="<b>%{y}</b><br>%{x:,d}"
                    ),
            go.Bar(name='Last Year', 
                    x=last_year_unit_entry_ifr_df_ytd["total_unit_entry"], 
                    y=last_year_unit_entry_ifr_df_ytd['JobTypeDescription'],
                    orientation='h',
                    text=last_year_unit_entry_ifr_df_ytd["total_unit_entry"],
                    texttemplate="%{text:,d}",
                    textposition='auto',
                    hoverlabel=dict(bgcolor="white",font_size=15),
                    hovertemplate="<b>%{y}</b><br>%{x:,d}",
                    )])
            # Change the bar mode
            fig.update_layout(barmode='group', yaxis=dict(showgrid=True), font=dict(size=15), uniformtext_minsize=15, uniformtext_mode='show',xaxis_title='Unit', yaxis_title='',)
            fig.update_yaxes(categoryorder='category ascending')
            fig.update_traces(textangle=0)
            tc2.plotly_chart(fig, use_container_width=True,key="YTD")

        t1.markdown('<h2 class="section-title">Workshop - Gross Profit (Loss)</h2>',unsafe_allow_html=True)
        
        # gross_profit_workshop = gross_profit[gross_profit['ProfitCenterCode'] == '00002']
        gross_profit_workshop = gross_profit.filter(pl.col('ProfitCenterCode') == '00002')
        # current_gross_profit = gross_profit_workshop[gross_profit_workshop['PeriodMonth'] == selected_month]
        current_gross_profit = gross_profit_workshop.filter(pl.col('PeriodMonth') == selected_month)
        # prev_gross_profit = gross_profit_workshop[~(gross_profit_workshop['PeriodMonth'] == selected_month)]
        prev_gross_profit = gross_profit_workshop.filter(pl.col('PeriodMonth') != selected_month)

        # income_budget_workshop = income_budget_gross_profit[income_budget_gross_profit['ProfitCenterCode'] == '00002']
        income_budget_workshop = income_budget_gross_profit.filter(pl.col('ProfitCenterCode') == '00002')
        # income_budget_workshop = income_budget_workshop[income_budget_workshop['PeriodMonth'] == selected_month]
        income_budget_workshop = income_budget_workshop.filter(pl.col('PeriodMonth') == selected_month)
        
        if income_budget_workshop.is_empty():
            empty_income_budget_workshop = pl.DataFrame(
                schema={
                    'CompanyCode': pl.Int64,
                    'CompanyName': pl.Utf8,
                    'CompanyAbbreviation': pl.Utf8,
                    'PeriodYear': pl.Utf8,
                    'PeriodMonth': pl.Utf8,
                    'AccountNumber': pl.Utf8,
                    'AccountDescription': pl.Utf8,
                    'AccountType': pl.Utf8,
                    'Group1': pl.Utf8,
                    'DebitAmount': pl.Int64,
                    'CreditAmount': pl.Int64,
                    'Brand': pl.Utf8,
                    'ProfitCenterCode': pl.Utf8,
                    'ProfitCenter': pl.Utf8,
                    'CompanArGroupyCode': pl.Utf8,
                    'mutation': pl.Int64
                }
            )
            income_budget_workshop = empty_income_budget_workshop
        
        if selected_brand != 'ALL':
            income_budget_workshop = income_budget_workshop[income_budget_workshop['Brand'] == selected_brand]

        # gross_profit_workshop_last_year = gross_profit_last_year[(gross_profit_last_year['ProfitCenterCode'] == '00002') & (gross_profit_last_year['PeriodMonth'] == selected_month)]
        gross_profit_workshop_last_year = gross_profit_last_year.filter((pl.col('ProfitCenterCode') == '00002') & (pl.col('PeriodMonth') == selected_month))
        current_gross_profit_ytd = current_gross_profit['EndAmount'].sum()
        prev_gross_profit_ytd = gross_profit_workshop_last_year['EndAmount'].sum()

        # income_budget_workshop_ytd = income_budget_gross_profit[income_budget_gross_profit['ProfitCenterCode'] == '00002']
        income_budget_workshop_ytd = income_budget_gross_profit.filter(pl.col('ProfitCenterCode') == '00002')
        # income_budget_workshop_ytd = income_budget_workshop_ytd[income_budget_workshop_ytd['PeriodMonth'].isin(month_to_proceed)]
        income_budget_workshop_ytd = income_budget_workshop_ytd.filter(pl.col('PeriodMonth').is_in(month_to_proceed))
        
        workshop_sum = income_budget_workshop['mutation'].sum()
        workshop_sum_ytd = income_budget_workshop_ytd['mutation'].sum()
        if workshop_sum != 0:
            percent_budget_gross_profit_workshop = round(current_gross_profit['mutation'].sum() / workshop_sum * 100, 2)
        else:
            percent_budget_gross_profit_workshop = 0
        if workshop_sum_ytd != 0:
            percent_budget_gross_profit_workshop_ytd = round(current_gross_profit_ytd / workshop_sum_ytd * 100, 2)
        else:
            percent_budget_gross_profit_workshop_ytd = 0

        col1, col2, col3, col4, col5, col6 = t1.columns((1,2,1,1,2,1))
        with col1:
            pass
        with col2:
            col2.metric('% Current Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_workshop)}%")
            style_metric_cards()
        with col3:
            pass
        with col4:
            pass
        with col5:
            col5.metric('% YTD Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_workshop_ytd)}%")
            style_metric_cards()
        with col6:
            pass

        tcc1, tcc2 = t1.columns(2)
        with tcc1:
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[current_gross_profit['mutation'].sum()],
                        name='Actual',
                        textposition='auto',
                        text=financial_format(current_gross_profit['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
                )
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[income_budget_workshop['mutation'].sum()],
                        name='Budget',
                        textposition='auto',
                        text=financial_format(income_budget_workshop['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
                )
            fig.add_trace(
                    go.Bar(
                        x=["Gross Profit"],
                        y= [prev_gross_profit['mutation'].sum()],
                        name='Last Month',
                        textposition='auto',
                        text=financial_format(prev_gross_profit['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.update_layout(
                    barmode='group',
                    xaxis_title='',
                    yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'Current Gross Profit (Loss) (Rp. Million)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            tcc1.plotly_chart(fig,use_container_width=True,key="Current Gross Profit")
        
        with tcc2:
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[current_gross_profit_ytd],
                        name='Actual',
                        textposition='auto',
                        text=financial_format(current_gross_profit_ytd/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )
            
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[income_budget_workshop_ytd['mutation'].sum()],
                        name='Budget',
                        textposition='auto',
                        text=financial_format(income_budget_workshop_ytd['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.add_trace(
                    go.Bar(
                        x=["Gross Profit"],
                        y= [prev_gross_profit_ytd],
                        name='Last Year',
                        textposition='auto',
                        text=financial_format(prev_gross_profit_ytd/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.update_layout(
                    barmode='group',
                    xaxis_title='',
                    yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'YTD Gross Profit (Loss) (Rp. Million)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            tcc2.plotly_chart(fig,use_container_width=True,key="YTD Gross Profit")
    
    with t2:
        #Body repair    
        t2.markdown('<h2 class="section-title">Body Repair - Unit Entry</h2>',unsafe_allow_html=True)
        unit_entry_ifr_bp_df = unit_entry_ifr

        if unit_entry_ifr_bp_df.is_empty():
            empty_unit_entry_df = pl.DataFrame(
                schema = {
                    'RegionalName': pl.Utf8,
                    'CompanyName': pl.Utf8,
                    'CompanyAbbreviation': pl.Utf8,
                    'WoType': pl.Utf8,
                    'ModelCode': pl.Utf8,
                    'ModelDescription': pl.Utf8,
                    'VariantCode': pl.Utf8,
                    'VariantDescription': pl.Utf8,
                    'WoSysNo': pl.Utf8,
                    'VehicleBrand': pl.Utf8,
                    'JobTypeValue': pl.Utf8,
                    'JobTypeDescription': pl.Utf8,
                    'CostProfitCenterCode': pl.Utf8,
                    'InvoiceDate': pl.Utf8,
                }
            )
            unit_entry_ifr_bp_df = empty_unit_entry_df
        if selected_brand != 'ALL':
            # unit_entry_ifr_bp_df = unit_entry_ifr_bp_df[unit_entry_ifr_bp_df['VehicleBrand'] == selected_brand]
            unit_entry_ifr_bp_df = unit_entry_ifr_bp_df.filter(pl.col('VehicleBrand') == selected_brand)
        # unit_entry_ifr_bp_df = unit_entry_ifr_bp_df[unit_entry_ifr_bp_df['CostProfitCenterCode'] == '00003']
        unit_entry_ifr_bp_df = unit_entry_ifr_bp_df.filter(pl.col('CostProfitCenterCode') == '00003')
        # unit_entry_ifr_bp_df["PeriodMonth"] = pl.to_datetime(unit_entry_ifr_bp_df['InvoiceDate']).dt.month
        unit_entry_ifr_bp_df = unit_entry_ifr_bp_df.with_columns(
            pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%SZ").dt.month().alias("PeriodMonth")
        )

        # current_unit_entry_ifr_bp_df = unit_entry_ifr_bp_df[unit_entry_ifr_bp_df['InvoiceDate'].str.contains(f"{selected_year}-{selected_month}")]
        current_unit_entry_ifr_bp_df = unit_entry_ifr_bp_df.filter(pl.col('InvoiceDate').str.contains(f"{selected_year}-{selected_month}"))
        get_current_month = datetime.datetime.now().month
        # -2 because current month setting in filter is prev month
        if get_current_month > 10:
            prev_month = str(get_current_month-2)
        else:
            prev_month = "0"+str(get_current_month-2)
        # prev_unit_entry_ifr_bp_df = unit_entry_ifr_bp_df[unit_entry_ifr_bp_df['InvoiceDate'].str.contains(f"{selected_year}-{prev_month}")]
        prev_unit_entry_ifr_bp_df = unit_entry_ifr_bp_df.filter(pl.col('InvoiceDate').str.contains(f"{selected_year}-{prev_month}"))
        
        # total_current_unit_entry_ifr_bp_df = current_unit_entry_ifr_bp_df['WoSysNo'].nunique()
        total_current_unit_entry_ifr_bp_df = current_unit_entry_ifr_bp_df.select(pl.col('WoSysNo').n_unique()).item()
        # total_prev_unit_entry_ifr_bp_df = prev_unit_entry_ifr_bp_df['WoSysNo'].nunique()
        total_prev_unit_entry_ifr_bp_df = prev_unit_entry_ifr_bp_df.select(pl.col('WoSysNo').n_unique()).item()
        # unit_entry_ifr_bp_df_ytd = unit_entry_ifr_bp_df[unit_entry_ifr_bp_df['PeriodMonth'] <= get_current_month-1]
        unit_entry_ifr_bp_df_ytd = unit_entry_ifr_bp_df.filter(pl.col('PeriodMonth') <= get_current_month-1)
        # current_unit_entry_ifr_bp_df_ytd = unit_entry_ifr_bp_df_ytd['WoSysNo'].nunique()
        current_unit_entry_ifr_bp_df_ytd = unit_entry_ifr_bp_df_ytd.select(pl.col('WoSysNo').n_unique()).item()


        tc1,tc2 = t2.columns(2)
        with tc1:
            tc1.subheader("Current")
            fig = go.Figure()
            fig.add_trace(
                go.Bar(x=["Unit Entry"],
                    y=[total_current_unit_entry_ifr_bp_df],
                    width=0.2,
                    name='Actual',
                    textposition='auto',
                    texttemplate="%{y:,.0f}",
                    text=str(total_current_unit_entry_ifr_bp_df),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=15
                    ),
                    hovertemplate="<b>%{x}</b><br>%{y:,.0f}"
                )
            )

            fig.add_trace(
                go.Bar(
                    x=["Unit Entry"],
                    y= [total_prev_unit_entry_ifr_bp_df],
                    width=0.2,
                    name='Last Month',
                    textposition='auto',
                    texttemplate="%{y:,.0f}",
                    text=str(total_prev_unit_entry_ifr_bp_df),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=15
                    ),
                    hovertemplate="<b>%{x}</b><br>%{y:,.0f}"
                )
            )

            fig.update_layout(
                barmode='group',
                bargap = 0.6,
                xaxis_title='',
                yaxis_title='Unit',
                legend_title='',
                template='simple_white',
                yaxis_tickprefix = '', 
                yaxis_tickformat = '',
                title = 'Current Unit Entry',
                font = dict(size=15),
                yaxis=dict(tickfont=dict(size=15)),
                xaxis=dict(tickfont=dict(size=15))
            )       

            tc1.plotly_chart(fig,use_container_width=True,key="Current Unit Entry")
        
        get_current_year = datetime.datetime.now().year
        last_year_unit_entry_ifr_bp_df = load_data(f"/ifr-unit-entry?period_year={str(get_current_year-1)}&company_name={selected_company}")
        last_year_unit_entry_ifr_bp_df = pl.DataFrame(last_year_unit_entry_ifr_bp_df['Data'])

        if (last_year_unit_entry_ifr_bp_df.is_empty()):
            empty_unit_entry_df = pl.DataFrame(
                schema ={
                    'RegionalName': pl.Utf8,
                    'CompanyName': pl.Utf8,
                    'CompanyAbbreviation': pl.Utf8,
                    'WoType': pl.Utf8,
                    'ModelCode': pl.Utf8,
                    'ModelDescription': pl.Utf8,
                    'VariantCode': pl.Utf8,
                    'VariantDescription': pl.Utf8,
                    'WoSysNo': pl.Utf8,
                    'VehicleBrand': pl.Utf8,
                    'JobTypeValue': pl.Utf8,
                    'JobTypeDescription': pl.Utf8,
                    'CostProfitCenterCode': pl.Utf8,
                    'InvoiceDate': pl.Utf8,
                }
            )
            last_year_unit_entry_ifr_bp_df = empty_unit_entry_df
        if selected_brand != 'ALL':
            # last_year_unit_entry_ifr_bp_df = last_year_unit_entry_ifr_bp_df[last_year_unit_entry_ifr_bp_df['VehicleBrand'] == selected_brand]
            last_year_unit_entry_ifr_bp_df = last_year_unit_entry_ifr_bp_df.filter(pl.col('VehicleBrand') == selected_brand)
        # last_year_unit_entry_ifr_bp_df = last_year_unit_entry_ifr_bp_df[last_year_unit_entry_ifr_bp_df['CostProfitCenterCode'] == '00003']
        last_year_unit_entry_ifr_bp_df = last_year_unit_entry_ifr_bp_df.filter(pl.col('CostProfitCenterCode') == '00003')
        # last_year_unit_entry_ifr_bp_df["PeriodMonth"] = pl.to_datetime(last_year_unit_entry_ifr_bp_df['InvoiceDate']).dt.month
        last_year_unit_entry_ifr_bp_df = last_year_unit_entry_ifr_bp_df.with_columns(
            pl.col('InvoiceDate').str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%SZ").dt.month().alias("PeriodMonth")
        )

        # last_year_unit_entry_ifr_bp_df_ytd = last_year_unit_entry_ifr_bp_df[last_year_unit_entry_ifr_bp_df['PeriodMonth'] <= get_current_month]
        last_year_unit_entry_ifr_bp_df_ytd = last_year_unit_entry_ifr_bp_df.filter(pl.col('PeriodMonth') <= get_current_month-1)
        last_year_unit_entry_ifr_bp_df_ytd = last_year_unit_entry_ifr_bp_df_ytd['WoSysNo'].count()

        with tc2:
            tc2.subheader("YTD")
            fig = go.Figure()
            fig.add_trace(
                go.Bar(x=["Unit Entry"],
                    y=[current_unit_entry_ifr_bp_df_ytd],
                    width=0.2,
                    name='Actual',
                    textposition='auto',
                    texttemplate="%{y:,.0f}",
                    text=str(current_unit_entry_ifr_bp_df_ytd),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=15
                    ),
                    hovertemplate="<b>%{x}</b><br>%{y:,.0f}"
                )
            )

            fig.add_trace(
                go.Bar(
                    x=["Unit Entry"],
                    y= [last_year_unit_entry_ifr_bp_df_ytd],
                    width=0.2,
                    name='Last Year',
                    textposition='auto',
                    texttemplate="%{y:,.0f}",
                    text=str(last_year_unit_entry_ifr_bp_df_ytd),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=15
                    ),
                    hovertemplate="<b>%{x}</b><br>%{y:,.0f}"
                )
            )

            fig.update_layout(
                barmode='group',
                bargap = 0.6,
                xaxis_title='',
                yaxis_title='Unit',
                legend_title='',
                template='simple_white',
                yaxis_tickprefix = '', 
                yaxis_tickformat = '',
                title = 'YTD Unit Entry',
                font = dict(size=15),
                yaxis=dict(tickfont=dict(size=15)),
                xaxis=dict(tickfont=dict(size=15))
            )       

            tc2.plotly_chart(fig,use_container_width=True,key="YTD Unit Entry")

        t2.markdown('<h2 class="section-title">Body Repair - Gross Profit (Loss)</h2>',unsafe_allow_html=True)
        
        # gross_profit_bodyrepair = gross_profit[gross_profit['ProfitCenterCode'] == '00003']
        gross_profit_bodyrepair = gross_profit.filter(pl.col('ProfitCenterCode') == '00003')
        # current_gross_profit = gross_profit_bodyrepair[gross_profit_bodyrepair['PeriodMonth'] == selected_month]
        current_gross_profit = gross_profit_bodyrepair.filter(pl.col('PeriodMonth') == selected_month)
        # prev_gross_profit = gross_profit_bodyrepair[~(gross_profit_bodyrepair['PeriodMonth'] == selected_month)]
        prev_gross_profit = gross_profit_bodyrepair.filter(pl.col('PeriodMonth') != selected_month)

        # income_budget_bodyrepair = income_budget_gross_profit[income_budget_gross_profit['ProfitCenterCode'] == '00003']
        income_budget_bodyrepair = income_budget_gross_profit.filter(pl.col('ProfitCenterCode') == '00003')
        # income_budget_bodyrepair = income_budget_bodyrepair[income_budget_bodyrepair['PeriodMonth'] == selected_month]
        income_budget_bodyrepair = income_budget_bodyrepair.filter(pl.col('PeriodMonth') == selected_month)

        # gross_profit_bodyrepair_last_year = gross_profit_last_year[(gross_profit_last_year['ProfitCenterCode'] == '00003') & (gross_profit_last_year['PeriodMonth'] == selected_month)]
        gross_profit_bodyrepair_last_year = gross_profit_last_year.filter((pl.col('ProfitCenterCode') == '00003') & (pl.col('PeriodMonth') == selected_month))
        current_gross_profit_ytd = current_gross_profit['EndAmount'].sum()
        prev_gross_profit_ytd = gross_profit_bodyrepair_last_year['EndAmount'].sum()

        # income_budget_bodyrepair_ytd = income_budget_gross_profit[income_budget_gross_profit['ProfitCenterCode'] == '00003']
        income_budget_bodyrepair_ytd = income_budget_gross_profit.filter(pl.col('ProfitCenterCode') == '00003')
        # income_budget_bodyrepair_ytd = income_budget_bodyrepair_ytd[income_budget_bodyrepair_ytd['PeriodMonth'].isin(month_to_proceed)]
        income_budget_bodyrepair_ytd = income_budget_bodyrepair_ytd.filter(pl.col('PeriodMonth').is_in(month_to_proceed))

        mut_sum = income_budget_bodyrepair['mutation'].sum()
        mut_sum_ytd = income_budget_bodyrepair_ytd['mutation'].sum()
        if mut_sum != 0:
            percent_budget_gross_profit_bodyrepair = round(current_gross_profit['mutation'].sum() / mut_sum * 100, 2)
        else:
            percent_budget_gross_profit_bodyrepair = 0
        if mut_sum_ytd != 0:
            percent_budget_gross_profit_bodyrepair_ytd = round(current_gross_profit_ytd / mut_sum_ytd * 100, 2)
        else:
            percent_budget_gross_profit_bodyrepair_ytd = 0

        col1, col2, col3, col4, col5, col6 = t2.columns((1,2,1,1,2,1))
        with col1:
            pass
        with col2:
            col2.metric('% Current Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_bodyrepair)}%")
            style_metric_cards()
        with col3:
            pass
        with col4:
            pass
        with col5:
            col5.metric('% YTD Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_bodyrepair_ytd)}%")
            style_metric_cards()
        with col6:
            pass

        tcc1, tcc2 = t2.columns(2)
        with tcc1:
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[current_gross_profit['mutation'].sum()],
                        name='Actual',
                        textposition='auto',
                        text=financial_format(current_gross_profit['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
                )
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[income_budget_bodyrepair['mutation'].sum()],
                        name='Budget',
                        textposition='auto',
                        text=financial_format(income_budget_bodyrepair['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
                )
            fig.add_trace(
                    go.Bar(
                        x=["Gross Profit"],
                        y= [prev_gross_profit['mutation'].sum()],
                        name='Last Month',
                        textposition='auto',
                        text=financial_format(prev_gross_profit['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.update_layout(
                    barmode='group',
                    xaxis_title='',
                    yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'Current Gross Profit (Loss)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            tcc1.plotly_chart(fig,use_container_width=True,key="Current Gross Profit (Loss)")
        
        with tcc2:
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[current_gross_profit_ytd],
                        name='Actual',
                        textposition='auto',
                        text=financial_format(current_gross_profit_ytd/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    ))
        
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[income_budget_bodyrepair_ytd['mutation'].sum()],
                        name='Budget',
                        textposition='auto',
                        text=financial_format(income_budget_bodyrepair_ytd['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    ))

            fig.add_trace(
                    go.Bar(
                        x=["Gross Profit"],
                        y= [prev_gross_profit_ytd],
                        name='Last Year',
                        textposition='auto',
                        text=financial_format(prev_gross_profit_ytd/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.update_layout(
                    barmode='group',
                    xaxis_title='',
                    yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'YTD Gross Profit (Loss)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            tcc2.plotly_chart(fig,use_container_width=True,key="YTD Gross Profit (Loss)")

        # PMC Stock
        t2.markdown('<h2 class="section-title">PMC Stock (4 & 5)</h2>',unsafe_allow_html=True)
        pmc_stock_ifr = parquet(f"reports/ifr/parquet/ifr-pmc-stock_{selected_company}.parquet",
                                f"/ifr-pmc-stock?company_name={selected_company}")
        pmc_stock_ifr_df = pmc_stock_ifr
        if pmc_stock_ifr_df.is_empty():
            empty_pmc_stock_ifr_df = pl.DataFrame(
            schema={
                'CompanyCode': pl.Utf8,
                'CompanyName': pl.Utf8,
                'RegionalCode': pl.Utf8,
                'RegionalName': pl.Utf8,
                'VehicleBrand': pl.Utf8,
                'MovingCode': pl.Utf8,
                'QtyEnding': pl.Int64,
                'AmountEnding': pl.Float64,
                'ItemClass': pl.Utf8
            }
            )
            pmc_stock_ifr_df = empty_pmc_stock_ifr_df
        if selected_brand != 'ALL':
            # pmc_stock_ifr_df = pmc_stock_ifr_df[pmc_stock_ifr_df['VehicleBrand'] == selected_brand]
            pmc_stock_ifr_df = pmc_stock_ifr_df.filter(pl.col('VehicleBrand') == selected_brand)
        pmc_stock_45_ifr_df_amount = pmc_stock_ifr_df['AmountEnding'].sum()
        # pmc_stock_45_only = pmc_stock_ifr_df[(pmc_stock_ifr_df['MovingCode']=='4') | (pmc_stock_ifr_df['MovingCode']=='5')]
        pmc_stock_45_only = pmc_stock_ifr_df.filter((pl.col('MovingCode') == '4') | (pl.col('MovingCode') == '5'))
        pmc_stock_45_only_amount = pmc_stock_45_only['AmountEnding'].sum()
        if pmc_stock_45_only_amount == 0:
            percentage_of_pmc45_amount = 0
        else:
            percentage_of_pmc45_amount = (pmc_stock_45_only_amount/pmc_stock_45_ifr_df_amount)*100

        pmc_stock_45_ifr_df_qty = pmc_stock_ifr_df['QtyEnding'].sum()
        pmc_stock_45_only_qty = pmc_stock_45_only['QtyEnding'].sum()
        if pmc_stock_45_only_qty == 0:
            percentage_of_pmc45_qty = 0
        else:
            percentage_of_pmc45_qty = (pmc_stock_45_only_qty/pmc_stock_45_ifr_df_qty)*100
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            col1.metric('PMC Stock (4 & 5) Qty',value='{:,.0f}'.format(pmc_stock_45_only_qty))
        with col2:
            col2.metric('PMC Stock (4 & 5) Qty %',value=f'{financial_format(percentage_of_pmc45_qty)}%')
        with col3:
            col3.metric('PMC Stock (4 & 5) Amount (Rp. Million)',value=f'{financial_format(pmc_stock_45_only_amount/1000000)}')
        with col4:
            col4.metric('PMC Stock (4 & 5) Amount %',value=f'{financial_format(percentage_of_pmc45_amount)}%')
        style_metric_cards()
            
        #Outstanding SS    
        st.markdown('<h2 class="section-title">Outstanding Supply Slip</h2>',unsafe_allow_html=True)
        outstanding_ss_ifr = parquet(f"reports/ifr/parquet/ifr-outstanding-ss_{selected_company}.parquet",
                                f"/ifr-outstanding-ss?company_name={selected_company}")
        outstanding_ss_ifr_df = outstanding_ss_ifr
        if outstanding_ss_ifr_df.is_empty():
            empty_outstanding_ss_ifr_df = pl.DataFrame(
                schema = {
                    'CompanyAbbr': pl.Utf8,
                    'CompanyName': pl.Utf8,
                    'SupplyDate': pl.Utf8,
                    'SupplyDocNo': pl.Utf8,
                    'OutstandingAmount': pl.Int64,
                    'RegionalName': pl.Utf8,
                    'VehicleBrand': pl.Utf8,
                    'SupplyType': pl.Utf8,
                    'SupplyTypeName': pl.Utf8,
                    'JumlahSS30': pl.Int64
                }
            )
            outstanding_ss_ifr_df =empty_outstanding_ss_ifr_df
        if selected_brand != 'ALL':
            # outstanding_ss_ifr_df = outstanding_ss_ifr_df[outstanding_ss_ifr_df['VehicleBrand'] == selected_brand]
            outstanding_ss_ifr_df = outstanding_ss_ifr_df.filter(pl.col('VehicleBrand') == selected_brand)
        # outstanding_ss_ifr_df['PeriodMonth'] = pl.to_datetime(outstanding_ss_ifr_df['SupplyDate']).dt.month
        outstanding_ss_ifr_df = outstanding_ss_ifr_df.with_columns(
            pl.col('SupplyDate').str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%SZ").dt.month().alias("PeriodMonth")
        )
        # outstanding_ss_ifr_df['PeriodYear'] = pl.to_datetime(outstanding_ss_ifr_df['SupplyDate']).dt.year
        outstanding_ss_ifr_df = outstanding_ss_ifr_df.with_columns(
            pl.col('SupplyDate').str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%SZ").dt.year().alias("PeriodYear")
        )
    
        get_current_month = datetime.datetime.now().month

        if (get_current_month - 1) == 0:
            prev_month = 12

        # amount
        current_ending_amount = outstanding_ss_ifr_df.filter((pl.col('PeriodMonth') == get_current_month) & 
                                                    (pl.col('PeriodYear') == selected_year)).select(pl.col('OutstandingAmount')).sum()
        

        last_year_ending_amount = outstanding_ss_ifr_df.filter((pl.col('PeriodMonth') == get_current_month) & 
                                                    (pl.col('PeriodYear') == (selected_year - 1))).select(pl.col('OutstandingAmount')).sum()
        
        # unit
        current_ending_SS30 = outstanding_ss_ifr_df.filter((pl.col('PeriodMonth') == get_current_month) & 
                                                    (pl.col('PeriodYear') == selected_year)).select('SupplyDocNo').count()
        
        last_year_ending_SS30 = outstanding_ss_ifr_df.filter((pl.col('PeriodMonth') == get_current_month) & 
                                                    (pl.col('PeriodYear') == (selected_year-1))).select('SupplyDocNo').count()
        


        ss1, ss2 = st.columns(2)
        with ss1:
            ss1.subheader("YTD")
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Outstanding Supply Slip"],
                        y=[current_ending_amount],
                        name='Actual',
                        width=0.2,
                        textposition='auto',
                        text=financial_format(current_ending_amount/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )
            
            fig.add_trace(
                    go.Bar(x=["Outstanding Supply Slip"],
                        y=[last_year_ending_amount],
                        width=0.2,
                        name='Last Year',
                        textposition='auto',
                        text=financial_format(last_year_ending_amount/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )
            fig.update_layout(
                    barmode='group',
                    bargap=0.6,
                    xaxis_title='',
                    yaxis_title='Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'YTD Outstanding Supply Slip - Amount (Rp. Million)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            ss1.plotly_chart(fig,use_container_width=True,key="YTD Outstanding Supply Slip - Amount (Rp. Million)")
        with ss2:
            ss2.subheader("YTD")
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Outstanding Supply Slip"],
                        y=[current_ending_SS30],
                        name='Actual',
                        width=0.2,
                        textposition='auto',
                        texttemplate="%{y:d}",
                        text=str(current_ending_SS30),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>%{y:,.0f}"
                    )
                )
            
            fig.add_trace(
                    go.Bar(x=["Outstanding Supply Slip"],
                        y=[last_year_ending_SS30],
                        width=0.2,
                        name='Last Year',
                        textposition='auto',
                        texttemplate="%{y:,d}",
                        text=str(last_year_ending_SS30),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>%{y:,.0f}"
                    )
                )
            fig.update_layout(
                    barmode='group',
                    bargap=0.6,
                    xaxis_title='',
                    yaxis_title='Unit',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'YTD Outstanding Supply Slip - Unit',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            ss2.plotly_chart(fig,use_container_width=True,key="YTD Outstanding Supply Slip - Unit")

    with t3:
        # Accessories
        t3.markdown('<h2 class="section-title">Accessories - Gross Profit (Loss)</h2>',unsafe_allow_html=True)

        # gross_profit_accessories = gross_profit[gross_profit['ProfitCenterCode'] == '00004']
        gross_profit_accessories = gross_profit.filter(pl.col('ProfitCenterCode') == '00004')
        # current_gross_profit = gross_profit_accessories[gross_profit_accessories['PeriodMonth'] == selected_month]
        current_gross_profit = gross_profit_accessories.filter(pl.col('PeriodMonth') == selected_month)
        # prev_gross_profit = gross_profit_accessories[~(gross_profit_accessories['PeriodMonth'] == selected_month)]
        prev_gross_profit = gross_profit_accessories.filter(pl.col('PeriodMonth') != selected_month)

        # income_budget_accessories = income_budget_gross_profit[income_budget_gross_profit['ProfitCenterCode'] == '00004']
        income_budget_accessories = income_budget_gross_profit.filter(pl.col('ProfitCenterCode') == '00004')
        # income_budget_accessories = income_budget_accessories[income_budget_accessories['PeriodMonth'] == selected_month]
        income_budget_accessories = income_budget_accessories.filter(pl.col('PeriodMonth') == selected_month)
        
        if income_budget_accessories.is_empty():
            empty_income_budget_accessories = pl.DataFrame(
                schema={
                    'CompanyCode': pl.Int64,
                    'CompanyName': pl.Utf8,
                    'CompanyAbbreviation': pl.Utf8,
                    'PeriodYear': pl.Utf8,
                    'PeriodMonth': pl.Utf8,
                    'AccountNumber': pl.Utf8,
                    'AccountDescription': pl.Utf8,
                    'AccountType': pl.Utf8,
                    'Group1': pl.Utf8,
                    'DebitAmount': pl.Int64,
                    'CreditAmount': pl.Int64,
                    'Brand': pl.Utf8,
                    'ProfitCenterCode': pl.Utf8,
                    'ProfitCenter': pl.Utf8,
                    'CompanArGroupyCode': pl.Utf8,
                    'mutation': pl.Int64
                }
            )
            income_budget_accessories = empty_income_budget_accessories
        if selected_brand != 'ALL':
            # income_budget_accessories = income_budget_accessories[income_budget_accessories['Brand'] == selected_brand]
            income_budget_accessories = income_budget_accessories.filter(pl.col('Brand') == selected_brand)

        # gross_profit_accessories_last_year = gross_profit_last_year[(gross_profit_last_year['ProfitCenterCode'] == '00004') & (gross_profit_last_year['PeriodMonth'] == selected_month)]
        gross_profit_accessories_last_year = gross_profit_last_year.filter((pl.col('ProfitCenterCode') == '00004') & (pl.col('PeriodMonth') == selected_month))
        current_gross_profit_ytd = current_gross_profit['EndAmount'].sum()
        prev_gross_profit_ytd = gross_profit_accessories_last_year['EndAmount'].sum()

        # income_budget_accessories_ytd = income_budget_gross_profit[income_budget_gross_profit['ProfitCenterCode'] == '00004']
        income_budget_accessories_ytd = income_budget_gross_profit.filter(pl.col('ProfitCenterCode') == '00004')
        # income_budget_accessories_ytd = income_budget_accessories_ytd[income_budget_accessories_ytd['PeriodMonth'].isin(month_to_proceed)]
        income_budget_accessories_ytd = income_budget_accessories_ytd.filter(pl.col('PeriodMonth').is_in(month_to_proceed))
        
        acces_sum = income_budget_accessories['mutation'].sum()
        acces_sum_ytd = income_budget_accessories_ytd['mutation'].sum()
        if acces_sum != 0:
            percent_budget_gross_profit_accessories = round(current_gross_profit['mutation'].sum() / acces_sum * 100, 2)
        else:
            percent_budget_gross_profit_accessories = 0
        if acces_sum_ytd != 0:
            percent_budget_gross_profit_accessories_ytd = round(current_gross_profit_ytd / acces_sum_ytd * 100, 2)
        else:
            percent_budget_gross_profit_accessories_ytd = 0

        col1, col2, col3, col4, col5, col6 = t3.columns((1,2,1,1,2,1))
        with col1:
            pass
        with col2:
            col2.metric('% Current Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_accessories)}%")
            style_metric_cards()
        with col3:
            pass
        with col4:
            pass
        with col5:
            col5.metric('% YTD Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_accessories_ytd)}%")
            style_metric_cards()
        with col6:
            pass

        tcc1, tcc2 = t3.columns(2)
        with tcc1:
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[current_gross_profit['mutation'].sum()],
                        name='Actual',
                        textposition='auto',
                        text=financial_format(current_gross_profit['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
                )
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[income_budget_accessories['mutation'].sum()],
                        name='Budget',
                        textposition='auto',
                        text=financial_format(income_budget_accessories['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
                )
            fig.add_trace(
                    go.Bar(
                        x=["Gross Profit"],
                        y= [prev_gross_profit['mutation'].sum()],
                        name='Last Month',
                        textposition='auto',
                        text=financial_format(prev_gross_profit['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.update_layout(
                    barmode='group',
                    xaxis_title='',
                    yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'Current Gross Profit (Loss) (Rp. Million)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            tcc1.plotly_chart(fig,use_container_width=True,key="Current Gross Profit (Loss) (Rp. Million)_1")
        
        with tcc2:
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[current_gross_profit_ytd],
                        name='Actual',
                        textposition='auto',
                        text=financial_format(current_gross_profit_ytd/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )
            
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[income_budget_accessories_ytd['mutation'].sum()],
                        name='Budget',
                        textposition='auto',
                        text=financial_format(income_budget_accessories_ytd['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.add_trace(
                    go.Bar(
                        x=["Gross Profit"],
                        y= [prev_gross_profit_ytd],
                        name='Last Year',
                        textposition='auto',
                        text=financial_format(prev_gross_profit_ytd/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.update_layout(
                    barmode='group',
                    xaxis_title='',
                    yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'YTD Gross Profit (Loss) (Rp. Million)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            tcc2.plotly_chart(fig,use_container_width=True,key="YTD Gross Profit (Loss) (Rp. Million)_1")
    with t4:
        # Sparepart
        t4.markdown('<h2 class="section-title">Sparepart - Gross Profit (Loss)</h2>',unsafe_allow_html=True)

        # gross_profit_sparepart = gross_profit[gross_profit['ProfitCenterCode'] == '00005']
        gross_profit_sparepart = gross_profit.filter(pl.col('ProfitCenterCode') == '00005')
        # current_gross_profit = gross_profit_sparepart[gross_profit_sparepart['PeriodMonth'] == selected_month]
        current_gross_profit = gross_profit_sparepart.filter(pl.col('PeriodMonth') == selected_month)
        # prev_gross_profit = gross_profit_sparepart[~(gross_profit_sparepart['PeriodMonth'] == selected_month)]
        prev_gross_profit = gross_profit_sparepart.filter(pl.col('PeriodMonth') != selected_month)

        # income_budget_sparepart = income_budget_gross_profit[income_budget_gross_profit['ProfitCenterCode'] == '00005']
        income_budget_sparepart = income_budget_gross_profit.filter(pl.col('ProfitCenterCode') == '00005')
        # income_budget_sparepart = income_budget_sparepart[income_budget_sparepart['PeriodMonth'] == selected_month]
        income_budget_sparepart = income_budget_sparepart.filter(pl.col('PeriodMonth') == selected_month)
        

#         "CompanyCode":"Int64"
# "CompanyName":"String"
# "CompanyAbbreviation":"String"
# "PeriodYear":"String"
# "PeriodMonth":"String"
# "AccountNumber":"String"
# "AccountDescription":"String"
# "AccountType":"String"
# "Group1":"String"
# "DebitAmount":"Int64"
# "CreditAmount":"Int64"
# "Brand":"String"
# "ProfitCenterCode":"String"
# "ProfitCenter":"String"
# "CompanArGroupyCode":"String"
# "mutation":"Int64"
        if income_budget_sparepart.is_empty():
            empty_income_budget_sparepart = pl.DataFrame(
                schema={
                    'CompanyCode': pl.Int64,
                    'CompanyName': pl.Utf8,
                    'CompanyAbbreviation': pl.Utf8,
                    'PeriodYear': pl.Utf8,
                    'PeriodMonth': pl.Utf8,
                    'AccountNumber': pl.Utf8,   
                    'AccountDescription': pl.Utf8,
                    'AccountType': pl.Utf8,
                    'Group1': pl.Utf8,
                    'DebitAmount': pl.Int64,
                    'CreditAmount': pl.Int64,
                    'Brand': pl.Utf8,
                    'ProfitCenterCode': pl.Utf8,
                    'ProfitCenter': pl.Utf8,
                    'CompanArGroupyCode': pl.Utf8,
                    'mutation': pl.Int64
                }
            )
            income_budget_sparepart = empty_income_budget_sparepart
        if selected_brand != 'ALL':
            # income_budget_sparepart = income_budget_sparepart[income_budget_sparepart['Brand'] == selected_brand]
            income_budget_sparepart = income_budget_sparepart.filter(pl.col('Brand') == selected_brand)

        # gross_profit_sparepart_last_year = gross_profit_last_year[(gross_profit_last_year['ProfitCenterCode'] == '00005') & (gross_profit_last_year['PeriodMonth'] == selected_month)]
        gross_profit_sparepart_last_year = gross_profit_last_year.filter((pl.col('ProfitCenterCode') == '00005') & (pl.col('PeriodMonth') == selected_month))
        current_gross_profit_ytd = current_gross_profit['EndAmount'].sum()
        prev_gross_profit_ytd = gross_profit_sparepart_last_year['EndAmount'].sum()

        # income_budget_sparepart_ytd = income_budget_gross_profit[income_budget_gross_profit['ProfitCenterCode'] == '00005']
        income_budget_sparepart_ytd = income_budget_gross_profit.filter(pl.col('ProfitCenterCode') == '00005')
        # income_budget_sparepart_ytd = income_budget_sparepart_ytd[income_budget_sparepart_ytd['PeriodMonth'].isin(month_to_proceed)]
        income_budget_sparepart_ytd = income_budget_sparepart_ytd.filter(pl.col('PeriodMonth').is_in(month_to_proceed))
        
        spare_sum = income_budget_sparepart['mutation'].sum()
        spare_sum_ytd = income_budget_sparepart_ytd['mutation'].sum()
        if spare_sum != 0:
            percent_budget_gross_profit_sparepart = round(current_gross_profit['mutation'].sum() / spare_sum * 100, 2)
        else:
            percent_budget_gross_profit_sparepart = 0
        if spare_sum_ytd != 0:
            percent_budget_gross_profit_sparepart_ytd = round(current_gross_profit_ytd / spare_sum_ytd * 100, 2)
        else:
            percent_budget_gross_profit_sparepart_ytd = 0

        col1, col2, col3, col4, col5, col6 = t4.columns((1,2,1,1,2,1))
        with col1:
            pass
        with col2:
            col2.metric('% Current Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_sparepart)}%")
            style_metric_cards()
        with col3:
            pass
        with col4:
            pass
        with col5:
            col5.metric('% YTD Gross Profit (Loss) Budget',value=f"{financial_format(percent_budget_gross_profit_sparepart_ytd)}%")
            style_metric_cards()
        with col6:
            pass

        tcc1, tcc2 = t4.columns(2)
        with tcc1:
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[current_gross_profit['mutation'].sum()],
                        name='Actual',
                        textposition='auto',
                        text=financial_format(current_gross_profit['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
                )
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[income_budget_sparepart['mutation'].sum()],
                        name='Budget',
                        textposition='auto',
                        text=financial_format(income_budget_sparepart['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}")
                )
            fig.add_trace(
                    go.Bar(
                        x=["Gross Profit"],
                        y= [prev_gross_profit['mutation'].sum()],
                        name='Last Month',
                        textposition='auto',
                        text=financial_format(prev_gross_profit['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.update_layout(
                    barmode='group',
                    xaxis_title='',
                    yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'Current Gross Profit (Loss) (Rp. Million)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            tcc1.plotly_chart(fig,use_container_width=True,key="Current Gross Profit (Loss) (Rp. Million)_2")
        
        with tcc2:
            fig = go.Figure()
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[current_gross_profit_ytd],
                        name='Actual',
                        textposition='auto',
                        text=financial_format(current_gross_profit_ytd/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )
            
            fig.add_trace(
                    go.Bar(x=["Gross Profit"],
                        y=[income_budget_sparepart_ytd['mutation'].sum()],
                        name='Budget',
                        textposition='auto',
                        text=financial_format(income_budget_sparepart_ytd['mutation'].sum()/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.add_trace(
                    go.Bar(
                        x=["Gross Profit"],
                        y= [prev_gross_profit_ytd],
                        name='Last Year',
                        textposition='auto',
                        text=financial_format(prev_gross_profit_ytd/1000000),
                        hoverlabel=dict(
                            bgcolor="white",
                            font_size=15
                        ),
                        hovertemplate="<b>%{x}</b><br>Rp.%{text}"
                    )
                )

            fig.update_layout(
                    barmode='group',
                    xaxis_title='',
                    yaxis_title='Gross Profit (Loss) Amount (Rp. Million)',
                    legend_title='',
                    template='simple_white',
                    yaxis_tickprefix = '', 
                    yaxis_tickformat = '',
                    title = 'YTD Gross Profit (Loss) (Rp. Million)',
                    font = dict(size=15),
                    yaxis=dict(tickfont=dict(size=15)),
                    xaxis=dict(tickfont=dict(size=15))
                )       

            tcc2.plotly_chart(fig,use_container_width=True,key="YTD Gross Profit (Loss) (Rp. Million)_2")