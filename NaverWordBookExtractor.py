from bs4 import BeautifulSoup 
import requests
import rsa
from rsa import common, transform, core
import re
import argparse

session_keys = {}

#Type the username
#TODO Move to other files that private information.
info = { "id" : "  ", "pw" : "" }
session = requests.Session()
session_key_string = ""

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
    pub_key = rsa.PublicKey(e=int(session_keys["nvalue"],16), n = int(session_keys["evalue"],16))
    source  = (getLenChar(session_keys["sessionkey"]) + session_keys["sessionkey"] + getLenChar(info["id"]) + info["id"]
            + getLenChar(info["pw"]) + info["pw"])
    return rsa.encrypt(source.encode('utf-8'), pub_key)

def signin():
    session_key_string = requests.get("https://nid.naver.com/login/ext/keys.nhn").text
    if(split_keys(session_key_string) is False):
        print("Error")
        return False
    encrypted_source = encrypt()
    postdata = {
    "encpw": encrypted_source.hex(), 
    "enctp": 1,
    "encnm": session_keys["keyname"],
    }
    response = session.post("https://nid.naver.com/nidlogin.login", data=postdata)
    
    if response.text.count('\n') > 50 :
        print("sigin in error")
        return False
        
    bf = BeautifulSoup(response.text, 'html.parser')
    url = re.search(r'\"(.+?)\"', bf.find_all("script")[0].string).group(0).replace("\"","")
    bf = BeautifulSoup(response.text, 'html.parser')
    url = re.search(r'\"(.+?)\"', bf.find_all("script")[0].string).group(0).replace("\"","")
    response = session.get(url)
    bf = BeautifulSoup(response.text, 'html.parser')
    url = re.search(r'\"(.+?)\"', bf.find_all("script")[0].string).group(0).replace("\"","")
    response = session.get(url)

def getExtractSet():
    doc = session.get("http://wordbook.naver.com/endic")
    bf = BeautifulSoup(doc.text, 'html.parser')
    diclist = bf.find("ul", class_="list_a01_l").find_all("a")
    res = {}
    for a in diclist:
        if "recentReviewdWordBook" not in a['href']:
            title = a.string.replace("\n", "").replace("		            	", "")
            res[title] =  "http://wordbook.naver.com" + a['href']
    return res

def parsingData(baseurl):
    if baseurl is None:
        print(target+" is not None")
        exit(0)

    data = session.get(baseurl)
    bf = BeautifulSoup(data.text, 'html.parser')
    pagenaiv = bf.find("div", class_ = "pagenavi_c")
    pages = None
    wordset = {}
    i = 0

    if pagenaiv is not None:
        pages = pagenaiv.find_all("a")        

    while True:
        words = []
        means = []

        form = bf.find("form", {"name" : "frm"})
        alist = form.find_all("a", class_ = "_miniPage")
        divlist = form.find_all("div", class_ = "vocab_cont")
        
        for a in alist:
            word = a.find('span').contents
            words.append(word[0].replace("\t", "").replace("\n", "").replace("   ", ""))
        for div in divlist:
            m = div.find("ol").find_all("li")[0].find("li", class_ = "c_13_a")
            mean = ""
            for ms in m.contents:
                mean += ms.string + "@"
            means.append(mean) 
        for j in range(len(words)):
            print(words[j] + " : " + means[j])
            wordset[words[j]] = means[j]
        i+=1
        if i > (pages is not None and len(pages)):
            break
        data = session.get("http://wordbook.naver.com" + pages[i-1]["href"])
        bf = BeautifulSoup(data.text, 'html.parser')
    return wordset

parser = argparse.ArgumentParser(description='Naver Wordbook data extractor.')
parser.add_argument('WordBook', metavar='WORDBOOK',
                   help='extract target word book.')
parser.add_argument('-o','--out',metavar="FILENAME", help='out put file name.')

args = parser.parse_args()


if signin() is False:
    exit(0)
urlset = getExtractSet()
if(urlset[args.WordBook] is None):
    print(args.WordBook+" is Not existing.")
    exit(0)
data = parsingData(urlset[args.WordBook])
filename = "a.txt"
if args.out is not None:
    filename = args.out
f = open(filename, "w", encoding='utf8')
for key, value in data.items():
    f.write(key +  "::" + value + "\n")
f.close()
