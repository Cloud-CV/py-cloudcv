import json
from pprint import pprint

class ConfigParser:
    data=None
    
    def __init__(self):
        pass

    def readConfigFile(self,file):
        data_file = open('config.json','r').read()
        self.data = json.loads(data_file)
    
    def writeToConfigFile(self, file):
        data_file = open(file,'w')
        json.dump(self.data, data_file)

    def parseArguments(self, arg):
        print arg

    def changeSourcePath(self,path, execname):
        for d in self.data:
            if(d["name"]==execname):
                d["path"] = path
                pprint(d["path"])

c = ConfigParser()
c.readConfigFile('config.json')
c.changeSourcePath("/home/dexter","ImageStitch")

