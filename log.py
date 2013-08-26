from colorama import init, Fore

init()

def log(logType,e):
    if(logType=='W'):
        print Fore.RED+str(e)+'\n\n'
        print Fore.RESET
    if(logType == 'I'):
        print str(e)+'\n\n'


class ExecutableError(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        if(self.value==0):
            return 'Executable Not found. Possibly a typing error. Should be:\n1.) ImageStitch\n2.) VOCRelease5'



