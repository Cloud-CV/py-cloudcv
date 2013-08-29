from uploadData import UploadData
from socketConnection import SocketIOConnection
from colorama import init
from colorama import Fore
from parseArguments import ConfigParser
from log import log
init()

import sys

class PCloudCV:
    config_obj=None
    
    def __init__(self, list):
        self.config_obj = ConfigParser()
        self.config_obj.parseArguments(list)
        self.config_obj.verify()

    def pCloudCV(self):
        ud = UploadData(self.config_obj)
        ud.start()
        log('I','Starting Uploading Data')
        sioc=SocketIOConnection(self.config_obj.exec_name, self.config_obj.output_path)
        sioc.start()

if __name__ == "__main__":
    imagepath = None
    resultpath = None
    executable = None
    
    print Fore.RESET
    
    p = PCloudCV(sys.argv[1:])
    p.pCloudCV()

