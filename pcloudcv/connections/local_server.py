import threading
import json
import os
import sys

import requests
import cherrypy
from utility import accounts


def exit_program():
    sys.exit(0)

class Path:
    @cherrypy.expose
    def __init__(self):
        pass
    @cherrypy.expose
    def index(self):
        return 'hi'

    @cherrypy.expose
    def dropbox_callback(self, *args, **kwargs):
        state = kwargs['state']
        code = kwargs['code']

        result = requests.post('http://cloudcv.org/cloudcv/callback/dropbox/',
                                data={
                                'code': code,
                                'state': state,
                                'userid': accounts.account_obj.getGoogleUserID()
                                })
        print result.text

        try:
            account_info = json.loads(result.text)
        except Exception:
            return result.text

        accounts.account_obj.dbaccount = accounts.DropboxAccounts(str(account_info['uid']), str(account_info['token']))
        accounts.writeAccounts(accounts.account_obj)
        accounts.dropboxAuthentication = True
        return result

    @cherrypy.expose
    def callback(self, *args, **kwargs):
        state = kwargs['state']
        code = kwargs['code']

        result = requests.post('http://cloudcv.org/cloudcv/callback/google/',
                                data={
                                'code': code,
                                'state': state
                                })
        print result.text
        try:
            account_info = json.loads(result.text)

        except Exception:
            return result.text

        if 'user_table_message' in account_info and 'gaccount_table_message' in account_info:
            print account_info['user_table_message']
            print account_info['gaccount_table_message']


        accounts.account_obj = accounts.Accounts()
        accounts.account_obj.gaccount = accounts.GoogleAccounts(str(account_info['id']), str(account_info['email']))
        accounts.writeAccounts(accounts.account_obj)
        accounts.googleAuthentication=True
        return result

    def exit(self):
        """
        /exit
        Quits the application
        """

        threading.Timer(1, lambda: os._exit(0)).start()
        return "Local Server Stopped"

def GET(self, name, **params):
    print str(params)

    if name is 'google':
        state = params.get('state')
        code = params.get('code')

        result = requests.post('http://cloudcv.org/cloudcv/callback/google/',
                               data={
                                   'code': code,
                                   'state': state
                               })
        global server
        server.stop()
        return str(result.text)

    return 'not extracted'


class HTTPServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.sync = threading.Condition()

    def run(self):
        with self.sync:
            try:
                cherrypy.process.servers.check_port('127.0.0.1', 8000)
            except IOError:
                sys.stderr.write("The port %s is not free\n" % 8000)


        cherrypy.log.screen = False
        cherrypy.server.socket_port = 8000
        cherrypy.quickstart(Path())

    def stop(self):
        cherrypy.engine.exit()
        cherrypy.server.stop()
        cherrypy.process.bus.exit()
        print 'Local Server Stopped'

server = HTTPServer()