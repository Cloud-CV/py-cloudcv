import json
from logging import log, ArgumentError
import job

class ConfigParser:
    data = None
    """
    Contains info from the ``config`` attribute of the :doc:`config file <configfile>`
    """
    exec_name = None
    """
    Name of the executable. See :ref:`this <functionalities>` for available executables.
    """
    source_path = None
    """
    Path of the input directory.
    """
    output_path = None
    """
    Path where output will be stored.
    """
    params = None
    """
    Set of config file attributes.
    """
    maxim = None
    """

    """

    def __init__(self):
        pass

    def changePath(self):
        """
        If a user provides different input/output paths and doesn't want to use the ones mentioned in the config.json, then the default paths
        are overriden using this function. Used :func:`here <utility.parseArguments.ConfigParser.parseArguments>`
        """
        for d in self.data:
            if d['name'] == self.exec_name:
                self.source_path = d['path']
                self.output_path = d['output']

    def setParams(self):
        """
        Sets the config parameters for a job.
        """
        for d in self.data:
            if d['name'] == self.exec_name:
                self.params = d['params']
                #print str(self.params)

    def getParams(self):
        #pprint(self.params)
        pass

    def readConfigFile(self, file):
        """
        Method to read the config.json file and obtain the required config attributes.

        :param file: Path to the `config.json` file.
        :type file: str 
        """
        data_file = open(file, 'r').read()
        complete_data = json.loads(data_file)
        self.data = complete_data['config']
        self.exec_name = complete_data['exec']
        self.maxim = int(complete_data['maxim'])

    def writeToConfigFile(self, file):
        """
        Method to write to the :doc:`config.json <configfile>` file. 
        """
        data_file = open(file, 'w')
        json.dump(self.complete_data, data_file)

    def parseArguments(self, arg, file):
        """
        Parses the command line args, if any. If a required config attribute is not provided explicitly then 
        its value in config.json file is used as a default.

        :param args: Contains all the config parameters from user. 
        :type args: dict
        :param file: Path to the config.json file.
        :type file: str
        """
        sourcepath = None
        resultpath = None
        name = None

        i = 0

        if 'input' in arg:
            sourcepath = arg['input']
        if 'output' in arg:
            resultpath = arg['output']
        if 'exec' in arg:
            name = arg['exec']

        try:
            self.readConfigFile(file)

            if name is not None:
                self.exec_name = name
            elif self.exec_name is None:
                raise ArgumentError(0)
            elif name is None and self.exec_name is not None:
                name = self.exec_name

            self.changePath()

            if sourcepath is not None:
                self.changeSourcePath(sourcepath, name)
            elif self.source_path is None:
                raise ArgumentError(1)

            if resultpath is not None:
                self.changeOutputPath(resultpath, name)
            elif self.output_path is None:
                raise ArgumentError(2)

            self.setParams()
        except ArgumentError as e:
            log('W', str(e))

    def changeSourcePath(self, path, execname):
        """
        Changes the config source path to that of provided by the user. 

        :param path: Source path of the images. 
        :type path: str
        :param execname: Name of the :ref:`executable <functionalities>` to be run. 
        :type execname: str
        """
        try:
            for d in self.data:
                if d["name"] == execname:
                    d["path"] = path
                    self.source_path = path
                    return
            raise ArgumentError(0)

        except ArgumentError as e:
            log('W', str(e))
            raise SystemExit

    def changeOutputPath(self, path, execname):
        """
        Changes the config output path to that of provided by user.

        :param path: Path where output will be stored. 
        :type path: str
        :param execname: Name of the :ref:`executable <functionalities>` to be run.
        """ 
        try:
            for d in self.data:
                if d["name"] == execname:
                    d["output"] = path
                    self.output_path = path
                    return

            raise ArgumentError(0)

        except ArgumentError as e:
            log('W', str(e))
            raise SystemExit

    def verify(self):
        """
        Verifies the config attributes provided by user.
        """
        if self.exec_name == ' ':
            log('W', 'Undefined Executable Name. Please try again')
            raise SystemExit
        if self.source_path == ' ':
            log('W', 'Empty Input Folder Path. Please try again')
            raise SystemExit
        if self.output_path == ' ':
            log('W', 'Empty Output Path. Please try again')
            raise SystemExit
