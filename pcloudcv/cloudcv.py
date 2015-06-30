import os
import sys
from os import system
import time
import requests
from concurrent.futures import ThreadPoolExecutor 
path = os.path.dirname(os.path.realpath(__file__))
if path not in sys.path:
    sys.path.append(path)

import threading
import sqlite3 
from connections import local_server
from utility import accounts
from utility.logger import warn, error, debug, critical
from utility.parseArguments import ConfigParser
import utility.job as job
from connections.uploadData import UploadData
from connections.socketConnection import SocketIOConnection , socketio


class CloudCV(threading.Thread):
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

    def __init__(self,login_required=True):
        threading.Thread.__init__(self, name="Shubham")
        self.login_required = login_required
        accounts.login_required = login_required
        self._workers = 5
        self.upld_launched = 0         
        self.pool = ThreadPoolExecutor(self._workers)
        self._connection = sqlite3.connect('cloudcv.db')

        self.cursor = self._connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Jobs(uid TEXT, jobid TEXT, status TEXT, input TEXT, ouput TEXT, exec TEXT, login_required INTEGER)")
        
        # local_server.server.setDaemon(True)
        # Daemon threads give warnings on unexpected exit. 

        local_server.server.start()
        
        # self.sioc.setDaemon(True)
        # Daemon threads give warnings on unexpected exit. 
        self.socket_started = False 
        
        self.start()
        

    def execute(self, file, dict):
        
        self.config_obj = ConfigParser()
        self.config_obj.parseArguments(dict, file)
        self.config_obj.verify()
        self.upld_launched+=1
        
        if not self.socket_started:
            self.sioc = SocketIOConnection(self.config_obj.exec_name, self.config_obj.output_path)
            self.sioc.start()
            self.socket_started = True
            time.sleep(4)

        udobj = UploadData(self.config_obj)

        self.pool.submit(udobj.run())

    def ec2_demo(self):
        """
        

        """
        params_data= {}
        params_data['dropbox_token'] = accounts.account_obj.dbaccount.access_token
        params_data['emailid'] = 'h.agrawal092@gmail.com'
        response = requests.get('http://godel.ece.vt.edu/cloudcv/ec2/', params=params_data)
        # print response.text
        self.stop_local_server()

    def azure_demo(self, emailid, path):

        params_data= {}
        params_data['dropbox_token'] = accounts.account_obj.dbaccount.access_token
        params_data['emailid'] = emailid
        params_data['dropbox_path'] = path
        response = requests.post('http://mlpmasternode.cloudapp.net/api', data=params_data)
        # print response.text
        self.stop_local_server()

    

    def exit(self, timeout):
        """
        An Alias for :func:`connections.local_server.server.stop`.
        """
        
        if timeout is not None:
            time.sleep(timeout)
            self.sioc.socket_io.disconnect()
        # here socket is closed but we need to care about the upload threads running 
        # by closing sockets we do not want results but upload is still working
        # or they get killed once the main thread is killed (daemons)


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

        #communication with socketio via redis (if number_of_launched_jobs = number_of_results_recieved then close the socket )    
