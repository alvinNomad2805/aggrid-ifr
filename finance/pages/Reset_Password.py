import streamlit as st
from data.UpdateData import update_password

with st.form("Reset"):
    #Front end style
    with open('./assets/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    st.sidebar.page_link('Finance.py', label='Finance')
    st.sidebar.page_link('pages/Reset_Password.py', label='Reset Password')
    st.subheader("Reset Password")
    username = st.text_input("Username")
    new_pass = st.text_input('New Password',type='password')
    confirm_pass = st.text_input('Confirm New Password',type='password')
    reset_now = st.form_submit_button('Reset')
    if reset_now:
        if new_pass != confirm_pass:
            st.error("New and Confirm Password not match !!!")
        else:
            update_password(username,new_pass)
            st.warning("Successfully Reset")
    else:
        st.warning("Please fill the user and new password")
