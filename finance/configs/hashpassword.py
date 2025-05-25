import streamlit_authenticator as stauth
hasher = stauth.Hasher(['abc123','abc123','testabc','asd']).generate()
print(hasher)