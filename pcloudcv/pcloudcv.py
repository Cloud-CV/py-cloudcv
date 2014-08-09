import os
import sys
from os import system
import time
import requests

path = os.path.dirname(os.path.realpath(__file__))
print "Added Path: " + path
if path not in sys.path:
    sys.path.append(path)

import threading
from colorama import init
from colorama import Fore
from connections import local_server
from utility import accounts, logging
from utility.parseArguments import ConfigParser
import utility.job as job
from connections.uploadData import UploadData
from connections.socketConnection import SocketIOConnection

init()

def getfullpath(s):
    return os.path.join(os.getcw(), s)

class PCloudCV(threading.Thread):
    config_obj = None
    login_required = True

    def __init__(self, file, list, login_required):
        threading.Thread.__init__(self)
        self.login_required = login_required
        accounts.login_required = login_required

        self.config_obj = ConfigParser()
        self.config_obj.parseArguments(list, file)
        self.config_obj.verify()

        local_server.server.setDaemon(True)
        local_server.server.start()

    def ec2_demo(self):
        params_data= {}
        params_data['dropbox_token'] = accounts.account_obj.dbaccount.access_token
        params_data['emailid'] = 'h.agrawal092@gmail.com'
        response = requests.get('http://godel.ece.vt.edu/cloudcv/ec2/', params=params_data)
        print response.text
        self.stop_local_server()

    def azure_demo(self, emailid, path):
        params_data= {}
        params_data['dropbox_token'] = accounts.account_obj.dbaccount.access_token
        params_data['emailid'] = emailid
        params_data['dropbox_path'] = path
        response = requests.post('http://mlpmasternode.cloudapp.net/api', data=params_data)
        print response.text
        self.stop_local_server()

    def stop_local_server(self):
        local_server.server.stop()
        local_server.exit_program()

    def signal_handler(self, signal, frame):
        print 'You pressed Ctrl+C! Exiting Now'
        local_server.server.stop()
        local_server.exit_program()

    def dropbox_authenticate(self):
        accounts.dropboxAuthenticate()

    def authenticate(self):
        accounts.authenticate()

    def run(self):

        if self.login_required:
            self.authenticate()

        ud = UploadData(self.config_obj)
        sioc = SocketIOConnection(self.config_obj.exec_name, self.config_obj.output_path)
        sioc.setDaemon(True)
        sioc.start()

        time.sleep(4)

        ud.setDaemon(True)
        ud.start()





