from __builtin__ import str
import threading
import time
import re
import traceback
from os import listdir, makedirs, chmod
from os.path import isfile, join, exists

from concurrent.futures import ThreadPoolExecutor 

import redis
import requests
from utility.logger import debug, info, warn, error
from utility import accounts

from PIL import Image

import utility.job as job

exitFlag = 0


class UploadData(threading.Thread):
    """
    Starts a data uploading instance in a new thread. This instance subscribs to a Redis Channel ``intercomm`` and starts 
    listening to it in a new thread.  

    :param config_parser: An instance of :class:`ConfigParser <utility.parseArguments.ConfigParser>` class.
    :type config_parser: :class:`type <utility.parseArguments.ConfigParser>`

    """
    socketid = None
    def __init__(self, config_parser):
        self.source_path = config_parser.source_path
        self.output_path = config_parser.output_path
        self.exec_name = config_parser.exec_name
        self.params = config_parser.params
        self.maxim = config_parser.maxim
        self._redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)
        self._pubsub = self._redis_obj.pubsub()
        self._pubsub.subscribe('intercomm')

    def run(self):
        """
        Entry point for UploadData thread. Details about the uploading method :func:`here <connections.uploadData.UploadData.sendPostRequest>`.
        """
        info('Starting Post Request')
        self.sendPostRequest()
        info('Exiting From the Post Request Thread')

    #get all files in the directory and create a params dictionary.
    def filesInDirectory(self, dir):
        """
        A regex filter for images in the input directory.

        :param dir: An input directory. 
        :type dir: str
        :return: A list of all the image files that match the regex for image formats. 
        """ 
        onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f)) is not None]
        onlyfiles = [f for f in onlyfiles if (re.search('([^\s]+(\.(jpg|png|gif|bmp|jpeg|JPG|PNG|GIF|BMP|JPEG))$)', str(f)) is not None)]
        return onlyfiles

    def identifySourcePath(self):
        """
        Identifies whether the input path is a local directory or a Dropbox folder. 

        :return: A tuple containing the ``source`` (dropbox/local) and the source path. 
        """
        list = self.source_path.split(':')
        if len(list) < 2:
            raise Exception('Image Input Path not in proper format. ')
        return list[0].lower().strip(), list[1].strip()

    def addAccountParameters(self, params_data, source):
        """
        Read the config.cfg file and adds required Google/Dropbox account parameters.

        :param params_data: Contains userID and/or Dropbox token.
        :type params_data: dict
        :param source: Specifies whether to upload the images from Dropox or a local directory.
        :type source: str
        """
        if accounts.login_required:
            params_data['userid'] = accounts.account_obj.getGoogleUserID()

        if source == 'dropbox':
            if accounts.dropboxAuthentication is False:
                accounts.dropboxAuthenticate()
                dbtoken = self._redis_obj.get('dropbox_token')
            else:
                dbtoken = self._redis_obj.get('dropbox_token')

            params_data['userid'] = accounts.account_obj.getGoogleUserID()
            params_data['dropbox_token'] = dbtoken
            debug('Dropbox Token: ', params_data['dropbox_token'])

    def resize(self, files, resized_path, source_path):
        """
        Resizes the images depending on the ``maxim`` attribute of the :doc:`config file <configfile>`
        
        :param files: A list of image files.
        :type files: list
        :param resized_path: Path of the new directory contaning resized images.
        :type resized_path: str
        :param source_path: Path of the input directory.
        """
        for f in files:
            if not exists(resized_path.rstrip('/') + '/' + f):
                im = Image.open(join(source_path.rstrip('/'),f))
                size = self.maxim
                if im.size[0] > size or im.size[1] > size:
                    im.thumbnail((size, size), Image.ANTIALIAS)
                im.save(resized_path.rstrip('/') + '/' + f)
            else:
                warn("Resized image already present in the directory")
    def openFile(self, path_name):
        """
        Opens an image in binary read mode. 
        
        :param path_name: Path to an image.
        :type path: str
        :return: Binary content of an image. 
        """
        f = open(path_name, 'rb')
        return f.read()

    def addFileParameters(self, source, source_path, params_data, params_for_request):
        """
        Checks input directory against corner cases such as empty directory, upload limit. The `dict` to be uploaded
        is updated with the binary data of the image files.

        :param source: Source of the input images. (dropbox/local)
        :type source: str
        :param source_path: In case of local directory, this contains the absolute path of input folder. In case of input from Dropbox, the path is relative to ``/Apps/CloudCV``.
        :type source_path: str 
        :param params_data: Contains payload for the POST request. Contains ``csrf token``, ``Dropbox path``, ``Dropbox token``, ``Google UserID``, ``SocketID``, and ``Executable parameters``. 
        :type params_data: dict
        """
        if source == 'dropbox':
            params_data['dropbox_path'] = source_path
        else:  # path given by user is on local system
            files = self.filesInDirectory(source_path.rstrip('/'))
            i = 0

            if not exists(join(source_path.rstrip('/'), 'resized')):
                makedirs(join(source_path.rstrip('/'), 'resized'))
                chmod(join(source_path.rstrip('/'), 'resized'), 0776)

            self.resize(files, join(source_path.rstrip('/'), 'resized'), source_path)

            if len(files) > 50:
                raise Exception("No. of files is more than the specified limit:50")
            if len(files) == 0:
                raise Exception("No of images in the directory is zero. "
                                "Please check the path, and the extension of the files present.")
            warn('No of files to be uploaded: '+str(len(files)))
            for f in files:
                params_for_request[f] = open(source_path+'/resized/'+f, 'rb')
                i += 1

            params_data['count'] = str(len(files))


    
    def sendPostRequest(self):
        """
        Sends POST request containing the images to the server. For the payload data refer ``params_data`` parameter of :func:`this <connections.uploadData.UploadData.addFileParameters>` function.
        """
        try:
            params_for_request = {}
            params_data = {}

            token = self.getRequest('http://cloudcv.org/api')
            
            if token is None:
                warn('token not found')
                raise SystemExit

            source, source_path = self.identifySourcePath()
            self.addAccountParameters(params_data, source)
            self.addFileParameters(source, source_path, params_data, params_for_request)


            job.job.imagepath = source_path

            params_data['token'] = token
            params_data['socketid'] = ''
            params_data['executable'] = self.exec_name
            params_data['exec_params'] = str(self.params)

            self.socketid = self._redis_obj.get('socketid')
            while True:
                if self.socketid != '' and self.socketid is not None:
                    params_data['socketid'] = (self.socketid)
                    info('SocketID: '+str(self.socketid))
                    break
                else:
                    self.socketid = self._redis_obj.get('socketid')
                    time.sleep(3)
                    warn('Waiting for Socket Connection to complete')



            # for k,v in params_for_request.items():
            #     params_data[k] = v
            debug('Starting The POST request')
            for i in range(1,5):
                try:
                    request = requests.post("http://cloudcv.org/api/", data=params_data,
                                            files=params_for_request)

                    warn('Please wait while CloudCV runs your job request')
                    break
                except Exception as e:
                    warn('Error in sendPostRequest' + str(traceback.format_exc()))
        except Exception as e:
            warn(str(traceback.format_exc()))
            self._redis_obj.publish('intercomm', '***end***')


    #get request to obtain csrf token
    def getRequest(self, url):
        """
        Sets a CSRF token as a session cookie. 
        """
        client = requests.session()
        client.get('http://cloudcv.org/classify')
        token = client.cookies['csrftoken']
        return token
