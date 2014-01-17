import os
import signal

from colorama import init
from colorama import Fore
from connections import local_server
from utility import accounts, logging
from utility.parseArguments import ConfigParser

from connections.uploadData import UploadData
from connections.socketConnection import SocketIOConnection

init()

import sys



def signal_handler(signal, frame):
    print 'You pressed Ctrl+C! Exiting Now'
    local_server.server.stop()
    sys.exit(0)

class PCloudCV:
    config_obj = None

    def __init__(self, file, list):
        signal.signal(signal.SIGINT, signal_handler)
        self.config_obj = ConfigParser()
        self.config_obj.parseArguments(list, file)
        self.config_obj.verify()

    def authenticate(self):
        local_server.server.start()
        accounts.authenticate()

    def run(self):
        self.authenticate()
        ud = UploadData(self.config_obj)
        ud.setDaemon(True)
        ud.start()
        logging.log('I', 'Starting Uploading Data')
        sioc = SocketIOConnection(self.config_obj.exec_name, self.config_obj.output_path)
        sioc.setDaemon(True)
        sioc.start()

def parseCommandLineArgs(list):
    i = 0
    parsedList = {}

    if len(list) % 2 is not 0:
        print('Error in Specifying Arguments' +
              '\nIt should be mentioned as follows:' +
              '\n-E </full/path/to/Executable Name>'
              '\n-I </full/path/to/Input Path>' +
              '\n-O </full/path/to/Output Path>' +
              '\nFor example -E \'ImageStitch\' ' +
              '-I \'/home/dexter/Picture/input\' ' +
              '-O \'/home/dexter/Picture/output\'')
        sys.exit(0)

    while i < len(list):
        if list[i] == '-E':
            parsedList['name'] = (list[i + 1])
        if list[i] == '-I':
            parsedList['input'] = (list[i + 1])
        if list[i] == '-O':
            parsedList['output'] = ([i + 1])
        i += 2
    return parsedList

if __name__ == "__main__":
    imagepath = None
    resultpath = None
    executable = None

    print Fore.RESET
    if (len(sys.argv) < 2):
        print 'No Config File Specified'
    else:
        file = sys.argv[1]
        parsedList = parseCommandLineArgs(sys.argv[2:])
        p = PCloudCV(os.getcwd() + '/' + str(file), parsedList)
        p.run()

    signal.pause()


