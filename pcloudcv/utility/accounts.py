import pickle
import requests
import webbrowser
import uuid
from os import path
import sys
import json

class GoogleAccounts:
    userid = None
    emailid = None

    def __init__(self, userid='', emailid=''):
        self.userid = userid
        self.emailid = emailid


class DropboxAcconts:
    userid = None
    access_token = None

    def __init__(self):
        self.userid = ''
        self.access_token = ''


class Accounts:
    gaccount = GoogleAccounts()
    dbaccount = DropboxAcconts()

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


def authenticate():
        global random_key, account_obj
        random_key = str(uuid.uuid1())

        if path.exists('config.cfg'):
            account_obj = readAccounts()
            userid = account_obj.gaccount.userid
            print userid
            response = requests.get('http://cloudcv.org/cloudcv/auth/google', params={'type': 'api',
                                                                                      'state': random_key,
                                                                                      'userid': str(userid)})
        else:
            response = requests.get('http://cloudcv.org/cloudcv/auth/google', params={'type': 'api',
                                                                                      'state': random_key})
        try:
            response_json = json.loads(response.text)
        except ValueError:
            print response.text
            sys.exit()

        if 'redirect' in response_json and response_json['redirect'] == 'True':
            print 'coming'
            webbrowser.open_new_tab(str(response_json['url']))

        elif 'isValid' in response_json and response_json['isValid'] == 'True':
            print 'User Authenticated'
            print 'Welcome '+str(response_json['first_name'])

account_obj = Accounts()