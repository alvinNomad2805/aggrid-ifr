import streamlit as st
import pandas as pd

def convert_to_excel(data_source: list, data_filename: list, username):
    with pd.ExcelWriter(f'data/tempfile/dashboard_{username}.xlsx') as writer:
        for data, filename in zip(data_source, data_filename):
            datetime_columns = [col for col in data.columns if data[col].dtypes == 'datetime64[ns, UTC]']
            if datetime_columns != None:
                for i in datetime_columns:
                    data.loc[:, i] = data[i].dt.tz_localize(None)
            if filename == 'ifr':
                data.to_excel(writer, sheet_name=f'{filename}')
            else:
                data.to_excel(writer, sheet_name=f'{filename}', index=False)

def download_source(data_source: list, data_filename: list, page):
    username = st.session_state['name']
    convert_to_excel(data_source, data_filename, username)

    with open(f"data/tempfile/dashboard_{username}.xlsx", "rb") as file:
        download_button = st.download_button(label='Download Data',
                                data = file,
                                file_name=f'dashboard_{page}.xlsx',
                                mime="application/vnd.ms-excel")
        if download_button:
            st.toast('Data source have succesfully downloaded!', icon='⬇️')