import json
from logging import log, ArgumentError
import job

class ConfigParser:
    data = None
    exec_name = None
    source_path = None
    output_path = None
    params = None
    maxim = None
    def __init__(self):
        pass

    def changePath(self):
        for d in self.data:
            if d['name'] == self.exec_name:
                self.source_path = d['path']
                self.output_path = d['output']

    def setParams(self):
        for d in self.data:
            if d['name'] == self.exec_name:
                self.params = d['params']
                #print str(self.params)

    def getParams(self):
        #pprint(self.params)
        pass

    def readConfigFile(self, file):
        data_file = open(file, 'r').read()
        complete_data = json.loads(data_file)
        self.data = complete_data.get('config')
        self.maxim = int(complete_data.get('maxim'))
        self.server_port = int(complete_data.get('server_port'))
        return complete_data

    def writeToConfigFile(self, file):
        data_file = open(file, 'w')
        json.dump(self.complete_data, data_file)

    def parseArguments(self, arg, config_file):
        i = 0
        sourcepath = arg.get('input')
        resultpath = arg.get('output')
        name = arg.get('exec')

        try:
            config_dict = self.readConfigFile(config_file)

            # exec param is not mentioned in config.json and config dictionary
            if arg.get('exec') is None and config_dict.get('exec') is None:
                raise ArgumentError(0)

            if arg.get('exec') is None and config_dict.get('exec') is not None:
                name = config_dict.get('exec')

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
        for d in self.data:
            if d["name"] == execname:
                d["path"] = path
                self.source_path = path


    def changeOutputPath(self, path, execname):
        for d in self.data:
            if d["name"] == execname:
                d["output"] = path
                self.output_path = path
                return

    def verify(self):
        if self.exec_name == ' ':
            log('W', 'Undefined Executable Name. Please try again')
            raise SystemExit
        if self.source_path == ' ':
            log('W', 'Empty Input Folder Path. Please try again')
            raise SystemExit
        if self.output_path == ' ':
            log('W', 'Empty Output Path. Please try again')
            raise SystemExit
