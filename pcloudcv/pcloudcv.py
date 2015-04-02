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



class PCloudCV(threading.Thread):
    """Creates a PCloudCV instance in a new thread.

    :param file: Path to :doc:`config <configfile>` file.
    :type file:  str
    :param list: Config input from user to override the :doc:`Config file <configfile>` defaults.(Pass an empty dict to use defaults from config.json )
    :type list: dict
    :param login_required: Specifies if a user wants to use a service that requires authentication. Default value is True.
    :type login_required: bool
    """
    config_obj = None
    """
    An instance of :class:`utility.parseArguments.ConfigParser` class. Default is set to None.
    """
    login_required = True
    """
    Variable to mention the requirement of authentication before using the API's.
    """

    def __init__(self, file, list, login_required):
        threading.Thread.__init__(self)
        self.login_required = login_required
        accounts.login_required = login_required

        self.config_obj = ConfigParser()
        self.config_obj.parseArguments(list, file)
        self.config_obj.verify()

        local_server.server.setDaemon(True)
        local_server.server.start()

        self.ud = UploadData(self.config_obj)
        self.sioc = SocketIOConnection(self.config_obj.exec_name, self.config_obj.output_path)
        self.sioc.setDaemon(True)
        self.ud.setDaemon(True)


    def ec2_demo(self):
        """
        

        """
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
        """
        An Alias for :func:`connections.local_server.server.stop`.
        """
        local_server.server.stop()

    def signal_handler(self, signal, frame):
        """
        A call back function for receiving a 'Ctrl+C' KeyboardInterrupt.
        """
        print '\nYou pressed Ctrl+C! Exiting Now'
        local_server.server.stop()
        local_server.exit_program()

    def dropbox_authenticate(self):
        """
        An Alias for :func:`utility.accounts.dropboxAuthenticate`.
        """
        accounts.dropboxAuthenticate()

    def authenticate(self):
        """
        An Alias for :func:`utility.accounts.authenticate`.
        """
        accounts.authenticate()

    def run(self):
        """
        Entry point for the thread containing a CloudCV instance. Starts Auth process and uploads the data to the servers in a child thread.
        """
        if self.login_required:
            self.authenticate()

        self.sioc.start()
        time.sleep(4)

        self.ud.start()






