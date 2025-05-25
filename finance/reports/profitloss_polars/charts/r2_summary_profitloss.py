import streamlit as st
import plotly.graph_objects as go

def summary_profitloss_indicator(label, value):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        number = {'suffix': '%'},
        title = {'text': label},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps' : [
                {'range': [0, 50], 'color': "#84ccfb"},
                {'range': [50, 100], 'color': "#046ccc"}],
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': value}
        }
    ))
    fig.update_layout(height=300, margin=dict(l=50,r=50,b=50,t=50))
    st.plotly_chart(fig, use_container_width=True)

def summary_profitloss_scorecard(label, value):
    st.markdown(f"""
        <div class="score-card-profit-loss"> 
            <p>{label}<p>
            <p class="profit-loss-font"> {"{:.2%}".format(value)} </p>
        </div>
    """,unsafe_allow_html=True)