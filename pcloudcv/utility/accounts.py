
import pickle
import requests
import webbrowser
import uuid
from os import path
import sys
import json
import time
from logging import log

googleAuthentication = False
dropboxAuthentication = False
login_required = True

class GoogleAccounts:
    userid = None
    emailid = None

    def __init__(self, userid='', emailid=''):
        self.userid = userid
        self.emailid = emailid


class DropboxAccounts:
    userid = None
    access_token = None

    def __init__(self, userid='', access_token=''):
        self.userid = userid
        self.access_token = access_token


class Accounts:
    gaccount = GoogleAccounts()
    dbaccount = DropboxAccounts()

    def __init__(self):
        pass

    def getGoogleUserID(self):
        return self.gaccount.userid

PATH_TO_CONFIG_FILE = str(path.dirname(path.dirname(path.realpath(__file__))))+'/config.cfg'

def readAccounts(path=PATH_TO_CONFIG_FILE):
        print path
        reader = open(path, 'rb')
        account = pickle.load(reader)
        reader.close()
        return account

def writeAccounts(account, path = PATH_TO_CONFIG_FILE):
        writer = open(path, 'wb')
        pickle.dump(account, writer)
        writer.close()


random_key = ''

def dropboxAuthenticate():
    global random_key, account_obj, googleAuthentication, dropboxAuthentication

    if googleAuthentication:
        db_userid = account_obj.dbaccount.userid
        if db_userid and db_userid is not '':
            response = requests.get('http://cloudcv.org/cloudcv/auth/dropbox', params={'type': 'api',
                                                                                       'state': random_key,
                                                                                       'userid': str(account_obj.gaccount.userid),
                                                                                       'dbuserid': str(db_userid)})
        else:
            response = requests.get('http://cloudcv.org/cloudcv/auth/dropbox', params={'type': 'api',
                                                                                       'state': random_key,
                                                                                       'userid': str(account_obj.gaccount.userid)})
        fi = open('error.html', 'w')
        fi.write(str(response.text))
        fi.close()
        print "Written to File"

        try:
            response_json = json.loads(response.text)
        except ValueError:
            print response.text
            sys.exit()

        if 'redirect' in response_json and response_json['redirect'] == 'True':
            webbrowser.open_new_tab(str(response_json['url']))

        elif 'isValid' in response_json and response_json['isValid'] == 'True':
            print 'DropBox Authentication Successful'
            if account_obj.dbaccount.access_token is None or account_obj.dbaccount.access_token == '':
                account_obj.dbaccount.access_token = response_json['token']
            dropboxAuthentication = True

    else:
        authenticate()
        while not googleAuthentication:
            time.sleep(5)
        dropboxAuthenticate()



def authenticate():

    global random_key, account_obj, googleAuthentication
    random_key = str(uuid.uuid1())
    for i in range(100):
        try:
            if path.exists('config.cfg'):
                account_obj = readAccounts()
                userid = account_obj.gaccount.userid
                print userid

                response = requests.get('http://cloudcv.org/cloudcv/auth/google/', params={'type': 'api',
                                                                                          'state': random_key,
                                                                                          'userid': str(userid)})
            else:
                response = requests.get('http://cloudcv.org/cloudcv/auth/google/', params={'type': 'api',
                                                                                          'state': random_key})
            break
        except Exception as e:
            log('W', 'Error connecting to cloudcv. Retrying: ' + str(i) + ' attempt\n')

    try:
        response_json = json.loads(response.text)
    except ValueError:
        print response.text
        sys.exit()

    if 'redirect' in response_json and response_json['redirect'] == 'True':
        print 'coming'
        webbrowser.open_new_tab(str(response_json['url']))
        while not googleAuthentication:
            time.sleep(2)

    elif 'isValid' in response_json and response_json['isValid'] == 'True':
        print 'User Authenticated'
        print 'Welcome ' + str(response_json['first_name'])
        googleAuthentication = True

account_obj = Accounts()