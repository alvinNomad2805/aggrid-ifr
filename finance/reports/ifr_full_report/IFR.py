from io import BytesIO
import streamlit as st
import pandas as pd
import polars as pl
from st_aggrid import AgGrid, GridOptionsBuilder
import os
import datetime

def exclude_company_filter(list_company):
    path = os.path.join(os.getcwd(),'reports','ifr_full_report') 
    no_dms = pl.read_csv(os.path.join(path,'company_no_dms.txt'),columns='no_dms_companies') # no dms companies
    closed = pl.read_csv(os.path.join(path,'company_closed.txt'),columns='closed_companies') # closed companies
    indep = pl.read_csv(os.path.join(path,'company_independent.txt'),columns='independent_companies') # independent companies
    no_dms = no_dms['no_dms_companies'].to_list()
    closed = closed['closed_companies'].to_list()
    indept = indep['independent_companies'].to_list()
    filtered_companies = list_company.filter(~pl.col('Company').str.contains("|".join(no_dms),strict=False))
    filtered_companies = filtered_companies.filter(~pl.col('Company').str.contains("|".join(closed),strict=False))
    filtered_companies = filtered_companies.filter(~pl.col('Company').str.contains("|".join(indept),strict=False))
    return filtered_companies
    


def ifr_full_report(userlogin, company_list, brand_list):
    st.title('Indomobil Financial Reports')
    main_path = os.getcwd()
    #get urutan
    cek_data = pl.read_excel(os.path.join(main_path,'reports','ifr_full_report','urutan_ifr.xlsx'))

    c1,c2,c3,c4 = st.columns(4)

    @st.cache_data(ttl=3600)
    def load_data(period_year:str,period_month:str):
        path_read = os.path.join(main_path,'reports','ifr_full_report',f'raw_data_{period_year}_{period_month}.parquet')
        data = pl.read_parquet(path_read)
        data_check = exclude_company_filter(data)
        return data_check

    def convert_df_to_excel(dataframe):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
        processed_data = output.getvalue()
        return processed_data

    current_year = datetime.datetime.now().year
    total_months = datetime.datetime.now().month
    list_months_append = []
    for get_month in range(1,total_months+1):
        if get_month >= 10:
            month_selected = str(get_month)
        else:
            month_selected = '0' + str(get_month)
        list_months_append.append(month_selected)


    list_year = str(current_year)

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
    list_month_nums = list_months_append

    list_month_names = [month_mapping[month] for month in list_month_nums]

    with c1:
        selected_year = c1.selectbox('Period Year',list_year)
    with c2:
        selected_month_name = c2.selectbox('Period Month', list_month_names)
        selected_month = list(month_mapping.keys())[list(month_mapping.values()).index(selected_month_name)]
    with c3:
        pass
    with c4:
        pass

    data = load_data(selected_year,selected_month)
    data = data.to_pandas()

    level_1 = cek_data[:,0].drop_nulls()
    data['LEVEL_1'] = pd.Categorical(data['LEVEL_1'],categories=level_1,ordered=True)

    level_2 = cek_data[:,1].drop_nulls()
    data['LEVEL_2'] = pd.Categorical(data['LEVEL_2'],categories=level_2,ordered=True)

    level_3 = cek_data[:,2].drop_nulls()
    data['LEVEL_3'] = pd.Categorical(data['LEVEL_3'],categories=level_3,ordered=True)

    level_4 = cek_data[:,3].drop_nulls()
    data['LEVEL_4'] = pd.Categorical(data['LEVEL_4'],categories=level_4,ordered=True)

    level_5 = cek_data[:,4].drop_nulls()
    data['LEVEL_5'] = pd.Categorical(data['LEVEL_5'],categories=level_5,ordered=True)

    level_6 = cek_data[:,5].drop_nulls()
    data['LEVEL_6'] = pd.Categorical(data['LEVEL_6'],categories=level_6,ordered=True)

    level_7 = cek_data[:,6].drop_nulls()
    data['LEVEL_7'] = pd.Categorical(data['LEVEL_7'],categories=level_7,ordered=True)

    # Define custom sort order            
    # brand_orders = ['ALL','NISSAN','KIA','JLR','SUZUKI','HINO','VW',
    #             'AUDI','CITROEN','GAC','AION','HARLEY DAVIDSON','MAXUS',
    #             'MERCEDES BENZ','E MOTOR','JEEP','OTHERS']

    # read from file
    full_path = os.path.join(main_path,'reports','ifr_full_report','new_column_brand_name.xlsx')
    brand_order_check = pd.read_excel(full_path,names=['key','value'])
    brand_order_check = brand_order_check.dropna(subset=["key", "value"])
    # Convert to dictionary
    mapping = dict(zip(brand_order_check["key"].str.strip(), brand_order_check["value"].str.strip()))       
    data['Brand'] = data['Brand'].replace(mapping)

    data = data.sort_values(['LEVEL_1','LEVEL_2','LEVEL_3','LEVEL_4','LEVEL_5','LEVEL_6','LEVEL_7','Brand'])
    

    list_companies = data['Company'].unique().tolist()
    list_brands = data['Brand'].unique().tolist()      

    selected_companies = st.multiselect('Select Company(ies) (multi selection)',list_companies,default=company_list)
    if selected_companies != []:
        data = data[data['Company'].isin(selected_companies)]

    selected_brand = st.multiselect('Select Brand(s) (multi selection)',list_brands)
    if selected_brand != []:
        data = data[data['Brand'].isin(selected_brand)]

    radio_selected = st.radio(label='Please select report type',options=['Year to Date','Current Month'])

    if radio_selected=='Year to Date':
        st.subheader('IFR Year to Date Report')
        shouldDisplayPivoted = True

        gb = GridOptionsBuilder()

        gb.configure_default_column(
            resizable=True,
            filterable=True,
            sortable=True,
            editable=False,
        )
        gb.configure_column(
            field="LEVEL_1", 
            header_name="Level 1", 
            width=80, 
            rowGroup=shouldDisplayPivoted
        )

        gb.configure_column(
            field="LEVEL_2",
            header_name="Level 2",
            flex=1,
            tooltipField="Level 2",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_3",
            header_name="Level 3",
            flex=1,
            tooltipField="Level 3",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_4",
            header_name="Level 4",
            flex=1,
            tooltipField="Level 4",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_5",
            header_name="Level 5",
            flex=1,
            tooltipField="Level 5",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_6",
            header_name="Level 6",
            flex=1,
            tooltipField="Level 6",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_7",
            header_name="Level 7",
            flex=1,
            tooltipField="Level 7",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="Company",
            header_name="company",
            width=100,
            pivot=True,
            hide=False,
        )

        gb.configure_column(
            field="Brand",
            header_name="brand",
            pivot=True,
            hide=False,
            sort=None
        )

        gb.configure_column(
            field="Period_Year",
            header_name="Year",
            pivot=False,
            hide=False,
        )

        gb.configure_column(
            field="Periode_Month",
            header_name="Month",
            pivot=False,
            hide=False,
        )

        gb.configure_column(
            field="Value_Type",
            header_name="Type",
            pivot=True,
            hide=False,
        )

        gb.configure_column(
            field="ytd_value",
            header_name="Total",
            width=150,
            type=["numericColumn","numberColumnFilter","customNumericFormat"],
            aggFunc="sum",
            valueFormatter='new Intl.NumberFormat("en-GB", { style: "decimal", minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(x)',
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

        AgGrid(data, gridOptions=go,fit_columns_on_grid_load=False,height=700)

    elif radio_selected=='Current Month':
        st.subheader('IFR Current Month Report')
        shouldDisplayPivoted = True

        gb = GridOptionsBuilder()

        gb.configure_default_column(
            resizable=True,
            filterable=True,
            sortable=True,
            editable=False,
        )
        gb.configure_column(
            field="LEVEL_1", 
            header_name="Level 1", 
            width=80, 
            rowGroup=shouldDisplayPivoted
        )

        gb.configure_column(
            field="LEVEL_2",
            header_name="Level 2",
            flex=1,
            tooltipField="Level 2",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_3",
            header_name="Level 3",
            flex=1,
            tooltipField="Level 3",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_4",
            header_name="Level 4",
            flex=1,
            tooltipField="Level 4",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_5",
            header_name="Level 5",
            flex=1,
            tooltipField="Level 5",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_6",
            header_name="Level 6",
            flex=1,
            tooltipField="Level 6",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="LEVEL_7",
            header_name="Level 7",
            flex=1,
            tooltipField="Level 7",
            rowGroup=True if shouldDisplayPivoted else False,
        )

        gb.configure_column(
            field="Company",
            header_name="company",
            width=100,
            pivot=True,
            hide=False,
        )

        gb.configure_column(
            field="Brand",
            header_name="brand",
            pivot=True,
            hide=False,
        )

        gb.configure_column(
            field="Period_Year",
            header_name="Year",
            pivot=False,
            hide=False,
        )

        gb.configure_column(
            field="Periode_Month",
            header_name="Month",
            pivot=False,
            hide=False,
        )

        gb.configure_column(
            field="Value_Type",
            header_name="Type",
            pivot=True,
            hide=False,
        )

        gb.configure_column(
            field="mutation_value",
            header_name="Total",
            width=150,
            type=["numericColumn","numberColumnFilter","customNumericFormat"],
            precision=2,
            aggFunc="sum",
            valueFormatter='new Intl.NumberFormat("en-GB", { style: "decimal", minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(x)',
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

    else:
        st.write('selection not valid')

    # st.download_button(
    #     label="📤 Download Excel",
    #     data=convert_df_to_excel(data),
    #     file_name='IFR-data-source.xlsx',
    #     mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # )
