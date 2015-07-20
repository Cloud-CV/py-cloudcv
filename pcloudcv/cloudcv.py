import os
import sys
from os import system
import time
import requests
from concurrent.futures import ThreadPoolExecutor 
path = os.path.dirname(os.path.realpath(__file__))
if path not in sys.path:
    sys.path.append(path)
import uuid 
import threading
import sqlite3 
from connections import local_server
from utility import accounts
from utility.logger import warn, error, debug, critical
from utility.parseArguments import ConfigParser
import utility.job as job
from connections.uploadData import UploadData
from connections.socketConnection import SocketIOConnection , socketio
import redis
import signal

class CloudCV():
    """
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
        self.login_required = login_required
        accounts.login_required = login_required
        self._workers = 5
        self.upld_launched = 0         
        self.pool = ThreadPoolExecutor(self._workers)
        self._connection = sqlite3.connect('cloudcv.db')

        self._cursor = self._connection.cursor()
        self._cursor.execute("CREATE TABLE IF NOT EXISTS Jobs(uid TEXT, jobid TEXT, status TEXT, input TEXT, output TEXT, exec TEXT, login_required INTEGER)")
        self._redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        # local_server.server.setDaemon(True)
        # Daemon threads give warnings on unexpected exit. 

        local_server.server.start()
        
        # self.sioc.setDaemon(True)
        # Daemon threads give warnings on unexpected exit. 
        self.socket_started = False 
        signal.signal(signal.SIGINT, self.signal_handler)
        
        
    def execute(self, file, dict):
        
        self.config_obj = ConfigParser()
        self.config_obj.parseArguments(dict, file)
        self.config_obj.verify()
        self.upld_launched+=1
        
        if not self.socket_started:
            try :
                self.sioc = SocketIOConnection(self.config_obj.exec_name, self.config_obj.output_path)
                self.sioc.start()
                self.socket_started = True
                time.sleep(4)
            except(KeyboardInterrupt, SystemExit):
                self.sioc.socket_io.disconnect()
                local_server.server.stop()

        self._cursor.execute("INSERT INTO Jobs (uid, status, input, output, exec, login_required)VALUES (?,?,?,?,?,?)",(str(uuid.uuid1()),"queued",self.config_obj.source_path,self.config_obj.output_path,self.config_obj.exec_name,self.login_required,))
        self._connection.commit() 
        udobj = UploadData(self.config_obj)

        self.pool.submit(udobj.run)

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

    

    def exit(self, timeout=None):
        """
        An Alias for :func:`connections.local_server.server.stop`.
        """
        

        if timeout is not None:
            time.sleep(timeout)
            self.sioc.socket_io.disconnect()
            local_server.server.stop()
            
        else :
            while True:
                count = self._redis_obj.get('received_count') 
                if count is not None and int(count) is self.upld_launched:
                    self.sioc.socket_io.disconnect()
                    local_server.server.stop()
                    self._redis_obj.set('received_count',0) 
                    self._redis_obj.set('socketid','') 
                    break
    


    def signal_handler(self, signal, frame):
        """
        A call back function for receiving a 'Ctrl+C' KeyboardInterrupt.
        """
        print '\nYou pressed Ctrl+C! Exiting Now'
        local_server.server.stop()
        self.sioc.socket_io.disconnect()
        sys.exit(0)

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
