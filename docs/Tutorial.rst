Tutorial
********

Installation
------------

| To start using PCloudCV is easy. You can download PCloudCV using:
| https://github.com/batra-mlp-lab/pcloudcv/wiki/Setup

You need to make sure you have redis-server installed and running before
you can use the python APIs.

Please follow this link to install it: http://redis.io/topics/quickstart

Sample Application:
-------------------

Steps to write a simple application using CloudCV APIs can be seen in
run.py

1. Import PCloudCV class from pcloudcv module

   .. code:: python

           from pcloudcv import PCloudCV

2. Start by creating a dictionary containing three parameters:

   1. Full Path to Input Folder where all the images are present, ignore
      it if you want to use path mentioned in config file. Prefix the
      path with “local:” if its a local path or “dropbox:” if its a
      dropbox path
   2. Full Path to Output Folder where the results will be stored,
      ignore it if you want to use path mentioned in config file.
   3. Algorithm that needs to be run. More information about the valid
      names are here. Ignore it if you want to use the name of the
      executable mentioned in the config file

      .. code:: python

          config_dict =    {'input':'local:/path/to/input/folder','output':'/path/to/output/folder','exec':'executable_name'}

3. Create a variable to store the full path to the config file. More
   information about config files here. Also create a variable to
   mention whether you want to use APIs after logging in or not.

   .. code:: python

          path_to_config_file = '/home/dexter/projects/vt/pcloudcv/pcloudcv/config.json'
          login_required = True

4. Create an object of the PCloudCV class

   .. code:: python
   
          pcv = PCloudCV(path_to_config_file, config_dict, login_required)
   
5. Start uploading images in the background using

   .. code:: python
   
          pcv.start()
   
6. The APIs will upload the result in the background. It will wait for
   results in the background so that your main application thread is not
   stuck. When the results are available, they will automatically be
   retrieved from the server and the resultant text file/image file will
   be downloaded.
   
   Complete Code:
   
   .. code:: python

   		from pcloudcv import PCloudCV
		config_dict = {'input':'/path/to/input/folder','output':'/path/to/output/folder','exec':'executable_name'}
		path_to_config_file = '/home/dexter/projects/vt/pcloudcv/pcloudcv/config.json'
		login_required = True
		pcv = PCloudCV(path_to_config_file, config_dict, login_required)
		pcv.start()
         
	   