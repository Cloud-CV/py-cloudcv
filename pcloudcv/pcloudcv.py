import os
import signal
import argparse

from colorama import init
from colorama import Fore
from connections import local_server
from utility import accounts, logging
from utility.parseArguments import ConfigParser

from connections.uploadData import UploadData
from connections.socketConnection import SocketIOConnection

init()

import sys

#------------------------------Initial Setup :- Argument Parser--------------------------
parser = argparse.ArgumentParser()
parser.add_argument("config", type=str, help="Full Path to config file")
parser.add_argument("-I", "--input", type=str, help="Full Path to the Input Folder")
parser.add_argument("-O", "--output", type=str, help="Full Path to the Output Folder")
parser.add_argument("-E", "--executable", type=str, help="Executable Name: \n1.) ImageStitch or \n 2.)VOCRelease5")
parser.add_argument("--nologin", help="Specify this argument to ignore logging in. However some features can be used only when logged in.",
                    action="store_true")
args = parser.parse_args()
#----------------xxx-------------Argument Parser Code Ends---------------------xxx----------------------

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C! Exiting Now'
    local_server.server.stop()
    local_server.exit_program()


class PCloudCV:
    config_obj = None
    login_required = True

    def __init__(self, file, list, login_required):
        signal.signal(signal.SIGINT, signal_handler)
        self.login_required = login_required
        accounts.login_required = login_required

        self.config_obj = ConfigParser()
        self.config_obj.parseArguments(list, file)
        self.config_obj.verify()

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

def parseCommandLineArgs():
    i = 0
    parsedList = {}
    if args.input:
        parsedList['input'] = args.input
    if args.output:
        parsedList['output'] = args.output
    if args.executable:
        parsedList['exec'] = args.executable
    return parsedList, args.config, not args.nologin


if __name__ == "__main__":
    parsedList, config_file, login_required = parseCommandLineArgs()

    p = PCloudCV(os.getcwd() + '/' + str(config_file), parsedList, login_required)
    p.run()

    signal.pause()


