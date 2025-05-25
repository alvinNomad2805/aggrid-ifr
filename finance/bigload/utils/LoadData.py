import requests
import pandas as pd
import datetime
import os

def load_data(pagetype):
    # try:
    #     server  = "http://localhost:5000"
    #     read_data = requests.get(server+pagetype)
    #     print(f"hit-url: {server+pagetype}")
    # except:
    server = "http://172.16.5.5:5000"
    read_data = requests.get(server+pagetype)
    print(f"hit-url: {server+pagetype}")
    return read_data.json()

def profit_loss_process():
    today = datetime.datetime.now()
    year_list = [today.year-1, today.year]
    month_list = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13']
    list_df = []

    for year in year_list:
        for month in month_list:
            get_data = load_data(f"/profit-loss-view?year={str(year)}&month={month}")
            get_data = pd.DataFrame(get_data)
            list_df.append(get_data)
            if month == ("0" + str(today.month) if len(str(today.month)) < 2 else str(today.month)):
                break

    # results_old = pd.concat(list_df)
    # results_old.to_csv('profit_loss.tsv', sep="\t")