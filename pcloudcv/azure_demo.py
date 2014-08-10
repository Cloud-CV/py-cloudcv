__author__ = 'dexter'

from pcloudcv import PCloudCV
import signal
import argparse
import os

if __name__ == "__main__":
    parsedList, config_file, login_required = parseCommandLineArgs()
    print parsedList
    p = PCloudCV(os.getcwd() + '/' + str(config_file), parsedList, login_required)
    if login_required:
        p.dropbox_authenticate()
    raw_input()
    p.azure_demo('h.agrawal092@gmail.com', '/classify_azure/')