import threading

from socketIO_client import SocketIO
import redis
import requests
from utility.logger import info, debug, warn, error
import utility.job as job
import traceback
import os
import local_server
from urlparse import urlparse
from os.path import splitext, basename
from utility import conf
import json
from prettytable import PrettyTable
import ast
socketio = None


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
        threading.Thread.__init__(self, name="SocketIOConnection")

        self._executable = str(executable)
        self._imagepath = str(imagepath)
        
        self._redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._redis_obj.set("received_counter",0)
        debug("Socket Constructor...")
        

    def run(self):
        """
        An entry point for the Socket Connection thread.
        """
        info('Starting Socket Connection Thread')
        self.setupSocketIO()
        info('Exiting Socket Connection Thread')
        


    def connection(self, *args):
        """
        A handler method for ``connect`` event of the socket connection. 
        """
        debug('Connected using websockets.')

    def on_error_response(self, *args):
        """
        Error handler for the socket connection. In case of an error, It publishes an end flag across the channel ``intercomm``.
        """
        error_message = args[0]

        if('error' in error_message):
            error(error_message['error'])
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

            info('Received JobID: ' + message['jobid'])
            job.job.jobid = message['jobid']

        if ('name' in message):
            info(message['name'])
            # self.socket_io.emit('send_message', self._executable)

        if ('done' in message):
            self.socket_io.emit('send_message', self._executable)

        if ('jobinfo' in message):
            info(message['jobinfo'])
            job.job.jobinfo = message['jobinfo']

        if ('data' in message):
            data = ast.literal_eval(message['data'])
           
           
            table = PrettyTable(["Image","Class","Confidence"])
            for imageName in data.keys():
                # x.add_row([str(imageName),*data[i]])

                for li in data[imageName]:
                    table.add_row([imageName,li[0],li[1]])
                
            print table
            job.job.output = message['data']

            if(job.job.jobid is None):
                job.job.jobid = ''

            resultpath = self._imagepath.rstrip('/') + '/' + job.job.jobid

            job.job.resultpath = resultpath
            job.job.executable = self._executable
            debug("Data Received from Server")
            self._redis_obj.incr("received_count")
            info("Received : "+str(self._redis_obj.get("received_count")))
            # self._redis_obj.publish('intercomm', '***end***')

        if ('picture' in message):
            debug(message['picture'])

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
                        debug('File Saved: ' + resultpath + '/' + file_name)
                        break
                    except Exception as e:
                        error('Error Connecting to CloudCV. Will try again')
                    i+=1

            except Exception as e:
                warn(str(traceback.format_exc()))
                warn('possible reason: Output format improper')



        if ('mat' in message):
            debug(message['mat'])
            file = requests.get(os.path.join(conf.BASE_URL, message['mat']))
            with open(self._imagepath + '/results' + self._socketid + '.txt', 'wb') as f:
                f.write(file.content)
            debug('Results Saved: ' + self._imagepath + '/results' + self._socketid + '.txt')

        if ('request_data' in message):
            info('Data request from Server')
            self.socket_io.emit('send_message', 'data')

        if ('exit' in message):
            warn(message['exit'])
            # self._redis_obj.publish('intercomm', '***end***')
        

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
            info("Socket waiting started.")
            self.socket_io.wait()
            info('Socket waiting finished.')

        except Exception as e:
            warn(str(e))
            raise SystemExit

