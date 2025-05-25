import numpy as np

def filter_brand_company(brand, range_data):
    if brand == 'HINO':
        range_data = range_data.loc[((~range_data['KodeCompany'].str.contains('15200')) & 
                                        (range_data['KodeCompany'] != '1800098') & 
                                        (range_data['KodeCompany'] != '131007'))]
    return range_data

def text_font_size(data_source):
    if len(data_source) <= 20:
        fontSize = 15
        axisFontSize = 15
    else:
        fontSize = 11
        axisFontSize = 11
    return fontSize, axisFontSize

def financial_format(data):
    try:
        if np.isinf(float(data)) or np.isnan(float(data)):
            data = "-"
        else:
            data = f'({abs(data):,.2f})' if data < 0 else f'{data:,.2f}'
            #change the format to international currency format
            data = data.replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        data = "-"
    return data

# def generate_chart(data_source, chart_orient, text_format, axis_format, label_field, value_field, label_title, value_title, side_chart_height):
#     fontSize, axisFontSize = text_font_size(data_source)
    
#     if len(data_source) > 10:
#         label_field = label_field + ':N'
#         value_field = value_field + ':Q'
#         default_height = 800
#         final_height = max(default_height, side_chart_height)
#         if chart_orient == 'h':
#             chart = alt.Chart(data_source).mark_bar().encode(
#                 x=alt.X(value_field, title=value_title, sort='ascending', axis=alt.Axis(format=axis_format, labelFontSize=axisFontSize, titleFontSize=axisFontSize)),
#                 y=alt.Y(label_field, title=label_title, axis=alt.Axis(labelFontSize=axisFontSize, titleFontSize=axisFontSize)).sort('-x'),
#                 tooltip=[alt.Tooltip(label_field, title=label_title, format=text_format),
#                          alt.Tooltip(value_field, title=value_title)],
#                 text = alt.Text(label_field, format=text_format)
#             ).properties(height=final_height)
#             text = chart.mark_text(align='center', dx=20, fontSize=fontSize)
#             generated_chart = st.altair_chart(chart+text, use_container_width=True)
#         else:
#             chart = alt.Chart(data_source).mark_bar().encode(
#                 x=alt.X(label_field, title=label_title, axis=alt.Axis(labelFontSize=axisFontSize, titleFontSize=axisFontSize)).sort('-y'),
#                 y=alt.Y(value_field, title=value_title, axis=alt.Axis(format=axis_format, labelFontSize=axisFontSize, titleFontSize=axisFontSize)),
#                 tooltip=[alt.Tooltip(label_field, title=label_title, format=text_format),
#                         alt.Tooltip(value_field, title=value_title)],
#                 text = alt.Text(label_field, format=text_format)
#             )
#             text = chart.mark_text(align='center', dy=-5, fontSize=fontSize)
#             generated_chart = st.altair_chart(chart+text, use_container_width=True)

#     elif len(data_source) >= 2 and len(data_source) <= 10:
#         default_height = 420
#         final_height = max(default_height, side_chart_height)

#         fig = go.Figure(go.Pie(labels=data_source[label_field].tolist(), values=data_source[value_field].tolist()))
#         fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20).update_layout(height=final_height, margin=dict(t=50,b=50,l=0,r=0), legend=dict(font=dict(size=15)))
#         st.plotly_chart(fig, use_container_width=True)
    
#     else:
#         default_height = 505
#         final_height = max(default_height, side_chart_height)

#         generated_chart = st.markdown(f"""
#                         <div class="score-card-conversion" 
#                                       style="height:{final_height}px;
#                                       border-radius: 10px;
#                                       border-style: solid;
#                                       padding: 2px;
#                                       padding-top:100px;
#                                       box-shadow: 5px 10px 18px #888888;
#                                       text-align:center;
#                                       margin-bottom:15px;"> 
#                             <h1>{label_title}</h1>
#                             <p class="big-font"> {str(round(value_field))} </p>
#                         </div>
#                     """,unsafe_allow_html=True)
        
#     return generated_chart, default_height