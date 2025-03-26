import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# @st.cache_data()
def load_data():
    data = pd.read_csv("./coba.csv", sep=";")
    return data

data = load_data()

shouldDisplayPivoted = st.checkbox("Pivot data on Reference Date")

gb = GridOptionsBuilder()

gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=False,
)
gb.configure_column(
    field="section", header_name="section", width=80, rowGroup=shouldDisplayPivoted
)

gb.configure_column(
    field="subsection",
    header_name="subsection",
    flex=1,
    tooltipField="subsection",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="subsubsection",
    header_name="subsubsection",
    flex=1,
    tooltipField="subsubsection",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="subsubsubsection",
    header_name="subsubsubsection",
    flex=1,
    tooltipField="subsubsubsection",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="subsubsubsubsection",
    header_name="subsubsubsubsection",
    flex=1,
    tooltipField="subsubsubsubsection",
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
    hide=True,
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

AgGrid(data, gridOptions=go, height=400)