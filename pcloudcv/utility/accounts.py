
import pickle
import requests
import webbrowser
import uuid
from os import path
import sys
import json
import time
from logger import info, debug, error, warn
import conf
import redis


googleAuthentication = False
dropboxAuthentication = False
login_required = True

redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
class GoogleAccounts:
    """
    This class type stores the `userid` and `emailid` of a user's Google account.

    :param userid: Google UserId. 
    :param emailid: User's email Id. 
    """

    def __init__(self, userid='', emailid=''):
        self.userid = userid
        self.emailid = emailid


class DropboxAccounts:
    """
    This class type stores the `userid` and `access_token` of a user's Dropbox account. These details are updated when a user authorizes CloudCV to
    access data from his Dropbox folders.
    """

    def __init__(self, userid='', access_token=''):
        self.userid = userid
        self.access_token = access_token


class Accounts:
    """
    This class type stores the information about user's Dropbox and Google accounts.
    """
    gaccount = GoogleAccounts()
    dbaccount = DropboxAccounts()

    def __init__(self):
        pass

    def getGoogleUserID(self):
        """
        Returns Google userId of user.

        :return: Google `userid` of a user.
        """
        return self.gaccount.userid

PATH_TO_CONFIG_FILE = str(path.dirname(path.dirname(path.realpath(__file__))))+'/config.cfg'
    

def readAccounts(path=PATH_TO_CONFIG_FILE):
    """
    Reads the account info from the serialized config file. 

    :param path: Path to the config file. (not to be confused with `config.json`)
    :type path: str
    :return: Deserialized account information.  
    """
    debug(path)
    reader = open(path, 'rb')
    account = pickle.load(reader)
    reader.close()
    return account

def writeAccounts(account, path = PATH_TO_CONFIG_FILE):
    """
    Writes the account info by serializing it to the config file.

    :param account: An instance of :class:`Accounts`.
    :type account: :class:`Accounts`
    :param path: Path to the config.cfg file.(Not to be confused with config.json file.)
    """
    writer = open(path, 'wb')
    pickle.dump(account, writer)
    writer.close()


random_key = ''


def dropboxAuthenticate():
    """
    This prompts a new CloudCV user for permission to access his DropBox account. This requires user to be already 
    authenticated using Google account.  
    """
    global random_key, account_obj, googleAuthentication, dropboxAuthentication

    if googleAuthentication:
        db_userid = account_obj.dbaccount.userid
        if db_userid and db_userid is not '':
            response = requests.get(conf.BASE_URL + '/auth/dropbox', params={'type': 'api',
                                                                                       'state': random_key,
                                                                                       'userid': str(account_obj.gaccount.userid),
                                                                                       'dbuserid': str(db_userid)})
        else:
            response = requests.get(conf.BASE_URL + '/auth/dropbox', params={'type': 'api',
                                                                                       'state': random_key,
                                                                                       'userid': str(account_obj.gaccount.userid)})

        try:
            response_json = json.loads(response.text)
        except ValueError:
            debug(response.text)
            sys.exit()

        if 'redirect' in response_json and response_json['redirect'] == 'True':
            webbrowser.open_new_tab(str(response_json['url']))

        elif 'isValid' in response_json and response_json['isValid'] == 'True':
            info('DropBox Authentication Successful')
            if account_obj.dbaccount.access_token is None or account_obj.dbaccount.access_token == '':
                account_obj.dbaccount.access_token = response_json['token']
                redis_obj.set('dropbox_token', response_json['token'])
            dropboxAuthentication = True

    else:
        authenticate()
        while not googleAuthentication:
            time.sleep(5)
        dropboxAuthenticate()



def authenticate():
    """
    A new user is authenticated using his Google account. If the user is already authenticated, a Welcom message is displayed in a new browser tab. 
    """
    global random_key, account_obj, googleAuthentication
    random_key = str(uuid.uuid1())
    for i in range(100):
        try:
            if path.exists('config.cfg'):
                account_obj = readAccounts()
                userid = account_obj.gaccount.userid
                debug(userid)

                response = requests.get(conf.BASE_URL + '/auth/google/', params={'type': 'api',
                                                                                          'state': random_key,
                                                                                          'userid': str(userid)})
            else:
                response = requests.get(conf.BASE_URL + '/auth/google/', params={'type': 'api',
                                                                                          'state': random_key})
            break
        except Exception as e:
            warn('Error connecting to cloudcv. Retrying: ' + str(i) + ' attempt\n')

    try:
        response_json = json.loads(response.text)
    except ValueError:
        debug(response.text)
        sys.exit()
    if 'error' in response_json:
        error("Possible Error Finding this userid in the server database. Remove the config file and start again.")
        debug(response_json['error'])
        sys.exit()

    if 'redirect' in response_json and response_json['redirect'] == 'True':
        webbrowser.open_new_tab(str(response_json['url']))
        while not googleAuthentication:
            time.sleep(2)

    elif 'isValid' in response_json and response_json['isValid'] == 'True':
        info('User Authenticated')
        info('Welcome ' + str(response_json['first_name']))
        googleAuthentication = True

account_obj = Accounts()