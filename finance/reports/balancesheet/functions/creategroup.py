def create_group(raw_data):
    raw_data['AccountNumber2'] = raw_data['AccountNumber'].str[:4]
    identify = {'1101': ['1 - ASSETS','11 - Current Assets','1101 - Cash and Bank'],
                '1102': ['1 - ASSETS','11 - Current Assets','1102 - Deposit'],
                '1103': ['1 - ASSETS','11 - Current Assets','1103 - Investment'],
                '1110': ['1 - ASSETS','11 - Current Assets','1110 - Account Receivable - Trade'],
                '1120': ['1 - ASSETS','11 - Current Assets','1120 - Account receivable - Non Trade'],
                '1130': ['1 - ASSETS','11 - Current Assets','1130 - Intercompany Account - Debit'],
                '1140': ['1 - ASSETS','11 - Current Assets','1140 - Accrued Revenue'],
                '1150': ['1 - ASSETS','11 - Current Assets','1150 - Inventory'],
                '1152': ['1 - ASSETS','11 - Current Assets','1152 - Inventory for Production'],
                '1158': ['1 - ASSETS','11 - Current Assets','1158 - Good in Transit'],
                '1159': ['1 - ASSETS','11 - Current Assets','1159 - Stock Allowance'],
                '1160': ['1 - ASSETS','11 - Current Assets','1160 - Prepaid Tax'],
                '1161': ['1 - ASSETS','11 - Current Assets','1161 - Income Tax Bill'],
                '1170': ['1 - ASSETS','11 - Current Assets','1170 - Down Payment'],
                '1171': ['1 - ASSETS','11 - Current Assets','1171 - Prepaid Expenses'],
                '1210': ['1 - ASSETS','12 - Non Current Assets','1210 - Fixed Assets'],
                '1211': ['1 - ASSETS','12 - Non Current Assets','1211 - Accumulated depreciation Assets'],
                '1212': ['1 - ASSETS','12 - Non Current Assets','1212 - Investment Property'],
                '1213': ['1 - ASSETS','12 - Non Current Assets','1213 - Accumulation Depreciation Investment Property'],
                '1214': ['1 - ASSETS','12 - Non Current Assets','1214 - Intangible Assets'],
                '1215': ['1 - ASSETS','12 - Non Current Assets','1215 - Accumulated Amortization'],
                '1220': ['1 - ASSETS','12 - Non Current Assets','1220 - Asset Rights to Use'],
                '1221': ['1 - ASSETS','12 - Non Current Assets','1221 - Accumulated Depreciation Assets Rights to Use'],
                '1230': ['1 - ASSETS','12 - Non Current Assets','1230 - Stock Investment'],
                '1231': ['1 - ASSETS','12 - Non Current Assets','1231 - Stock Investment DP'],
                '1240': ['1 - ASSETS','12 - Non Current Assets','1240 - Accumulated Subsidiary Profits'],
                '1250': ['1 - ASSETS','12 - Non Current Assets','1250 - Deferred Tax Assets'],
                '1290': ['1 - ASSETS','12 - Non Current Assets','1290 - Other Assets'],
                '2110': ['2 - LIABILITIES','21 - Current Liabilities','2110 - Account Payable - Trade'],
                '2120': ['2 - LIABILITIES','21 - Current Liabilities','2120 - Account Payable - Non Trade'],
                '2121': ['2 - LIABILITIES','21 - Current Liabilities','2121 - Short term Loan - Bank'],
                '2122': ['2 - LIABILITIES','21 - Current Liabilities','2122 - Short term Loan - Non Bank'],
                '2123': ['2 - LIABILITIES','21 - Current Liabilities','2123 - Short term Loan - Obligation'],
                '2124': ['2 - LIABILITIES','21 - Current Liabilities','2124 - Long term Loan Bank Due in 1 Year'],
                '2125': ['2 - LIABILITIES','21 - Current Liabilities','2125 - Long term Loan Non Bank Due in 1 Year'],  
                '2126': ['2 - LIABILITIES','21 - Current Liabilities','2126 - Long Term Loan Obligation Due in 1 Year'],  
                '2127': ['2 - LIABILITIES','21 - Current Liabilities','2127 - Long Term Loan Obligation'], 
                '2128': ['2 - LIABILITIES','21 - Current Liabilities','2128 - Long Term Loan - Bank'], 
                '2130': ['2 - LIABILITIES','21 - Current Liabilities','2130 - Intercompany Accounts - Credit'], 
                '2140': ['2 - LIABILITIES','21 - Current Liabilities','2140 - Prepaid Income'], 
                '2160': ['2 - LIABILITIES','21 - Current Liabilities','2160 - Tax Payable'], 
                '2171': ['2 - LIABILITIES','21 - Current Liabilities','2171 - Accrued Expense'], 
                '2221': ['2 - LIABILITIES','22 - Non-current Liabilities','2221 - Long term bank debt'], 
                '2222': ['2 - LIABILITIES','22 - Non-current Liabilities','2222 - Long term non bank debt'], 
                '2223': ['2 - LIABILITIES','22 - Non-current Liabilities','2223 - Long Term Debt - Obligation'], 
                '2240': ['2 - LIABILITIES','22 - Non-current Liabilities','2240 - Accumulated share of subsidiary profits'], 
                '2241': ['2 - LIABILITIES','22 - Non-current Liabilities','2241 - Accumulated Losses of subsidiaries'], 
                '2242': ['2 - LIABILITIES','22 - Non-current Liabilities','2242 - Minority interest in Net Assets of Subsidiaries'], 
                '2250': ['2 - LIABILITIES','22 - Non-current Liabilities','2250 - Employee Benefits Liabilities'], 
                '2251': ['2 - LIABILITIES','22 - Non-current Liabilities','2251 - Deferred Tax Liabilities'], 
                '2261': ['2 - LIABILITIES','22 - Non-current Liabilities','2261 - Lease Liabilities - BOT Usage Rights Assets'], 
                '2290': ['2 - LIABILITIES','22 - Non-current Liabilities','2290 - Other Long-Term Liabilities'], 
                '3110': ['3 - EQUITY','31 - Capital','3110 - Paid Up Capital'], 
                '3210': ['3 - EQUITY','31 - Capital','3210 - Down payment paid up capital'], 
                '3520': ['3 - EQUITY','31 - Capital','3520 - Additional Paid Up Capital'], 
                '3310': ['3 - EQUITY','33 - Difference in the restructuring value','3310 - Difference in Entity Restructuring Value'], 
                '3410': ['3 - EQUITY','34 - Fixed asset revaluation difference','3410 - Other Equity Components – Initial Fair Value Recognition when fixed assets are transferred to Invest Properties'], 
                '3510': ['3 - EQUITY','35 - Difference in transaction changes in subsidiary equity','3510 - Difference in Transactions on Changes in Equity of Subsidiaries'], 
                '3550': ['3 - EQUITY','35 - Difference in transaction changes in subsidiary equity','3550 - Other equity component'],
                '3610': ['3 - EQUITY','36 - Retained Earning','3610 - (Profit) Loss Last Year'],
                '3620': ['3 - EQUITY','36 - Retained Earning','3620 - Dividend distribution'],
                '3630': ['3 - EQUITY','36 - Retained Earning','3630 - (Profit) Loss Current Year'],
                '3640': ['3 - EQUITY','36 - Retained Earning','3640 - (Profit) Loss Last Year Correction'],
                '3650': ['3 - EQUITY','36 - Retained Earning','3650 - Reserve Retained Earnings'],
                '3660': ['3 - EQUITY','36 - Retained Earning','3660 - Other Comprehensive Income'],
                '3660': ['3 - EQUITY','36 - Retained Earning','3660 - Other Comprehensive Income'],
                '7210': ['7 - OTHER INCOME','72 - Financial Income','7210 - Bank Interest Income'],
    }

    raw_data.loc[:,'Groupdesc1'] = raw_data['AccountNumber2'].map(lambda x: identify.get(x, ['Unknown', 'Unknown','Unknown'])[0])
    raw_data.loc[:,'Groupdesc2'] = raw_data['AccountNumber2'].map(lambda x: identify.get(x, ['Unknown', 'Unknown','Unknown'])[1])
    raw_data.loc[:,'Groupdesc3'] = raw_data['AccountNumber2'].map(lambda x: identify.get(x, ['Unknown', 'Unknown','Unknown'])[2])
    return raw_data

def create_group_fixed(raw_data):
    create_group_fixed = raw_data[(raw_data['AccountNumber'].str[:3] == '121') | 
                                  (raw_data['AccountNumber'].str[:3] == '122') |
                                  (raw_data['AccountNumber'].str[:3] == '123') |
                                  (raw_data['AccountNumber'].str[:3] == '124')]
    
    identify_fa = {
        '121':'Fixed Assets',
        '122':'Investment Property',
        '123':'Intangible Assets',
        '124':'Asset Right To Use'
    }
    create_new_group = create_group_fixed.copy()
    create_new_group['FAGroup'] = create_new_group['AccountNumber'].str[:3].map(lambda x: identify_fa.get(x,['NA']))
    return create_new_group