import json
from log import log, ArgumentError


class ConfigParser:
    data = None
    exec_name = None
    source_path = None
    output_path = None
    params = None

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
        self.data = complete_data['config']
        self.exec_name = complete_data['exec']

    def writeToConfigFile(self, file):
        data_file = open(file, 'w')
        json.dump(self.data, data_file)

    def parseArguments(self, arg, file):
        sourcepath = None
        resultpath = None
        name = None

        i = 0

        if len(arg) == 3:
            if arg[0] != '':
                sourcepath = arg[0]
            if arg[1] != '':
                resultpath = arg[1]
            if arg[2] != '':
                name = arg[2]

        while i < len(arg):
            if arg[i] == '-E':
                name = arg[i + 1]
            if arg[i] == '-I':
                sourcepath = arg[i + 1]
            if arg[i] == '-O':
                resultpath = arg[i + 1]
            i += 2
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
        if self.exec_name == ' ':
            log('W', 'Undefined Executable Name. Please try again')
            raise SystemExit
        if self.source_path == ' ':
            log('W', 'Empty Input Folder Path. Please try again')
            raise SystemExit
        if self.output_path == ' ':
            log('W', 'Empty Output Path. Please try again')
            raise SystemExit
