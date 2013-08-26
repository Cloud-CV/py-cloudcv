import json
from pprint import pprint
from log import log, ArgumentError

class ConfigParser:
    data=None
    exec_name=None
    source_path=None
    output_path=None
    params=None

    
    def __init__(self):
        pass

    
    def changePath(self):
        for d in self.data:
            if(d['name']==self.exec_name):
                self.source_path=d['path']
                self.output_path=d['output']

    
    def setParams(self):
        for d in self.data:
            if(d['name']==self.exec_name):
                self.params=d['params']

    
    def getParams(self):
        pprint(self.params)

    
    def readConfigFile(self,file):
        data_file = open(file,'r').read()
        self.data = json.loads(data_file)
        
    
    def writeToConfigFile(self, file):
        data_file = open(file,'w')
        json.dump(self.data, data_file)

    
    def parseArguments(self, arg):
        sourcepath=None
        resultpath=None
        name=None

        i=0
        while(i<len(arg)):
            if(arg[i]=='-E'):
                name = arg[i+1]
            if(arg[i]=='-I'):
                sourcepath = arg[i+1]
            if(arg[i]=='-O'):
                resultpath = arg[i+1]
            i+=2
        if(name!=None):
            self.exec_name = name
            self.readConfigFile('config.json')
            self.changePath()
            self.setParams()

        try:
            if(sourcepath!=None):
                self.changeSourcePath(sourcepath,name)
            elif(sourcepath==None):
                raise ArugmentError(1)

            if(resultpath!=None):
                self.changeOutputPath(resultpath,name)
            elif(output_path==None):
                raise ArgumentError(2)
        except ArgumentError as e:
            log('W',str(e))
    

    def changeSourcePath(self,path, execname):
        try:
            for d in self.data:
                if(d["name"]==execname):
                    d["path"] = path
                    self.source_path = path
                    return
            raise ArgumentError(0)

        except ArgumentError as e:   
            log('W',str(e))
  

    def changeOutputPath(self, path, execname):
        try:
            for d in self.data:
                if(d["name"]==execname):
                    d["output"] = path
                    self.output_path = path
                    return

            raise ArgumentError(0)

        except ArgumentError as e:
            log('W', str(e))
                


