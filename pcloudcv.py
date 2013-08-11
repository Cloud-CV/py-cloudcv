from uploadData import UploadData
from socketConnection import SocketIOConnection

import sys

def pCloudCV(imagepath, resultpath):
    ud = UploadData(imagepath,resultpath)
    ud.start()
    sioc=SocketIOConnection()
    sioc.start()

if __name__ == "__main__":
    imagepath = None
    resultpath = None
    
    try:
        if sys.argv[1] == '-I' and sys.argv[2]!=None:
            imagepath = sys.argv[2]
        else:
            print 'Image Path Not mentioned. Mention the "-I" parameter '
        if sys.argv[3] == '-O' and sys.argv[4]!=None:
            resultpath = sys.argv[4]
        else:
            print 'Output Path Not mentioned. Mention the "-O" parameter'
        if(imagepath!=None and resultpath!=None):
            pCloudCV(imagepath, resultpath)
    except Exception as e:
        print 'Mention -I and -O parameter'
        print str(e)

