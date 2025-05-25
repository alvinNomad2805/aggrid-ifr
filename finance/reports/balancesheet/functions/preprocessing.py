from reports.balancesheet.functions import creategroup

def preprocessing(data_source):
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
                '12': 'December'
            }
    

    data_source = creategroup.create_group(data_source)
    data_source['Month'] = data_source['PeriodMonth'].map(month_mapping)

    return data_source