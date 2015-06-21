import threading

from socketIO_client import SocketIO
import redis
from colorama import init
import requests
from utility import logging
import utility.job as job
import traceback
import os
import local_server
from urlparse import urlparse
from os.path import splitext, basename
from utility import conf
import json

init()
socketio = None

#import logging.log
#logging.log.basicConfig(level=logging.log.DEBUG)

class SocketIOConnection(threading.Thread):
    """
    Configures a socket client to connect to CloudCV server so data upload can start. Once the data upload is finished client waits for the result. 

    :param executable: Name of the executable to be run on CloudCV servers.
    :type executable: str
    :param imagepath: Path of the input directory.
    :type imagepath: str
    """
    _redis_obj = None
    """
    An instance of Redis class.    
    """
    _pubsub_obj = None
    """
    A publisher/subscriber object.
    """

    def __init__(self, executable='', imagepath=''):
        threading.Thread.__init__(self)

        self._executable = str(executable)
        self._imagepath = str(imagepath)
        self.setupRedis()
        

    def setupRedis(self):
        """
        Instantiates a Redis object at specfied port and starts listening to the ``intercomm2`` channel. 

        :return: A thread containing listner for the Redis channel.  
        """
        self._redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._pubsub_obj = self._redis_obj.pubsub()
        self._pubsub_obj.subscribe('intercomm2')

       
        

    def run(self):
        """
        An entry point for the Socket Connection thread.
        """
        logging.log('I', 'Starting Socket Connection Thread')

        self.setupSocketIO()

        logging.log('I', 'Exiting Socket Connection Thread')


    def connection(self, *args):
        """
        A handler method for ``connect`` event of the socket connection. 
        """
        print 'Connected using websockets'

    def on_error_response(self, *args):
        """
        Error handler for the socket connection. In case of an error, It publishes an end flag across the channel ``intercomm``.
        """
        error_message = args[0]

        if('error' in error_message):
            print error_message['error']
        if('end' in error_message):
            self._redis_obj.publish('intercomm', '***end***')

    def on_aaa_response(self, *args):
        """
        Handler for messages received during the socket connection. Depending on the message received this method
        can assign a ``jobID``, ``socketID``, provides job completion acknowledgment, gives output of a job. At the end, the resultant image/text file
        is downloaded from the message received. 
        """
        message = args[0]

        if ('socketid' in message):
            self._socketid = message['socketid']
            self._redis_obj.set('socketid',self._socketid)


        if ('jobid' in message):
            print 'Received JobID: ' + message['jobid']
            job.job.jobid = message['jobid']

        if ('name' in message):
            logging.log('O',message['name'])
            # self.socket_io.emit('send_message', self._executable)

        if ('done' in message):
            self.socket_io.emit('send_message', self._executable)

        if ('jobinfo' in message):
            # logging.log('O', 'Received information regarding the current job')
            print message['jobinfo']
            job.job.jobinfo = message['jobinfo']

        if ('data' in message):
            logging.log('O', message['data'])
            job.job.output = message['data']

            if(job.job.jobid is None):
                job.job.jobid = ''

            resultpath = self._imagepath.rstrip('/') + '/' + job.job.jobid

            job.job.resultpath = resultpath
            job.job.executable = self._executable
            print "Data Received from Server"

            self._redis_obj.publish('intercomm', '***end***')

        if ('picture' in message):
            logging.log('D', message['picture'])

            resultpath = self._imagepath.rstrip('/') + '/' + message['jobid']

            job.job.setJobID(message['jobid'])
            job.job.resultpath = resultpath
            job.job.executable = self._executable

            try:
                if not os.path.exists(resultpath):
                    os.makedirs(resultpath)
                    os.chmod(resultpath, 0775)
                i =0
                while i<10:
                    try:
                        file = requests.get(os.path.join(conf.BASE_URL + message['picture']))
                        file_name = basename(urlparse(message['picture']).path)

                        f = open(resultpath + '/' + file_name, 'wb')
                        f.write(file.content)
                        f.close()

                        job.job.addFiles(resultpath + '/' + file_name)
                        logging.log('D', 'File Saved: ' + resultpath + '/' + file_name)
                        break
                    except Exception as e:
                        print 'Error Connecting to CloudCV. Will try again'
                    i+=1

            except Exception as e:
                logging.log('W', str(traceback.format_exc()))
                logging.log('W', str('possible reason: Output format improper'))



        if ('mat' in message):
            logging.log('D', message['mat'])
            file = requests.get(os.path.join(conf.BASE_URL, message['mat']))
            with open(self._imagepath + '/results' + self._socketid + '.txt', 'wb') as f:
                f.write(file.content)
            logging.log('D', 'Results Saved: ' + self._imagepath + '/results' + self._socketid + '.txt')

        if ('request_data' in message):
            print 'Data request from Server'
            self.socket_io.emit('send_message', 'data')

        if ('exit' in message):
            logging.log('W', message['exit'])
            self._redis_obj.publish('intercomm', '***end***')

    def setupSocketIO(self):
        """
        Establishes a socket connection and adds event handlers for ``connect``, ``message``, ``error`` events.
        """
        global socketio

        try:
            self.socket_io = SocketIO(conf.SOCKET_URL, 80)
            self.socket_io.on('connect', self.connection)
            self.socket_io.on('message', self.on_aaa_response)
            self.socket_io.on('error', self.on_error_response)
            socketio = self.socket_io
            self.socket_io.emit('getsocketid','socketid')
            print "socket waiting started"
            self.socket_io.wait()
            print 'Socket waiting finished. \n'

        except Exception as e:
            logging.log('W', e)
            raise SystemExit
