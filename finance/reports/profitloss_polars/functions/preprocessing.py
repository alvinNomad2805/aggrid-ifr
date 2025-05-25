from reports.profitloss_polars.functions.creategroup import create_group
import polars as pl

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
    data_source = data_source.with_columns(
        pl.col("PeriodMonth").map_elements(lambda x: month_mapping.get(x, "Unknown"), return_dtype=str).alias("Month")
    )

    #generate +- of amount
    data_source = data_source.with_columns(
        (pl.col("EndAmount") * -1).alias("EndAmount")
    )
    data_source = data_source.with_columns(
        (pl.col("MutationAmount") * -1).alias("MutationAmount")
    )
    data_company_console_list = data_company_console['console_combine_name'].unique().tolist()
    data_source = data_source.filter(
        ~pl.col("CompanyName").is_in(data_company_console_list)
    )
    data_source = data_source.with_columns(
        (pl.col("Brand").str.strip_chars().str.to_uppercase()).alias("Brand")
    )
    data_source = data_source.with_columns(
        (pl.col("ProfitCenter").str.strip_chars().str.to_uppercase()).alias("ProfitCenter")
    )
    data_source = data_source.with_columns(
        (pl.col("AccountType").str.strip_chars()).alias("AccountType")
    )
    data_source = data_source.with_columns(
        (pl.col("ArGroup").str.strip_chars()).alias("ArGroup")
    )
    data_source = data_source.with_columns(
        (pl.col("Group1").cast(pl.String)).alias("Group1")
    )
    data_source = data_source.with_columns(
        (pl.col("Group1").cast(pl.String)).alias("Group1")
    )
    data_source = data_source.with_columns(
        pl.when(pl.col("Brand") == 'OTHBRN2')
        .then(pl.lit('OTHBRN2 - MCA'))
        .otherwise(pl.col("Brand"))
        .alias("Brand")
    )
    data_source = data_source.to_pandas()
    return data_source