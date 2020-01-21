import requests
import json
import sys
import sqlite3

requests.packages.urllib3.disable_warnings()  # Disable warning message


url = "https://198.18.133.254/api/relation/HcsUserREL/" #Thi IP address is for HCS 11.5 dCloud lab


#The header below includes the encoded credentials of HCS 11.5 dCloud lab, you may need to login manually first to change the admin password
headers = {
    'Authorization': "Basic RENsb3VkU1BBZG1pbkBkY2xvdWQuY2lzY28uY29tOkMxc2NvMTIz",
    'Cache-Control': "no-cache",
    'Postman-Token': "953e9c63-e753-40de-93b3-ee6d09eb6400"
    }

# Open and connect to DB file
conn = sqlite3.connect('sqlite_file.db')
c = conn.cursor()

#Create table to include user name and entitlement 
c.execute('''CREATE TABLE if not exists usersdata
           (ID INTEGER PRIMARY KEY NULL,
           username           TEXT    NOT NULL,
           EP           TEXT);''')

#For testing purpose, limiting the query to 100 users information, 
#in production enviroment, it's better to create a loop with controlled API requests speed to prevent overworlming CUCDM server

querystring = {"skip": "0", "limit" : "100"}
try:
    response = requests.request("GET", url, headers=headers, params=querystring, verify=False) #Request users information from CUCDM server
except requests.exceptions.RequestException as _err:
        print ( "Error processing API request", _err )
        sys.exit(1)


usersJSONdump = response.json() #Loading recieved data from CUCDM in JSON format

#The loop below will go through JSON data and extract each user information, 
#and store user name with Entitlement Profile name in the database file

for u in (usersJSONdump['resources']):
    _user_href = (u['meta']['references']['self'][0]['href'] )
    _url2 = "https://198.18.133.254" + _user_href
    response2 = requests.request("GET", _url2, cookies=response.cookies, verify=False)
    userInfo = response2.json()
    _EP = (userInfo['data']['ps']['entitlement_profile'])
    _username = (userInfo['data']['username'])
    print(_username)
    print(_EP)

    c.execute("insert into usersdata (username, EP)  values (?,?)", (_username, _EP))


#Extract and print updated database for testing
c.execute('SELECT * FROM usersdata ')
print(c.fetchall())

