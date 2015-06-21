from pcloudcv import PCloudCV
import signal
import argparse
import os

#------------------------------Initial Setup :- Argument Parser--------------------------
parser = argparse.ArgumentParser()
parser.add_argument("config", type=str, help="Full Path to config file")
parser.add_argument("-I", "--input", type=str, help="Full Path to the Input Folder")
parser.add_argument("-O", "--output", type=str, help="Full Path to the Output Folder")
parser.add_argument("-E", "--executable", type=str, help="Executable Name: \n1.) ImageStitch or \n 2.)VOCRelease5")
parser.add_argument("--nologin", help="Specify this argument to ignore logging in. However some features can be used only when logged in.",
                    action="store_true")
args = parser.parse_args()
#----------------xxx-------------Argument Parser Code Ends---------------------xxx----------------------


def parseCommandLineArgs():
    i = 0
    parsedList = {}
    if args.input:
        parsedList['input'] = args.input
    if args.output:
        parsedList['output'] = args.output
    if args.executable:
        parsedList['exec'] = args.executable
    return parsedList, args.config, not args.nologin

if __name__ == "__main__":
    parsedList, config_file, login_required = parseCommandLineArgs()
    print parsedList
    p = PCloudCV(os.getcwd() + '/' + str(config_file), parsedList, login_required)
    signal.signal(signal.SIGINT, p.signal_handler)

    if login_required:
        p.dropbox_authenticate()

    raw_input()

    p.start()
    signal.pause()
