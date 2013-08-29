import threading
import time
import redis

import urllib2, json, requests, pprint, re

from os import listdir
from os.path import isfile, join

from colorama import init
from colorama import Fore, Back, Style

from poster.encode import multipart_encode

from log import log

exitFlag = 0
socketid = ''
init()

class UploadData (threading.Thread):
   
    def __init__(self, config_parser):
        threading.Thread.__init__(self)
        
        self._source_path = config_parser.source_path
        self._output_path = config_parser.output_path
        self._exec_name = config_parser.exec_name
        self._params = config_parser.params

        self._redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._pubsub = self._redis_obj.pubsub()
        self._pubsub.subscribe('intercomm')
        
        redisThread = RedisListenForPostThread(self._pubsub, self._redis_obj)
        redisThread.start()
              
    def run(self):
        log('I','Starting Post Request')
        self.sendPostRequest()
        log('I','Exiting From the Post Request Thread')

    #send post requests containing images to the server    
    def sendPostRequest(self):
        global socketid

        params_for_request={}
        params_data={}
        
        token = self.getRequest('http://godel.ece.vt.edu/cloudcv/matlab')
        
        if(token == None):
            print 'token not found'
            raise SystemExit
        
        
        files = self.filesInDirectory(self._source_path)
        
        i=0
        for f in files:
            params_for_request['file'+str(i)]=open(self._source_path+'/'+f, 'rb')
            i+=1
        
        params_data['token']=token
        params_data['count']=str(len(files))
        params_data['socketid']=''
        params_data['executable']=self._exec_name
        #params_data['exec_params'] = self._params
         
        while(True):
            if socketid != '':
                params_data['socketid']=socketid
                break
            else:
                time.sleep(1)
                print '\nwaiting for socket connection to complete'
                 
        log('I',str(params_for_request))
        log('I',str(params_data)) 
        datagen, headers = multipart_encode(params_for_request)
        
        try:	
            request = requests.post("http://godel.ece.vt.edu/cloudcv/matlab/", params_data, files=params_for_request)
            log('I','Text:   '+request.text)
        except Exception as e:
            log('W',e)

    #get request to obtain csrf token
    def getRequest(self,url):
        token='' 
        try:
            data = requests.get(url) 
            for line in data:
            
                m = re.search('(META:{\'CSRF_COOKIE\': \')((\\w)+)(\',)', line)
                if(m!=None):
                    token = m.group(2)
        
        except Exception as e:
            log('W',e)
        
        return token


    #get all files in the directory and create a params dictionary. 
    def filesInDirectory(self,dir):
        onlyfiles = [ f for f in listdir(dir) if isfile(join(dir,f)) !=None ]
        onlyfiles = [ f for f in onlyfiles if(re.search('([^\s]+(\.(jpg|png|gif|bmp))$)',str(f))!=None) ] 
        print onlyfiles
        return onlyfiles



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
                  

