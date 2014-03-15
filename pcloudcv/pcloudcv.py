import os
import sys
from os import system

path = os.path.realpath(__file__)
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

os.system('redis-server')

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
        job.job.imagepath = self.config_obj.source_path

    def signal_handler(self, signal, frame):
        print 'You pressed Ctrl+C! Exiting Now'
        local_server.server.stop()
        local_server.exit_program()

    def authenticate(self):
        local_server.server.setDaemon(True)
        local_server.server.start()

        accounts.authenticate()

    def run(self):

        if self.login_required:
            self.authenticate()


        ud = UploadData(self.config_obj)
        ud.setDaemon(True)
        ud.start()
        logging.log('I', 'Starting Uploading Data')
        sioc = SocketIOConnection(self.config_obj.exec_name, self.config_obj.output_path)
        sioc.setDaemon(True)
        sioc.start()






