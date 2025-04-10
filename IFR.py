from io import BytesIO
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title='IFR test report',layout='wide',initial_sidebar_state='expanded')

st.title('Indomobil Financial Reports')

c1,c2,c3,c4 = st.columns(4)

@st.cache_data(ttl=3600)
def load_data():
    data = pd.read_parquet('raw_data.parquet')
    return data

def convert_df_to_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

data = load_data()

manual_order = ['I. OUTLET',
                'II. VOLUME (in unit)',
                'III. STATEMENTS OF COMPREHENSIVE INCOME (in Rp full amount)',
                'IV. STATEMENTS OF FINANCIAL POSITION (in Rp full amount)',
                'V. TOTAL MAN POWER',
                'VI.RATIO ANALYSIS']

data['level_1'] = pd.Categorical(data['level_1'],categories=manual_order,ordered=True)
data = data.sort_values('level_1')

list_year = data['period_year'].unique().tolist()
month_mapping = {
    '01':'January',
    '02':'February',
    '03':'March',
    '04':'April',
    '05':'May',
    '06':'June',
    '07':'July',
    '08':'August',
    '09':'September',
    '10':'October',
    '11':'November',
    '12':'December',
}
list_month_nums = sorted(data["period_month"].unique().tolist())
list_month_names = [month_mapping[month] for month in list_month_nums]
list_companies = data['company'].unique().tolist()
list_brands = data['brand'].unique().tolist()

with c1:
    selected_year = c1.selectbox('Period Year',list_year)
    if selected_year:
        data = data[data['period_year'] == selected_year]
with c2:
    selected_month_name = c2.selectbox('Period Month', list_month_names)
    selected_month = list(month_mapping.keys())[list(month_mapping.values()).index(selected_month_name)]
    if selected_month:
        data = data[data['period_month'] == selected_month]
with c3:
    pass
with c4:
    pass

selected_companies = st.multiselect('Select Company(ies) (multi selection)',list_companies)
if selected_companies != []:
    data = data[data['company'].isin(selected_companies)]
selected_brand = st.multiselect('Select Brand(s) (multi selection)',list_brands)
if selected_brand != []:
    data = data[data['brand'].isin(selected_brand)]

tabs = st.tabs(['Detail Summary','Detail Percentage'])

with tabs[0]:
    st.subheader('IFR summary and detail')
    shouldDisplayPivoted = True

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
        pivot=True,
        hide=False,
    )

    gb.configure_column(
        field="brand",
        header_name="brand",
        pivot=True,
        hide=False,
    )

    gb.configure_column(
        field="period_year",
        header_name="Year",
        pivot=False,
        hide=False,
    )

    gb.configure_column(
        field="period_month",
        header_name="Month",
        pivot=False,
        hide=False,
    )

    gb.configure_column(
        field="value_type",
        header_name="Type",
        pivot=True,
        hide=False,
    )

    # gb.configure_column(
    #     field="mutation_value",
    #     header_name="Total",
    #     width=150,
    #     type=["numericColumn"],
    #     aggFunc="sum",
    #     valueFormatter="value.toLocaleString()",
    # )

    gb.configure_column(
        field="ytd_value",
        header_name="Total",
        width=150,
        type=["numericColumn"],
        aggFunc="sum",
        valueFormatter="value.toLocaleString()",
    )

    gb.configure_grid_options(
        tooltipShowDelay=0,
        pivotMode=shouldDisplayPivoted,
        autoGroupColumnDef=dict(
            minWidth=300, 
            pinned="left", 
            cellRendererParams=dict(suppressCount=True)
        ),
        pivotDefaultExpanded = -1,
        autoSizeStrategy=dict(
            type= 'fitCellContents'
        ),
        autoSizeAllColumns = True,
        suppressAggFuncInHeader = True,
    )
    go = gb.build()

    output = AgGrid(data, gridOptions=go,fit_columns_on_grid_load=False,height=700)
    excel_data = convert_df_to_excel(data)

    st.download_button(
        label="📤 Download Excel",
        data=excel_data,
        file_name='aggrid_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
with tabs[1]:
    st.subheader('Percentage Summary')
    data = {
        "Group":['Unit Sales'],
        "Company":["Indomobil Trada Nasional - MT Haryono"],
        "Brand":["Nissan"],
        "Year":["2024"],
        "Month":["04"],
        "Percentage":[43]

    }
    df = pd.DataFrame(data=data)
    st.dataframe(df)