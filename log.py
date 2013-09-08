from colorama import init, Fore

init()

def log(logType,e):
    if(logType=='W'):
        print Fore.RED+str(e)+'\n'
        print Fore.RESET
    if(logType == 'I'):
        print Fore.MAGENTA
        print str(e)+'\n'
        print Fore.RESET
    if(logType == 'D'):
        print Fore.CYAN+str(e)+'\n'
        print Fore.RESET


class ArgumentError(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        if(self.value==0):
            return 'Executable Not found. Possibly a typing error. Should be:\n1.) ImageStitch\n2.) VOCRelease5'
        if(self.value==1):
            return 'Path to the folder containing images is not defined.\n Define it through -I parameter\n'
        if(self.value==2):
            return 'Path to the output folder is not defined.\n Define it through -O parameter\n'



