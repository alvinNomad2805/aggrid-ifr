import requests
import pandas as pd


url = requests.get('http://172.16.5.5:5000/ifr-new-format')
data = url.json()['Data']
data_complete = pd.DataFrame(data)
data_to_parquet = data_complete.to_parquet('raw_data.parquet')