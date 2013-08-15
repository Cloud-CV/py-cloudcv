import threading
import time
import redis

import urllib2, json, requests, pprint, re

from os import listdir
from os.path import isfile, join

from colorama import init
from colorama import Fore, Back, Style

from poster.encode import multipart_encode

exitFlag = 0
socketid = ''
init()

class UploadData (threading.Thread):
    
    def __init__(self, pathname, imagepath, executable):
        threading.Thread.__init__(self)
        
        self.pathname = pathname
        self.imagepath = imagepath
        self.executable = executable

        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.ps = self.r.pubsub()
        self.ps.subscribe('intercomm')
        
        redisThread = RedisListenForPostThread(self.ps, self.r)
        redisThread.start()
              
    def run(self):
        print "\n\nStarting Post Request"
        send_post_request(self.pathname, self.imagepath, self.ps, self.r, self.executable)
        print "\nExiting From the Post Request Thread"

'''Redis Connection for Inter Thread Communication'''
class RedisListenForPostThread(threading.Thread):
    def __init__(self, ps, r):
        threading.Thread.__init__(self)
        self.r = r
        self.ps = ps
    def run(self):
        print '\nStarting Listening to Redis Channel for HTTP Post Requests'  
        while(True):
            shouldEnd = listenToChannel(self.ps, self.r)
            if(shouldEnd):
                break
        print '\nExiting Redis Thread for HTTP Post requests'


def listenToChannel(ps,r):
    global socketid

    for item in ps.listen():
        if item['type'] == 'message':
            if( item['channel'] == 'intercomm'):
                print item['data']
                if '***end***' in item['data']:
                    r.publish('intercomm2', '***endcomplete***')
                    return True
                else:    
                    socketid = item['data']
                    print socketid
    
    return False
                  
#get request to obtain csrf token
def get_request(url):
    token=''
    try:
	data = requests.get(url) 
	for line in data:
	    
	    m = re.search('(META:{\'CSRF_COOKIE\': \')((\\w)+)(\',)', line)
	    if(m!=None):
		token = m.group(2)
	
    except Exception as e:
	print "Error in get_request: "+str(e)
    
    return token


#get all files in the directory and create a params dictionary. 
def files_in_directory(dir):
    onlyfiles = [ f for f in listdir(dir) if isfile(join(dir,f)) !=None ]
    onlyfiles = [ f for f in onlyfiles if(re.search('([^\s]+(\.(jpg|png|gif|bmp))$)',str(f))!=None) ] 
    print onlyfiles
    return onlyfiles

#send post requests containing images to the server    
def send_post_request(pathname, imagepath, ps, r, executable):
    global socketid

    params={}
    params_data={}
    
    token = get_request('http://godel.ece.vt.edu/cloudcv/matlab')
    
    if(token == ''):
	print 'token not found'
	raise SystemExit
	
    
    files = files_in_directory(pathname)
    
    i=0
    for f in files:
	params['file'+str(i)]=open(pathname+'/'+f, 'rb')
	i+=1
	
    params_data['token']=token
    params_data['count']=str(len(files))
    params_data['socketid']=''
    params_data['executable']=executable
     
    while(True):
        if socketid != '':
            params_data['socketid']=socketid
            break
        else:
            time.sleep(1)
            print '\nwaiting for socket connection to complete'
             
    print str(params)+'\n\n\n\n'
    
    datagen, headers = multipart_encode(params)
    
    print headers
    print datagen

    try:	
	request = requests.post("http://godel.ece.vt.edu/cloudcv/matlab/", params_data, files=params)
	
	print Fore.BLUE + "Text:   "+request.text+"\n\n\n"
        print Fore.RESET
    except Exception as e:
	print e
