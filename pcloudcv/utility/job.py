__author__ = 'dexter'
import os, traceback

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

    def outputToFile(self):
        try:
            if not os.path.exists(self.resultpath):
                os.makedirs(self.resultpath)
                os.chmod(self.resultpath, 0776)

            if self.output != '':
                f = open(self.resultpath + '/output.txt', 'w')
                f.write(self.output)
                f.close()
                print 'Output Written to File: ' + self.resultpath + '/output.txt'
            else:
                print 'No Output Present'
        except Exception as e:
            print str(traceback.format_exc())

job = Job()