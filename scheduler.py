import requests
import pandas as pd
import time


if __name__ == '__main__':
    try:
        while (True):
            print("getting new data --- refreshed (Ctrl + C to terminate)")
            url = requests.get('http://172.16.5.5:5000/ifr-new-format')
            data = url.json()['Data']
            data_complete = pd.DataFrame(data)
            data_to_parquet = data_complete.to_parquet('raw_data.parquet')
            print('finished....')
            time.sleep(86400)
    except KeyboardInterrupt:
        print('scheduler terminated...')