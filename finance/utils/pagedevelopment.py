import streamlit as st

def underconstruction():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"# Under Development")
        st.markdown(f"""
                <div> 
                    <p class="score-card-title">We apologize, the dashboard page is still being developed.</br>We value your patience and can't wait to introduce you to our new page shortly.<p>
                </div>
            """,unsafe_allow_html=True)
    with col2:
        st.image("./assets/WebsiteDevelopment.jpg", width=500, use_column_width=True)