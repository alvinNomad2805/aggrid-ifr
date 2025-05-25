import requests
import pandas as pd
import time
import datetime


if __name__ == '__main__':
    try:
        while (True):
            current_year = datetime.datetime.now().year
            current_month = datetime.datetime.now().month
            for ch in range(1,current_month+1):
                data_complete = None
                if ch >=10:
                    get_month = str(ch)
                else:
                    get_month = '0' + str(ch)
                print(get_month)
                print("getting new data --- refreshed (Ctrl + C to terminate)")
                query_check = f'http://172.16.5.5:5000/ifr-new-format2?period_year={current_year}&period_month={get_month}'
                print('query check --> ' + query_check)
                url = requests.get(query_check)
                data = url.json()['Data']
                data_complete = pd.DataFrame(data)
                print('panjang data : ' + str(len(data_complete)))
                data_to_parquet = data_complete.to_parquet(f'raw_data_{current_year}_{get_month}.parquet')
                print(f'collected period year = {current_year} and period month = {get_month}')
            print('finished....')
            time.sleep(86400)
    except KeyboardInterrupt:
        print('scheduler terminated...')
