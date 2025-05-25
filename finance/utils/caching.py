from datetime import datetime, date
import os
import pandas as pd
import polars as pl
from data.LoadData import load_data
import polars as pl
from streamlit.runtime.scriptrunner import add_script_run_ctx

def refresh_data():
    parquet_make("raw_data/ifr-unit-performance.parquet",
                 "/ifr-unit-performance?company_name=Indo Sentosa Trada - Puri&year=2024")
    parquet_make("raw_data/ifr-income-statement.parquet",
                 "/ifr-income-statement?period_year=2024&period_month=12&company_name=Indo Sentosa Trada - Puri")

def merge_parquet(dirname, startswith):
    files = os.listdir(dirname)

    merge = [f"{dirname}/{file}" for file in files if file.startswith(startswith)]

    merged = pl.read_parquet(merge)
    merged.write_parquet(f"{dirname}/{startswith}merged.parquet")

    return merged

def parquet_make(filename, query_url, get_slice="Data"):
    raw_data = load_data(query_url)
    if get_slice:
        raw_data = pl.DataFrame(raw_data[get_slice])
    else:
        raw_data = pl.DataFrame(raw_data)
    raw_data.write_parquet(filename)
    return raw_data

def parquet_read(filename):
    if os.path.exists(filename):
        raw_data = pl.read_parquet(filename)
    else:
        raw_data = pl.DataFrame()
    return raw_data


def parquet(filename, query_url):
    if os.path.exists(filename):
        raw_data = pl.read_parquet(filename)
    else:
        raw_data = load_data(query_url)
        raw_data = pl.DataFrame(raw_data['Data'])
        raw_data.write_parquet(filename)
    return raw_data

def parquet_by_monthly(selected_year, selected_month, filename, query_url):
    now = datetime.now()
    current = date(year=now.year, month=now.month, day=1)
    selected = date(year=int(selected_year), month=int(selected_month), day=1)

    if current < selected:
        return pl.DataFrame()
    
    if current == selected:
        raw_data = load_data(query_url)
        raw_data = pl.DataFrame(raw_data['Data'])
    else:
        if os.path.exists(filename):
            raw_data = pl.read_parquet(filename)
        else:
            raw_data = load_data(query_url)
            raw_data = pl.DataFrame(raw_data['Data'])
            raw_data.write_parquet(filename)
    return raw_data

def parquet_by_yearly(selected_year, filename, query_url):
    now = datetime.now()
    current = date(year=now.year, month=1, day=1)
    selected = date(year=int(selected_year), month=1, day=1)

    if current < selected:
        return pl.DataFrame()
    
    if current == selected:
        raw_data = load_data(query_url)
        raw_data = pl.DataFrame(raw_data['Data'])
    else:
        if os.path.exists(filename):
            raw_data = pl.read_parquet(filename)
        else:
            raw_data = load_data(query_url)
            raw_data = pl.DataFrame(raw_data['Data'])
            raw_data.write_parquet(filename)
    return raw_data