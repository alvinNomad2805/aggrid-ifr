from reports.profitloss.functions.creategroup import create_group
import numpy as np

def preprocessing(data_source, data_company_console):
    month_mapping = {
                '01': 'January',
                '02': 'February',
                '03': 'March',
                '04': 'April',
                '05': 'May',
                '06': 'June',
                '07': 'July',
                '08': 'August',
                '09': 'September',
                '10': 'October',
                '11': 'November',
                '12': 'December',
            }
    
    data_source = create_group(data_source)
    data_source['Month'] = data_source['PeriodMonth'].map(month_mapping)

    #generate +- of amount
    data_source['EndAmount'] = data_source['EndAmount'] * -1
    data_source['MutationAmount'] = data_source['MutationAmount'] * -1
    data_company_console_list = data_company_console['console_combine_name'].unique().tolist()
    data_source = data_source[~data_source['CompanyName'].isin(data_company_console_list)]
    data_source.loc[:, 'Brand'] = data_source['Brand'].str.upper().str.strip()
    data_source.loc[:, 'ProfitCenter'] = data_source['ProfitCenter'].str.upper().str.strip()
    data_source.loc[:, 'AccountType'] = data_source['AccountType'].str.strip()
    data_source.loc[:, 'ArGroup'] = data_source['ArGroup'].str.strip()
    data_source = data_source.astype({'Group1': 'object'})
    data_source.loc[:, 'Group1'] = data_source['Group1'].astype(str)
    data_source.loc[data_source['Brand'] == 'OTHBRN2', 'Brand'] = 'OTHBRN2 - MCA'
    
    return data_source