__author__ = 'dexter'

class Job:
    jobid = None
    output = ''
    files = list()
    def __init__(self, imagepath=None, resultpath=None, executable=None):
        self.imagepath = imagepath
        self.resultpath = resultpath
        self.executable = executable

    def setJobParameters(self, imagepath=None, resultpath=None, executable=None):
        self.imagepath = imagepath
        self.resultpath = resultpath
        self.executable = executable

    def setJobID(self, jobid):
        self.jobid = jobid

    def setOutput(self, output):
        self.output = output

    def addFiles(self, path):
        self.files.append(path)
job = Job()