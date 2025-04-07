import calendar
import datetime
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
import numpy as np

# @st.cache_data()
def load_data():
    data = pd.read_csv("./new_data_mapping_ifr.csv", sep=",")
    return data

data = load_data()

st.set_page_config(page_title='IFR test report',layout='wide',initial_sidebar_state='expanded')

h1,h2,h3,h4= st.columns(4)
today = datetime.datetime.now()
if today.month - 1 == 0:
    default_month_index = 11
    default_year = today.year - 1
else:
    default_month_index = today.month - 2 # previous month
    # default_month_index = today.month - 1 # current month
    default_year = today.year
with h1:
    list_year = [today.year, today.year - 1]
    select_year = h1.selectbox("Year", list_year, index=list_year.index(default_year), key="year")
    data = data[data["period_year"] == select_year]
with h2:
    list_month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    select_month = h2.selectbox("Month", list_month, index=default_month_index, key="month_start")
    month_dict = dict((v, k) for k, v in enumerate(calendar.month_name))
    selected_month = month_dict[select_month]   
    selected_month = "0"+ str(selected_month) if len(str(selected_month)) < 2 else str(selected_month)
    data = data[data["period_month"] == select_month]
with h3:
    brands = data["brand"].unique()
    selected_brands = h3.multiselect("Brand", brands)
    if selected_brands:
        data = data[data["brand"].isin(selected_brands)]
with h4:
    companies = data["company"].unique()
    selected_companies = h4.multiselect("Company", companies)
    if selected_companies:
        data = data[data["company"].isin(selected_companies)]

shouldDisplayPivoted = st.checkbox("Pivot data on Reference Date")

gb = GridOptionsBuilder()

gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=False,
)
gb.configure_column(
    field="level_1", 
    header_name="Level 1",
    width=80, 
    rowGroup=shouldDisplayPivoted
)

gb.configure_column(
    field="level_2",
    header_name="Level 2",
    flex=1,
    tooltipField="Level 2",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="level_3",
    header_name="Level 3",
    flex=1,
    tooltipField="Level 3",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="level_4",
    header_name="Level 4",
    flex=1,
    tooltipField="Level 4",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="level_5",
    header_name="Level 5",
    flex=1,
    tooltipField="Level 5",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="level_6",
    header_name="Level 6",
    flex=1,
    tooltipField="Level 6",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="level_7",
    header_name="Level 7",
    flex=1,
    tooltipField="Level 7",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="company",
    header_name="company",
    width=100,
    # valueFormatter="value != undefined ? new Date(value).toLocaleString('en-US', {dateStyle:'medium'}): ''",
    pivot=True,
    hide=False,
)

gb.configure_column(
    field="brand",
    header_name="brand",
    # valueGetter="new Date(data.referenceDate).getFullYear()",
    pivot=True,
    hide=False,
)

gb.configure_column(
    "type",
    header_name="Type",
    pivot=True,         # <-- Pivot on the 'type' field
    rowGroup=False      # Usually no need to group by 'type' if we are pivoting it
)

# Make 'mutation' the numeric field to aggregate
gb.configure_column(
    "mutation",
    pivotValueColumn=True,
    pivotValueName="",  # remove the label so columns become just "Actual", "Budget"
    header_name="",     # no header for the pivot value
    aggFunc="sum",
    type=["numericColumn"]
)

gb.configure_grid_options(
    tooltipShowDelay=0,
    pivotMode=shouldDisplayPivoted,
)

gb.configure_grid_options(
    autoGroupColumnDef=dict(
        minWidth=300, 
        pinned="left", 
        cellRendererParams=dict(suppressCount=True)
    ),
    suppressAggFuncInHeader = True,
    groupDefaultExpanded = 7,
)
go = gb.build()

st.write(data)

AgGrid(data, gridOptions=go,fit_columns_on_grid_load=True,height=400)