__author__ = 'dexter'

class Job:
    jobid = None

    def __init__(self, imagepath=None, resultpath=None, executable=None):
        self.imagepath = imagepat.h
        self.resultpath = resultpath
        self.executable = executable

    def setJobParameters(self, imagepath=None, resultpath=None, executable=None):
        self.imagepath = imagepath
        self.resultpath = resultpath
        self.executable = executable

    def setJobID(self, jobid):
        self.jobid = jobid

job = Job()