__author__ = 'dexter'
import os, traceback
from logger import warn, info, debug, error

class Job:
    """
    This class represents a Job that is submitted to the servers for execution. 
    
    :param imagepath: Input path for the images. 
    :type imagepath: str
    :param resultpath: Path where result file is created.
    :type resultpath: str
    :param executable: Name of the executable. Available options are :ref:`here <functionalities>`
    :type executable: str
    """

    jobid = None
    """
    A job identifier.
    """
    output = ''
    """
    Output obtained from the executable. 
    """
    files = list()
    """
    A list of files associated with a job. 
    """
    jobinfo = {}
    
    def __init__(self, imagepath=None, resultpath=None, executable=None):
        self.imagepath = imagepath
        self.resultpath = resultpath
        self.executable = executable

    def setJobParameters(self, imagepath=None, resultpath=None, executable=None):
        """
        Assigns Job parameters.

        .. seealso:: :class:`Constructor <utility.job.Job>` of this class.
        """
        self.imagepath = imagepath
        self.resultpath = resultpath
        self.executable = executable

    def setJobID(self, jobid):
        """
        A setter method for JobID.

        :param jobid: A job identifier. 
        :type jobid: int
        """
        self.jobid = jobid

    def setOutput(self, output):
        """
        A setter method for output obtained from executable.

        :param output: Output obtained from a Job.
        """
        self.output = output

    def addFiles(self, path):
        """
        Associates a job with its result path. See :func:`here <connections.socketConnection.SocketIOConnection.on_aaa_response>`
        
        :param path: Path of the output file asscoiated with a Job. 
        :type path: str
        """
        self.files.append(path)

    def outputToFile(self):
        """
        Creates a output file with appropriate permissions and writes obtained output to it. 
        """
        try:
            if not os.path.exists(self.resultpath):
                os.makedirs(self.resultpath)
                os.chmod(self.resultpath, 0776)

            if self.output != '':
                f = open(self.resultpath + '/output.txt', 'w')
                f.write(self.output)
                f.close()
                info('Output Written to File: ' + self.resultpath + '/output.txt')
            else:
                info('No Output Present')
        except OSError as oserror:
            warn('Check Output Path in your config. This is usually caused while trying to write in a directory with limited permissions')
            warn(str(traceback.format_exc()))

        except Exception as e:
            warn('Error Writing Output.')
            warn(str(traceback.format_exc()))

job = Job()