from uploadData import UploadData
from socketConnection import SocketIOConnection
from colorama import init
from colorama import Fore
from parseArguments import ConfigParser

init()

import sys

class PCloudCV:
    config_obj=None
    
    def __init__(self, list):
        self.config_obj = ConfigParser()
        self.config_obj.parseArguments(list)
        self.config_obj.verify()

    def pCloudCV(self):
        ud = UploadData(self.config_obj.source_path,self.config_obj.output_path, self.config_obj.exec_name)
        ud.start()
        print "Starting Uploading Data"
        sioc=SocketIOConnection(self.config_obj.exec_name, self.config_obj.output_path)
        sioc.start()

if __name__ == "__main__":
    imagepath = None
    resultpath = None
    executable = None
    
    print Fore.RESET
    
    p = PCloudCV(sys.argv[1:])
    p.pCloudCV()
    

    '''
    try:
        if sys.argv[1] == '-I' and sys.argv[2]!=None:
            imagepath = sys.argv[2]
        else:
            print 'Image Path Not mentioned. Mention the "-I" parameter '
        
        if sys.argv[3] == '-O' and sys.argv[4]!=None:
            resultpath = sys.argv[4]
        else:
            print 'Output Path Not mentioned. Mention the "-O" parameter'
        
        if sys.argv[5] == '-E' and sys.argv[6]!=None:
            executable = sys.argv[6]
        else:
            print 'Executable Not Mentioned. Options: 1. "ImageStitch" 2. "VOCRelease5"'

        if(imagepath!=None and resultpath!=None and executable!=None):
            pCloudCV(imagepath, resultpath, executable)
        
    except Exception as e:
        print 'Mention -I and -O parameter'
        print str(e)
    '''

