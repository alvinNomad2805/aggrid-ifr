import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
from reports.balancesheet.functions.currencyformat import finance_format
from utils.filter import financial_format
import math

def tabulation_finance_format(data:float):
    if np.isinf(float(data)) or np.isnan(float(data)):
        return "-"
    else:
        return 'Rp. {:,.2f}'.format(data)

def detail(raw_data,raw_data_sum,results):
    st.markdown('<h2 class="section-title">Detail Tabulation</h2>',unsafe_allow_html=True)
    
    st.subheader("Balance Sheet Detail Account")
    chart_data = raw_data
    f1,f2,f3 = st.columns(3)
    account_desc = raw_data['AccountDescription'].unique().tolist()
    header = raw_data['Groupdesc1'].unique().tolist()
    detail = raw_data['Groupdesc2'].unique().tolist()
    account_desc.insert(0,'Please select')
    header.insert(0,'Please select')
    detail.insert(0,'Please select')
    group_check = []
    with f1:
        filter_header = f1.selectbox('Header',options=header)
        if filter_header != "Please select":
            chart_data = (raw_data[raw_data['Groupdesc1'] == filter_header]).copy()
            group_check.append(filter_header)
    with f2:
        filter_detail = f2.selectbox('Detail',options=detail)
        if filter_detail != "Please select":
            chart_data = (raw_data[raw_data['Groupdesc2'] == filter_detail]).copy()
            group_check.append(filter_detail)
    with f3:
        filter_acc = f3.selectbox('Account Description',options=account_desc)
        if filter_acc != "Please select":
            chart_data = (raw_data[raw_data['AccountDescription'] == filter_acc]).copy()
            group_check.append(filter_acc)

    chart_data.rename(columns={
        "CompanyName":'Company Name',
        'AccountDescription':'Account Description',
        'AccountNumber':'Account Number',
        'Groupdesc1':'Header',
        'Groupdesc2':'Detail',
        'EndAmount':'End Amount'
    },inplace=True)

    tabulation_dataframe = chart_data[['Company Name','Account Description','Account Number','Header','Detail','End Amount']]
    results_tabulation = (tabulation_dataframe.groupby(by=['Company Name','Account Description','Account Number','Header','Detail']).sum()).reset_index()
    results_tabulation = results_tabulation.sort_values(by='Account Number',ascending=True).reset_index()
   
    headerColor = '#0068c9'
    rowEvenColor = '#A0DEFF'
    rowOddColor = 'white'

    fig = go.Figure(data=[go.Table(
    header=dict(
        values=['<b>Company Name</b>','<b>Account Description</b>','<b>Account Number</b>','<b>Header</b>','<b>Detail</b>','<b>End Amount</b>'],
        line_color='darkslategray',
        fill_color=headerColor,
        align=['center','center', 'center', 'center','center','center'],
        font=dict(color='white', size=16)
    ),
    cells=dict(
        values= [results_tabulation['Company Name'],
                 results_tabulation['Account Description'],
                 results_tabulation['Account Number'],
                 results_tabulation['Header'],
                 results_tabulation['Detail'],
                 results_tabulation['End Amount'].apply(financial_format)],
        line_color='darkslategray',
        fill_color = [[rowOddColor,rowEvenColor]*math.ceil(len(results_tabulation)/2)],
        align = ['left', 'left', 'center', 'center','center','right'],
        height = 30,
        font = dict(color = 'black', 
                    size = 14)
        ))
    ])
    fig.update_layout(
        height=350,
        margin=dict(
            l=10,
            r=10,
            b=10,
            t=10
            )
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown('<h2 class="section-title">Fixed Assets Report</h2>',unsafe_allow_html=True)

    st.subheader("Fixed Asset")
    #get fixed assets
    try:
        fa_label_asset = results[(results['GroupAssets'] == 'Asset')&(results['AccountDescription'].str.contains('Aset Tetap -'))].copy()
        fa_label_asset['Account Description'] = fa_label_asset['AccountDescription'].apply(lambda x:x.split("- ")[1])
        fa_label_asset_total = fa_label_asset[['Account Description','EndAmount']]
        fa_label_asset_total_renamed = fa_label_asset_total.rename(columns={"EndAmount":"Asset"})
        fa_label_asset_total_amount = (fa_label_asset_total_renamed.groupby(by=['Account Description']).sum()).reset_index()

        fa_label_depreciation = results[(results['GroupAssets'].str.contains('depreciation',case=False))&(results['AccountDescription'].str.contains('Akumulasi Penyusutan -'))].copy()
        fa_label_depreciation['Account Description'] = fa_label_depreciation['AccountDescription'].apply(lambda x:x.split("- ")[1])
        fa_label_depreciation_total = fa_label_depreciation[['Account Description','EndAmount']]
        fa_label_depreciation_total_renamed = fa_label_depreciation_total.rename(columns={"EndAmount":"Accumulation Depreciation"})
        fa_label_depreciation_total_amount = (fa_label_depreciation_total_renamed.groupby(by=['Account Description']).sum()).reset_index()

        merged_join_test = pd.merge(fa_label_asset_total_amount,fa_label_depreciation_total_amount,on='Account Description',how="left")
        check_out_sum = merged_join_test.groupby(by=['Account Description']).sum().reset_index()
        check_out_sum['Book Value'] = check_out_sum['Asset'] + check_out_sum['Accumulation Depreciation']
        asset_total = np.sum(check_out_sum['Asset'])
        depreciation_total = np.sum(check_out_sum['Accumulation Depreciation'])
        grand_total = np.sum(check_out_sum['Book Value'])
        ff1,ff2,ff3 = st.columns(3)
        with ff1:
            ff1.metric("Asset Total",value=f"Rp. {finance_format(asset_total/1000000000,'B')}")
        with ff2:
            ff2.metric("Accumulation Depreciation Total",value=f"Rp. {finance_format(depreciation_total/1000000000,'B')}")
        with ff3:
            ff3.metric("Book Value",value=f"Rp. {finance_format((asset_total+depreciation_total)/1000000000,'B')}")
        style_metric_cards()
 
        fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Account Description</b>','<b>Asset</b>','<b>Accumulation Depreciation</b>','<b>Book Value</b>'],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['center','center', 'center', 'center'],
            font=dict(color='white', size=16)
        ),
        cells=dict(
            values= [check_out_sum['Account Description'],
                    check_out_sum['Asset'].apply(financial_format),
                    check_out_sum['Accumulation Depreciation'].apply(financial_format),
                    check_out_sum['Book Value'].apply(financial_format)],
            line_color='darkslategray',
            fill_color = [[rowOddColor,rowEvenColor]*math.ceil(len(results_tabulation)/2)],
            align = ['left', 'right', 'right', 'right',],
            height = 30,
            font = dict(color = 'black', 
                        size = 14)
            ))
        ])
        fig.update_layout(
            height=350,
            margin=dict(
                l=10,
                r=10,
                b=10,
                t=10
                )
        )
        st.plotly_chart(fig, use_container_width=True)

    except:
        ff1,ff2,ff3 = st.columns(3)
        with ff1:
            ff1.metric("Asset Total",value=None)
        with ff2:
            ff2.metric("Accumulation Depreciation Total",value=None)
        with ff3:
            ff3.metric("Book Value",value=None)
        style_metric_cards()
   
   
    st.subheader("Investment Property")
    #get investment property
    try:
        iv_prop_label_asset = (results[(results['GroupAssets'] == 'Asset')&(results['AccountDescription'].str.contains('Properti Investasi -'))]).copy()
        iv_prop_label_asset['Account Description'] = iv_prop_label_asset['AccountDescription'].apply(lambda x:x.split("- ")[1])
        iv_prop_label_asset_total = iv_prop_label_asset[['Account Description','EndAmount']]
        iv_prop_label_asset_total_renamed = iv_prop_label_asset_total.rename(columns={"EndAmount":"Asset"})
        iv_prop_label_asset_total_amount = (iv_prop_label_asset_total_renamed.groupby(by=['Account Description']).sum()).reset_index()

        iv_prop_label_depreciation = (results[results['GroupAssets'].str.contains('depreciation',case=False)]).copy()
        iv_prop_label_depreciation['Account Description'] = iv_prop_label_depreciation['AccountDescription'].apply(lambda x:x.split("- ")[1])
        iv_prop_label_depreciation_total = iv_prop_label_depreciation[['Account Description','EndAmount']]
        iv_prop_label_depreciation_total_renamed = iv_prop_label_depreciation_total.rename(columns={"EndAmount":"Accumulation Depreciation"})
        iv_prop_label_depreciation_total_amount = (iv_prop_label_depreciation_total_renamed.groupby(by=['Account Description']).sum()).reset_index()
        
        merged_join_test = pd.merge(iv_prop_label_asset_total_amount,iv_prop_label_depreciation_total_amount,on='Account Description',how="left")
        check_out_sum = merged_join_test.groupby(by=['Account Description']).sum().reset_index()
        check_out_sum['Book Value'] = check_out_sum['Asset'] + check_out_sum['Accumulation Depreciation']
        asset_total = np.sum(check_out_sum['Asset'])
        depreciation_total = np.sum(check_out_sum['Accumulation Depreciation'])
        grand_total = np.sum(check_out_sum['Book Value'])
        ff1,ff2,ff3 = st.columns(3)
        with ff1:
            ff1.metric("Asset Total",value=f"Rp. {finance_format(asset_total/1000000000,'B')}")
        with ff2:
            ff2.metric("Accumulation Depreciation Total",value=f"Rp. {finance_format(depreciation_total/1000000000,'B')}")
        with ff3:
            ff3.metric("Book Value",value=f"Rp. {finance_format(grand_total/1000000000,'B')}")
        style_metric_cards()

        fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Account Description</b>','<b>Asset</b>','<b>Accumulation Depreciation</b>','<b>Book Value</b>'],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['center','center', 'center', 'center'],
            font=dict(color='white', size=16)
        ),
        cells=dict(
            values= [check_out_sum['Account Description'],
                    check_out_sum['Asset'].apply(financial_format),
                    check_out_sum['Accumulation Depreciation'].apply(financial_format),
                    check_out_sum['Book Value'].apply(financial_format)],
            line_color='darkslategray',
            fill_color = [[rowOddColor,rowEvenColor]*math.ceil(len(results_tabulation)/2)],
            align = ['left', 'right', 'right', 'right',],
            height = 30,
            font = dict(color = 'black', 
                        size = 14)
            ))
        ])
        fig.update_layout(
            height=350,
            margin=dict(
                l=10,
                r=10,
                b=10,
                t=10
                )
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        ff1,ff2,ff3 = st.columns(3)
        with ff1:
            ff1.metric("Asset Total",value=None)
        with ff2:
            ff2.metric("Accumulation Depreciation Total",value=None)
        with ff3:
            ff3.metric("Book Value",value=None)
        style_metric_cards()

    
    st.subheader("Intangible Asset")
    #get intangible
    try:
        ig_ass_label_asset = (results[(results['GroupAssets'] == 'Asset')&(results['AccountDescription'].str.contains('Aset Tidak Berwujud -'))]).copy()
        ig_ass_label_asset['Account Description'] = ig_ass_label_asset['AccountDescription'].apply(lambda x:x.split("- ")[1])
        ig_ass_label_asset_total = ig_ass_label_asset[['Account Description','EndAmount']]
        ig_ass_label_asset_total_renamed = ig_ass_label_asset_total.rename(columns={"EndAmount":"Asset"})
        ig_ass_label_asset_total_amount = (ig_ass_label_asset_total_renamed.groupby(by=['Account Description']).sum()).reset_index()

        ig_ass_label_depreciation = (results[results['GroupAssets'].str.contains('depreciation',case=False)]).copy()
        ig_ass_label_depreciation['Account Description'] = ig_ass_label_depreciation['AccountDescription'].apply(lambda x:x.split("- ")[1])
        ig_ass_label_depreciation_total = ig_ass_label_depreciation[['Account Description','EndAmount']]
        ig_ass_label_depreciation_total_renamed = ig_ass_label_depreciation_total.rename(columns={"EndAmount":"Accumulation Depreciation"})
        ig_ass_label_depreciation_total_amount = (ig_ass_label_depreciation_total_renamed.groupby(by=['Account Description']).sum()).reset_index()
        
        merged_join_test = pd.merge(ig_ass_label_asset_total_amount,ig_ass_label_depreciation_total_amount,on='Account Description',how="left")
        check_out_sum = merged_join_test.groupby(by=['Account Description']).sum().reset_index()
        check_out_sum['Book Value'] = check_out_sum['Asset'] + check_out_sum['Accumulation Depreciation']
        asset_total = np.sum(check_out_sum['Asset'])
        depreciation_total = np.sum(check_out_sum['Accumulation Depreciation'])
        grand_total = np.sum(check_out_sum['Book Value'])
        ff1,ff2,ff3 = st.columns(3)
        with ff1:
            ff1.metric("Asset Total",value=f"Rp. {finance_format(asset_total/1000000000,'B')}")
        with ff2:
            ff2.metric("Accumulation Depreciation Total",value=f"Rp. {finance_format(depreciation_total/1000000000,'B')}")
        with ff3:
            ff3.metric("Book Value",value=f"Rp. {finance_format(grand_total/1000000000,'B')}")
        style_metric_cards()

        fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Account Description</b>','<b>Asset</b>','<b>Accumulation Depreciation</b>','<b>Book Value</b>'],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['center','center', 'center', 'center'],
            font=dict(color='white', size=16)
        ),
        cells=dict(
            values= [check_out_sum['Account Description'],
                    check_out_sum['Asset'].apply(financial_format),
                    check_out_sum['Accumulation Depreciation'].apply(financial_format),
                    check_out_sum['Book Value'].apply(financial_format)],
            line_color='darkslategray',
            fill_color = [[rowOddColor,rowEvenColor]*math.ceil(len(results_tabulation)/2)],
            align = ['left', 'right', 'right', 'right',],
            height = 30,
            font = dict(color = 'black', 
                        size = 14)
            ))
        ])
        fig.update_layout(
            height=350,
            margin=dict(
                l=10,
                r=10,
                b=10,
                t=10
                )
        )
        st.plotly_chart(fig, use_container_width=True)


    except:
        ff1,ff2,ff3 = st.columns(3)
        with ff1:
            ff1.metric("Asset Total",value=None)
        with ff2:
            ff2.metric("Accumulation Depreciation Total",value=None)
        with ff3:
            ff3.metric("Book Value",value=None)
        style_metric_cards()

    st.subheader("Asset Right to Use")
    #get asset right to use
    try:
        aru_label_asset = (results[(results['GroupAssets'] == 'Asset')&(results['AccountDescription'].str.contains('Aset Hak Guna -'))]).copy()
        aru_label_asset['Account Description'] = aru_label_asset['AccountDescription'].apply(lambda x:x.split("- ")[1])
        aru_label_asset_total = aru_label_asset[['Account Description','EndAmount']]
        aru_label_asset_total_renamed = aru_label_asset_total.rename(columns={"EndAmount":"Asset"})
        aru_label_asset_total_amount = (aru_label_asset_total_renamed.groupby(by=['Account Description']).sum()).reset_index()

        aru_label_depreciation = (results[results['GroupAssets'].str.contains('depreciation',case=False)]).copy()
        aru_label_depreciation['Account Description'] = aru_label_depreciation['AccountDescription'].apply(lambda x:x.split("- ")[1])
        aru_label_depreciation_total = aru_label_depreciation[['Account Description','EndAmount']]
        aru_label_depreciation_total_renamed = aru_label_depreciation_total.rename(columns={"EndAmount":"Accumulation Depreciation"})
        aru_label_depreciation_total_amount = (aru_label_depreciation_total_renamed.groupby(by=['Account Description']).sum()).reset_index()
        
        merged_join_test = pd.merge(aru_label_asset_total_amount,aru_label_depreciation_total_amount,on='Account Description',how="left")
        check_out_sum = merged_join_test.groupby(by=['Account Description']).sum().reset_index()
        check_out_sum['Book Value'] = check_out_sum['Asset'] + check_out_sum['Accumulation Depreciation']
        asset_total = np.sum(check_out_sum['Asset'])
        depreciation_total = np.sum(check_out_sum['Accumulation Depreciation'])
        grand_total = np.sum(check_out_sum['Book Value'])
        ff1,ff2,ff3 = st.columns(3)
        with ff1:
            ff1.metric("Asset Total",value=f"Rp. {finance_format(asset_total/1000000000,'B')}")
        with ff2:
            ff2.metric("Accumulation Depreciation Total",value=f"Rp. {finance_format(depreciation_total/1000000000,'B')}")
        with ff3:
            ff3.metric("Book Value",value=f"Rp. {finance_format(grand_total/1000000000,'B')}")
        style_metric_cards()

        fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Account Description</b>','<b>Asset</b>','<b>Accumulation Depreciation</b>','<b>Book Value</b>'],
            line_color='darkslategray',
            fill_color=headerColor,
            align=['center','center', 'center', 'center'],
            font=dict(color='white', size=16)
        ),
        cells=dict(
            values= [check_out_sum['Account Description'],
                    check_out_sum['Asset'].apply(financial_format),
                    check_out_sum['Accumulation Depreciation'].apply(financial_format),
                    check_out_sum['Book Value'].apply(financial_format)],
            line_color='darkslategray',
            fill_color = [[rowOddColor,rowEvenColor]*math.ceil(len(results_tabulation)/2)],
            align = ['left', 'right', 'right', 'right',],
            height = 30,
            font = dict(color = 'black', 
                        size = 14)
            ))
        ])
        fig.update_layout(
            height=350,
            margin=dict(
                l=10,
                r=10,
                b=10,
                t=10
                )
        )
        st.plotly_chart(fig, use_container_width=True)


    except:
        ff1,ff2,ff3 = st.columns(3)
        with ff1:
            ff1.metric("Asset Total",value=None)
        with ff2:
            ff2.metric("Accumulation Depreciation Total",value=None)
        with ff3:
            ff3.metric("Book Value",value=None)
        style_metric_cards()
    

    st.divider()

    #creata figure
    check_data_amount = raw_data_sum[raw_data_sum['AccountDescription'].str.contains('Kas dan Bank')]
    alv = check_data_amount[['CompanyName','BeginAmount','EndAmount']].copy()
    alv = alv.groupby(by=['CompanyName']).sum().reset_index()
    alv = alv.sort_values(by=['EndAmount'],ascending=False)

    st.subheader("Top 10 Company Cash and Bank Amount")
    fig_comp_balance = go.Figure()
    fig_comp_balance.add_trace(
        go.Bar(
            x = alv['BeginAmount'][:10],
            y = alv['CompanyName'][:10],
            orientation="h",
            marker=dict(color="blue"),
            name = "Begin Amount",
            text = finance_format(alv['BeginAmount'][:10]/1000000000,"B"),
            textposition = 'auto'
        )
    )

    fig_comp_balance.add_trace(
        go.Bar(
            x = alv['EndAmount'][:10],
            y = alv['CompanyName'][:10],
            orientation="h",
            marker=dict(color="red"),
            name = "End Amount",
            text = finance_format(alv['EndAmount'][:10]/1000000000,"B"),
            textposition = 'auto'
        )
    )

    fig_comp_balance.update_layout(
        yaxis = dict(autorange='reversed'),
        yaxis_title = dict(text='Companies',font=dict(size=15)),
        xaxis_title = dict(text='End Amount',font=dict(size=15)),
        height = 900,
        font = dict(
            size = 14,
        )  
    )

    st.plotly_chart(fig_comp_balance,use_container_width=True, key='top_10_company_cash_and_bank_amount')

    st.divider()

    st.markdown('<h2 class="section-title">Company Detail Bank : Ending Amount</h2>',unsafe_allow_html=True)
    s1,s2,s3,s4 = st.columns(4)

    merged_data = (raw_data[raw_data['Account Description']=='Kas dan Bank']).copy()

    list_company = merged_data['Company Name'].unique().tolist()
    list_company.insert(0,'Please select')
    list_bank = merged_data['BankName'].unique().tolist()
    list_bank.insert(0,'Please select')
    with s1:
        company_bank = s1.selectbox('Select a company', options=list_company)
    with s2:
        bank = s2.selectbox('Select a bank', options=list_bank)
    with s3:
        pass
    with s4:
        pass

    compare_comp_bank = go.Figure()

    if company_bank == 'Please select' and bank == 'Please select':
        final_filter = bank
        merged_data_amount = merged_data[merged_data['BankName']==final_filter]
        merged_data_amount = merged_data_amount[['Company Name','End Amount']].reset_index()
        merged_data_amount = merged_data_amount.groupby(by='Company Name').sum().reset_index()
        merged_data_amount = merged_data_amount.sort_values(by='End Amount',ascending=False).reset_index()
    elif company_bank == 'Please select' and bank != "Please select":
        merged_data_amount = merged_data[merged_data['BankName']==bank]
        merged_data_amount = merged_data_amount[['Company Name','End Amount']].reset_index()
        merged_data_amount = merged_data_amount.groupby(by='Company Name').sum().reset_index()
        merged_data_amount = merged_data_amount.sort_values(by='End Amount',ascending=False).reset_index()
        compare_comp_bank.add_trace(
        go.Bar(
            x = merged_data_amount['End Amount'][:20],
            y = merged_data_amount['Company Name'][:20],
            orientation = "h",
            marker=dict(color="blue"),
            name = "End Amount",
            text = finance_format(merged_data_amount['End Amount'][:20],'M'),
            textposition = 'auto'
            )
        )

        compare_comp_bank.update_layout(
            yaxis = dict(autorange='reversed'),
            yaxis_title = dict(text='Companies',font=dict(size=15)),
            xaxis_title = dict(text='End Amount',font=dict(size=15)),
            height = 900,
            font = dict(
                size = 14,
            )  
        )
    elif company_bank != 'Please select' and bank == 'Please select':
        final_filter = company_bank
        merged_data_amount = merged_data[merged_data['Company Name']==final_filter]
        merged_data_amount = merged_data_amount[['BankName','End Amount']].reset_index()
        merged_data_amount = merged_data_amount.groupby(by='BankName').sum().reset_index()
        merged_data_amount = merged_data_amount.sort_values(by='End Amount',ascending=False).reset_index()
        compare_comp_bank.add_trace(
        go.Bar(
            x = merged_data_amount['End Amount'][:20],
            y = merged_data_amount['BankName'][:20],
            orientation = "h",
            marker=dict(color="blue"),
            name = "End Amount",
            text = finance_format(merged_data_amount['End Amount'][:20],'M'),
            textposition = 'auto'
            )
        )

        compare_comp_bank.update_layout(
            yaxis = dict(autorange='reversed'),
            yaxis_title = dict(text='BankName',font=dict(size=15)),
            xaxis_title = dict(text='End Amount',font=dict(size=15)),
            height = 900,
            font = dict(
                size = 14,
            )  
        )
    else:
        merged_data_amount = merged_data[(merged_data['Company Name']==company_bank) & (merged_data['BankName']==bank)]
        bank_account = merged_data_amount['BankAccount'].values
        compare_comp_bank.add_trace(
        go.Bar(
            y = merged_data_amount['End Amount'][:20],
            x = merged_data_amount['BankAccount'][:20],
            orientation = "v",
            marker=dict(color="blue"),
            name = "End Amount",
            text = finance_format(merged_data_amount['End Amount'][:20],'M'),
            textposition = 'auto'
            )
        )

        compare_comp_bank.update_layout(
            xaxis_title = dict(text='BankAccount',font=dict(size=15)),
            yaxis_title = dict(text='End Amount',font=dict(size=15)),
            height = 900,
            font = dict(
                size = 14,
            )  
        )

        compare_comp_bank.update_xaxes(
                tickangle=0,
                 tickmode = 'array',
                 tickvals = bank_account,
                 ticktext= [d for d in bank_account]
        )


    st.plotly_chart(compare_comp_bank,use_container_width=True)