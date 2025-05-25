import streamlit as st
st.set_page_config(layout='wide', initial_sidebar_state='expanded')
import yaml
from yaml.loader import SafeLoader
from auth.auth import Authenticate
from data import LoadData
import pandas as sp
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
# from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
# from utils.caching import refresh_data

# if 'scheduled' not in st.session_state:
#     print("SESSION RESET")
#     st.session_state['scheduled'] = True
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(refresh_data, trigger='interval', id='task', minutes=1)
#     scheduler.start()

#read credentials data source - can be replaced to read database
with open('./configs/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

#Styling
with open('./assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

#read the credentials from data source
users_data_raw = LoadData.load_data_users("/users")
users_data = users_data_raw["Data"]
data_test = sp.DataFrame(users_data)
list_users = (data_test['username'].values).tolist()

# credentials = config['credentials']
credentials = list_users
cookie_name = config['cookie']['name']
key = config['cookie']['key']
cookie_expire = config['cookie']['expiry_days']
preauth = config['preauthorized']['emails']

st.sidebar.page_link('Finance.py', label='Finance')

#create login form
authenticator = Authenticate(credentials,cookie_name,key,cookie_expire,preauth,None)
authenticator.login('Login Finance Dashboard','main')

if (st.session_state['username'] == None) or (st.session_state['authentication_status'] == None):
    st.sidebar.page_link('pages/Forgot_Password.py', label='Forgot Password')
else:
    st.sidebar.page_link('pages/Reset_Password.py', label='Reset Password')
    st.sidebar.divider()

if st.session_state['authentication_status'] == True:
    from reports import MainDashboard

    authenticator.logout('Logout', 'sidebar', key='unique_key')
    getrole = data_test.query(f"username == '{st.session_state['name']}'")
    statusrole = getrole['rolename'].values
    current_user = getrole['username'].values
    try:
        MainDashboard.mainpage(st.session_state['name'],statusrole[0])
    except:
        pass
elif st.session_state['authentication_status'] == False:
    st.error('Username/password is incorrect or not registered')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')