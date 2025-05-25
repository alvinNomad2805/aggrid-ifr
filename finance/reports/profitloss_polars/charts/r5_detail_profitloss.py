import streamlit as st
import plotly.graph_objects as go
import math

def detail_profitloss_table(data_source):
    headerColor = '#0068c9'
    rowEvenColor = '#A0DEFF'
    rowOddColor = 'white'

    fig = go.Figure(data=[go.Table(
    header=dict(
        values=['<b>Category</b>','<b>Group</b>','<b>Account Detail</b>','<b>Amount (Rp. Million)</b>'],
        line_color='darkslategray',
        fill_color=headerColor,
        align=['left','left', 'left', 'left'],
        font=dict(color='white', size=16)
    ),
    cells=dict(
        values= [data_source['Group'],
                 data_source['Group2'],
                 data_source['AccountDescription'],
                 data_source['EndAmount']],
        line_color='darkslategray',
        fill_color = [[rowOddColor,rowEvenColor]*math.ceil(len(data_source)/2)],
        align = ['left', 'left', 'left', 'right'],
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

    # df = data_source.copy()
    # df = df.reset_index()
    # df = df[['Group', 'Group2', 'AccountDescription', 'EndAmount']]
    # df.rename(columns={"Group": "Category", "Group2": "Group", "AccountDescription": "Account Detail", "EndAmount": "Amount (Rp. Million)"}, inplace=True)

    # # Function to apply alternating row colors
    # def highlight_rows(row):
    #     return ['background-color: #A0DEFF' if row.name % 2 == 0 else 'background-color: white'] * len(row)
    
    # styled_df = df.style.apply(highlight_rows, axis=1)
    # st.dataframe(styled_df, use_container_width=True, hide_index=True)
