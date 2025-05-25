import pandas as pd

def melt(input_data_frame,id_var:list):
    if id_var == None:
        list_columns = list(input_data_frame.columns)
    else:
        list_columns = id_var
    value = []
    for i in range(0,len(list_columns)):
        value.append(input_data_frame[list_columns[i]].sum())
    data_object = {
        'variable':list_columns,
        'value':value
    }
    return data_object
