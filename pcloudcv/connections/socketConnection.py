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
    _executable = ''
    _imagepath = ''
    _redis_obj = None
    """
    An instance of Redis class.    
    """
    _pubsub_obj = None
    """
    A publisher/subscriber object.
    """

    def __init__(self, executable, imagepath):
        threading.Thread.__init__(self)

        self._executable = str(executable)
        self._imagepath = str(imagepath)

        redis_thread = self.setupRedis()
        redis_thread.setDaemon(True)
        redis_thread.start()

    def setupRedis(self):
        """
        Instantiates a Redis object at specfied port and starts listening to the ``intercomm2`` channel. 

        :return: A thread containing listner for the Redis channel.  
        """
        self._redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._pubsub_obj = self._redis_obj.pubsub()
        self._pubsub_obj.subscribe('intercomm2')

        redis_thread = RedisListen(self._pubsub_obj, self._redis_obj)
        return redis_thread

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
            self._redis_obj.publish('intercomm', message['socketid'])
            self._socketid = message['socketid']

        if ('jobid' in message):
            print 'Received JobID: ' + message['jobid']
            job.job.jobid = message['jobid']

        if ('name' in message):
            logging.log('O',message['name'])
            # self._socket_io.emit('send_message', self._executable)

        if ('done' in message):
            self._socket_io.emit('send_message', self._executable)

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
            self._socket_io.emit('send_message', 'data')

        if ('exit' in message):
            logging.log('W', message['exit'])
            self._redis_obj.publish('intercomm', '***end***')

    def setupSocketIO(self):
        """
        Establishes a socket connection and adds event handlers for ``connet``, ``message``, ``error`` events.
        """
        global socketio

        try:
            self._socket_io = SocketIO(conf.SOCKET_URL, 80)
            self._socket_io.on('connect', self.connection)
            self._socket_io.on('message', self.on_aaa_response)
            self._socket_io.on('error', self.on_error_response)
            socketio = self._socket_io
            self._socket_io.wait()
            print 'Socket waiting finished. \n'

        except Exception as e:
            logging.log('W', e)
            raise SystemExit


class RedisListen(threading.Thread):
    """
    Listens to the Redis channel.
    """
    def __init__(self, ps, r):
        threading.Thread.__init__(self)
        self._redis_obj = r
        self._pubsub_obj = ps

    def run(self):
        logging.log('I', 'Listening to Redis Channel')
        while (True):
            shouldEnd = self.listenToChannel(self._pubsub_obj, self._redis_obj)
            if (shouldEnd):
                break
        logging.log('I', 'Ending Listening to Redis Channel')

    def listenToChannel(self, ps, r):
        """Listens to the Redis channel ``intercomm2`` for messages. Depending on the message content
        either ends the socket connection to the server or poll the CloudCV server for a socketID. 

        :param ps: A publisher/subscriber instance. 
        :param r: A redis object. 
        :return: A boolean flag denoting the need to end the socket connection.   
        """
        global socketio

        for item in ps.listen():
            if item['type'] == 'message':
                if '***endcomplete***' in item['data']:
                    socketio.disconnect()
                    return True
                try:
                    if item['type'] == 'message':
                        socketio.emit('getsocketid', 'socketid')
                except Exception as e:
                    print e
        return False
