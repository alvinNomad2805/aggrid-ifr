import polars as pl

def create_group(raw_data):
    raw_data = raw_data.with_columns(pl.col("AccountNumber").str.slice(0, 2).alias("AccountNumber2"))
    identify = {'41': ['4 - SALES', '41 - Gross Sales'],
                '42': ['4 - SALES', '42 - Sales Discount'],
                '43': ['4 - SALES', '43 - Sales Return'],
                '51': ['5 - COST OF GOOD SOLD', '51 - Cost Of Goods Sold'],
                '55': ['5 - COST OF GOOD SOLD', '55 - Basic Expense'],
                '61': ['6 - OPERATIONAL EXPENSE', '61 - Selling Expense'],
                '62': ['6 - OPERATIONAL EXPENSE', '62 - General and Administrative Expenses'],
                '71': ['7 - OTHER INCOME', '71 - Subsidiary Profit and Loss'],
                '72': ['7 - OTHER INCOME', '72 - Financial Income'],
                '75': ['7 - OTHER INCOME', '75 - Other Income'],
                '76': ['8 - OTHER EXPENSE', '76 - Financial Expense'],
                '79': ['8 - OTHER EXPENSE', '79 - Other Expense'],
                '81': ['8 - OTHER EXPENSE', '81 - Tax Expense'],
                '82': ['8 - OTHER EXPENSE', '82 - Deffered Tax'],
                '83': ['8 - OTHER EXPENSE', '81 - Tax Expense'],
                '91': ['8 - OTHER EXPENSE', '91 - Minority share of non-controlling interests'],
                '94': ['8 - OTHER EXPENSE', '94 - Recognition of the fair value of assets when transferred'],
                '95': ['8 - OTHER EXPENSE', '95 - Comprehensive income'],
                '97': ['8 - OTHER EXPENSE', '82 - Deffered Tax']
                }
    
    raw_data = raw_data.with_columns(
        pl.col("AccountNumber2").map_elements(lambda x: identify.get(x, ["Unknown", "Unknown"])[0], return_dtype=str).alias("Group")
    )
    raw_data = raw_data.with_columns(
        pl.col("AccountNumber2").map_elements(lambda x: identify.get(x, ["Unknown", "Unknown"])[1], return_dtype=str).alias("Group2")
    )
    return raw_data