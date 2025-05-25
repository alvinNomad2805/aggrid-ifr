import pandas as pd

def calculate(data_source, domain, groupby:list, field_to_calculate:str):
    data_source[field_to_calculate] = pd.to_numeric(data_source[field_to_calculate], errors='coerce')

    raw_data_income = data_source[data_source['Group1'] == '4'].groupby(groupby)[field_to_calculate].sum().reset_index(name='income')
    raw_data_cogs = data_source[data_source['Group1'] == '5'].groupby(groupby)[field_to_calculate].sum().reset_index(name='cogs')
    raw_data_expense = data_source[data_source['Group1'] == '6'].groupby(groupby)[field_to_calculate].sum().reset_index(name='expense')
    raw_data_otherinex = data_source[~data_source['Group1'].isin(['4', '5', '6'])].groupby(groupby)[field_to_calculate].sum().reset_index(name='other_income_expense')
    profit_loss_summary = pd.merge(domain, raw_data_income, how='left', on=groupby)
    profit_loss_summary = pd.merge(profit_loss_summary, raw_data_cogs, how='left', on=groupby)
    profit_loss_summary = pd.merge(profit_loss_summary, raw_data_expense, how='left', on=groupby)
    profit_loss_summary = pd.merge(profit_loss_summary, raw_data_otherinex, how='left', on=groupby)
    profit_loss_summary.fillna({'income': 0, 'cogs': 0,'expense': 0, 'other_income_expense': 0}, inplace=True)
    profit_loss_summary = profit_loss_summary.assign(gross_profit = profit_loss_summary["income"] + profit_loss_summary["cogs"])
    profit_loss_summary = profit_loss_summary.assign(net_operating_profit = profit_loss_summary["gross_profit"] + profit_loss_summary["expense"])
    profit_loss_summary = profit_loss_summary.assign(net_profit = profit_loss_summary["net_operating_profit"] + profit_loss_summary["other_income_expense"])

    return profit_loss_summary