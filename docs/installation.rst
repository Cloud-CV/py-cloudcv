Installation
************
**Creating a virtual-env**

::

    virtualenv cloudcv_env
    source cloudcv_env/bin/activate

**Cloning**

::

    git clone https://github.com/batra-mlp-lab/pcloudcv.git pcloudcv
    cd pcloudcv/pcloudcv

**Pre-requisites**

1. Please ensure that redis-server is installed and running in
   background. Follow the instructions on this page - till the end of
   the page. `Redis Quickstart`_

   On OSX:
   http://www.richardsumilang.com/blog/2014/04/04/how-to-install-redis-on-os-x/
   ( I hope this is easier. Didn’t try it myself)

2. Port *8000* should be free
3. The h5py in requirements.txt needs to have HDF5 installed before. On
   Ubuntu 12.04 it’s called “libhdf5-serial-dev”, otherwise it cannot
   find the path to “hdf5.h”. Using Synaptic seems best to have all the
   paths set properly. On Ubuntu: ``sudo apt-get install libhdf5-dev``
   On OSX : ``brew tap homebrew/science`` , ``brew install hdf5``
4. In addition, a C compiler and the necesarry Python development
   environment are needed:

   Ubuntu/Debian: sudo apt-get install python-dev build-essential
   (untested, please report back if more packages are needed here) Mac
   OS X: Install XCode (usually bundled with the Mac OS X installation
   disks)

   On ubuntu 12:

   ::

       sudo apt-get install libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev    tcl8.5-dev tk8.5-dev python-tk

   On Ubuntu 14:

   ::

       sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

   On Mac:

   ::

       brew install libtiff libjpeg webp little-cms2

**Installing Dependencies**

::

    for req in $(cat requirements.txt); do pip install $req; done

The dependencies are not installed in order when using requirements.txt
and therefore this is a workaround. This will ensure proper installation
of all the packages.

| **Config File**
| It is important to ensure that config file is well setup. You can look
  at the sample config.json and modify it to suit your needs
| 1. **path:**
|  This is the input path. It should be the full path to where the files
  are located.
|  It can either take this form if you want to upload images from local
  directory:
|  ``"path": "local: /home/dexter/Pictures/test_upload/kitchen",``
|  or this form if you have files in your dropbox. Please note that
  dropbox is relative to /Apps/CloudCV folder.
|  ``"path": "dropbox: /1",``
| 2. **exec:** This executable should contain the name of the executable
  you want to run

3. **output:** This should contain the full path to the output
   directory. Please note that there shouldn’t be a local: prefix before
   the output directory path. Also in-case the input is an input
   directory, the output path is not considered and the results are
   uploaded in their corresponding jobid folde

.. _Redis Quickstart: http://redis.io/topics/quickstart