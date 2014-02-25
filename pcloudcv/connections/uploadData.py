from __builtin__ import str
import threading
import time
import re
from os import listdir
from os.path import isfile, join

import redis
import requests
from colorama import init
from poster.encode import multipart_encode

from utility import logging
from utility import accounts
import poster
import urllib2

exitFlag = 0
socketid = ''
init()


class UploadData(threading.Thread):
    def __init__(self, config_parser):
        threading.Thread.__init__(self)

        self.source_path = config_parser.source_path
        self.output_path = config_parser.output_path
        self.exec_name = config_parser.exec_name
        self.params = config_parser.params

        self._redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._pubsub = self._redis_obj.pubsub()
        self._pubsub.subscribe('intercomm')

        redisThread = RedisListenForPostThread(self._pubsub, self._redis_obj)
        redisThread.setDaemon(True)
        redisThread.start()

    def run(self):
        logging.log('I', 'Starting Post Request')
        self.sendPostRequest()
        logging.log('I', 'Exiting From the Post Request Thread')

    #get all files in the directory and create a params dictionary.
    def filesInDirectory(self, dir):
        onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f)) is not None]
        onlyfiles = [f for f in onlyfiles if (re.search('([^\s]+(\.(jpg|png|gif|bmp))$)', str(f)) is not None)]
        return onlyfiles

    def identifySourcePath(self):
        list = self.source_path.split(':')

        print list[0].lower().strip(), list[1].strip()
        return list[0].lower().strip(), list[1].strip()

    def addAccountParameters(self, params_data, source):
        if accounts.login_required:
            params_data['userid'] = accounts.account_obj.getGoogleUserID()
            print params_data['userid']

        if source == 'dropbox':
            if accounts.dropboxAuthentication is False:
                accounts.dropboxAuthenticate()

            params_data['userid'] = accounts.account_obj.getGoogleUserID()
            params_data['dropbox_token'] = accounts.account_obj.dbaccount.access_token
            print 'Dropbox Token: ', params_data['dropbox_token']

    def addFileParameters(self, source, source_path, params_data, params_for_request):
        print source
        print source_path

        if source == 'dropbox':
            params_data['dropbox_path'] = source_path
        else:  # path given by user is on local system
            files = self.filesInDirectory(source_path)
            i = 0
            for f in files:
                params_for_request['file' + str(i)] = open(source_path + '/' + f, 'rb')
                i += 1
            params_data['count'] = str(len(files))

    #send post requests containing images to the server    
    def sendPostRequest(self):
        global socketid

        params_for_request = {}
        params_data = {}

        token = self.getRequest('http://godel.ece.vt.edu/cloudcv/api')

        if token is None:
            logging.log('W', 'token not found')
            raise SystemExit

        source, source_path = self.identifySourcePath()

        self.addAccountParameters(params_data, source)
        self.addFileParameters(source, source_path, params_data, params_for_request)

        params_data['token'] = token
        params_data['socketid'] = ''
        params_data['executable'] = self.exec_name
        params_data['exec_params'] = str(self.params)

        while True:
            if socketid != '':
                params_data['socketid'] = socketid
                break
            else:
                time.sleep(1)
                logging.log('W', 'Waiting for Socket Connection to complete')


        # for k,v in params_for_request.items():
        #     params_data[k] = v

        logging.log('D', str(params_for_request))
        logging.log('D', str(params_data))

        try:
            request = requests.post("http://godel.ece.vt.edu/cloudcv/api/", data=params_data, files=params_for_request)
            logging.log('D', 'Text:   ' + request.text)
        except Exception as e:
            logging.log('W', 'Error in sendPostRequest' + str(e))

    #get request to obtain csrf token
    def getRequest(self, url):
        token = ''
        try:
            data = requests.get(url)
            for line in data:

                m = re.search('(META:{\'CSRF_COOKIE\': \')((\\w)+)(\',)', line)
                if m is not None:
                    token = m.group(2)

        except Exception as e:
            logging.log('W', e)

        return token


"""Redis Connection for Inter Thread Communication"""
class RedisListenForPostThread(threading.Thread):
    def __init__(self, ps, r):
        threading.Thread.__init__(self)
        self.r = r
        self.ps = ps

    def run(self):
        logging.log('I', 'Starting Listening to Redis Channel for HTTP Post Requests')
        while (True):
            shouldEnd = listenToChannel(self.ps, self.r)
            if (shouldEnd):
                break
        logging.log('I', 'Exiting Redis Thread for HTTP Post requests')


def listenToChannel(ps, r):
    global socketid

    for item in ps.listen():
        if item['type'] == 'message':
            if item['channel'] == 'intercomm':

                if '***end***' in item['data']:
                    r.publish('intercomm2', '***endcomplete***')
                    return True
                else:
                    socketid = item['data']

    return False
                  

