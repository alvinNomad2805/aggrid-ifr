import requests
import bcrypt

def update_password(username:str,new_password:str):
    server = "http://172.16.5.5:5000"
    url = server + '/auth'
    saltkey = bcrypt.gensalt()
    has_pass = bcrypt.hashpw(new_password.encode(),saltkey)
    inp_data = {
        "username" : username,
        "password" : has_pass.decode()
    }
    status = requests.put(url,json=inp_data)

