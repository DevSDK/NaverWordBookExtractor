from bs4 import BeautifulSoup 
import requests


session_keys = {}
info = { "id" : "", "pw" : "" }

def split_keys(a):
    keys = a.split(',')

    if (a is None or keys[0] is None or keys[1] is None or keys[2] is None or keys[3] is None):
        return False
    session_keys["sessionkey"] = keys[0]
    session_keys["keyname"] = keys[1]
    session_keys["evalue"] = keys[2]
    session_keys["nvalue"] = keys[3]
    return True

def getLenChar(a):
    return chr(len(a))

def encrypt():
    id = info['id']
    pw = info['pw']

#    change library python rsa to crypto
#    pub_key = rsa.PublicKey(int(session_keys["nvalue"]), int(session_keys["evalue"],16))
#    source  = (getLenChar(session_keys["sessionkey"]) + session_keys["sessionkey"] + getLenChar(info["id"]) + info["id"]
               + getLenChar(info["pw"]) + info["pw"])
    
#    print(pub_key)
#    return rsa.encrypt(source, pub_key)
    

                
    

session_key_string = requests.get("https://nid.naver.com/login/ext/keys.nhn").text

if(split_keys(session_key_string) is False):
    print("Error")
    exit(0)
encrypt()
