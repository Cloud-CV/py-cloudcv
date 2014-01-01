import pickle
import requests
import webbrowser

class GoogleAccounts:
    userid = None
    first_name = None
    last_name = None
    emailid = None
    access_token = None

    def __init__(self):
        self.userid = ''
        self.first_name = ''
        self.last_name = ''
        self.emailid = ''
        self.access_token = ''


class DropboxAcconts:
    userid = None
    access_token = None

    def __init__(self):
        self.userid = ''
        self.access_token = ''


class CVModule:
    name = ''
    path = ''
    output = ''
    params = None

    def __init__(self, name, path, output):
        self.name = name
        self.path = path
        self.output = output
        self.params = {}


class Accounts:
    gaccount = GoogleAccounts()
    dbaccount = DropboxAcconts()

    def readAccounts(self, path='config.cfg'):
        global account_obj
        reader = open(path, 'rb')
        account_obj = pickle.load(reader)
        reader.close()

    def writeAccounts(self, account, path='config.cfg'):
        writer = open(path, 'wb')
        pickle.dump(account, writer)
        writer.close()

    def authenticate(self):
        response = requests.get('http://cloudcv.org/cloudcv/auth/google')
        webbrowser.open_new_tab(str(response))

account_obj = Accounts()