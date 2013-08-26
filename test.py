from parseArguments import ConfigParser

c = ConfigParser()
c.readConfigFile('config.json')
c.changeSourcePath('/home/dexter','ImageStitch')
c.changeOutputPath('/home/dexter','ImageStitch')
c.writeToConfigFile('config2.json')
