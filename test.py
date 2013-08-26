from parseArguments import ConfigParser

def test1():
    c = ConfigParser()
    c.readConfigFile('config.json')
    c.changeSourcePath('/home/dexter','ImageStitch')
    c.changeOutputPath('/home/dexter','ImageStitch')
    c.writeToConfigFile('config2.json')


def test2():
    c = ConfigParser()
    list=['-I','/home/dexter/Pictures/test_download/1','-E','VOCRelease5','-O','/home/dexter/Pictures/test_download']
    c.parseArguments(list)
    c.getParams()






test2()
