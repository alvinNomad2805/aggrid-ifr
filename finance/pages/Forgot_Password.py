import streamlit as st
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#https://myaccount.google.com/u/4/apppasswords -> set up gmail password authenticated

def emailsetup(emailaddress:str):
    sender_email = "alvinsahroni@gmail.com"
    receiver_email = emailaddress
    password = "mjzn ajoq osqv slqe"

    message = MIMEMultipart("alternative")
    message["Subject"] = "multipart test"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    html = """
    <html>
    <body>
        <p>Hi,<br>
        How are you?<br>
        you are requesting a reset password. Please click this link to RESET your PASSWORD! <br>
        <a href="http://10.1.32.26:7000/Reset_Password">Reset password link</a>
        </p>
    </body>
    </html>
    """
    part1 = MIMEText(html, "html")
    message.attach(part1)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )

#Front-end development        
with open('./assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
st.subheader('Forgot Password')
email_addr = st.text_input(label="Email",placeholder="Please input your active/valid email")
clicked = st.button(label="Send")

st.sidebar.page_link('Finance.py', label='Finance')
st.sidebar.page_link('pages/Forgot_Password.py', label='Forgot Password')

if (clicked):
    emailsetup(email_addr)
    st.warning("Email sent, please check your email (Inbox or Junk/Spam Folder)")
else:
    st.warning("Please enter your valid/active email address")

