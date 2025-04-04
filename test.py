import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title='IFR test report',layout='wide',initial_sidebar_state='expanded')

@st.cache_data()
def load_data():
    data = pd.read_excel("coba2.xlsx")
    return data



data = load_data()
print(data)

shouldDisplayPivoted = st.checkbox("Check the detail IFR")

gb = GridOptionsBuilder()

gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=False,
)
gb.configure_column(
    field="level_1", header_name="Level 1", width=80, rowGroup=shouldDisplayPivoted
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
    field="period_year",
    header_name="Year",
    # valueGetter="new Date(data.referenceDate).getFullYear()",
    pivot=True,
    hide=False,
)

gb.configure_column(
    field="period_month",
    header_name="Month",
    # valueGetter="new Date(data.referenceDate).getFullYear()",
    pivot=True,
    hide=False,
)

gb.configure_column(
    field="value_type",
    header_name="Type",
    # valueGetter="new Date(data.referenceDate).getFullYear()",
    pivot=True,
    hide=False,
)

gb.configure_column(
    field="total",
    header_name="total",
    width=100,
    type=["numericColumn"],
    aggFunc="sum",
    # valueFormatter="value.toLocaleString()",
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
    )
)
go = gb.build()

AgGrid(data, gridOptions=go,fit_columns_on_grid_load=True,height=700)