import threading
import json
import os
import sys
import redis
import requests
import cherrypy
from utility import accounts, conf
from utility.logger import debug, info, warn, error
from mako.template import Template
from mako.lookup import TemplateLookup
import utility.job as job
import utility.conf as conf
import collections

lookup = TemplateLookup(directories=['html'])
redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)

def exit_program():
    """
    An alias for exit system call. 
    """
    sys.exit(0)

class Path:
    @cherrypy.expose
    def __init__(self):
        pass
    @cherrypy.expose
    def index(self):
        return 'hi'

    @cherrypy.expose
    def classify_output(name=None):
        template = Template(filename='html/index.html')
        imagepath = []

        output_dict = json.loads(job.job.output)
        result = []
        for k, v in output_dict.iteritems():
            imagepath.append(os.path.join(conf.BASE_URL+job.job.jobinfo['url'], k))
            scores = output_dict[k]
            result.append(scores)
        return template.render(imagepath=imagepath, result = result)




    @cherrypy.expose
    def dropbox_callback(self, *args, **kwargs):
        """
        A callback handler for Dropbox authentication. It requires a user to be authenticated with A Google account first. The `code` and `state` 
        parameters in the callback are posted to CloudCV API endpoint. 
        """
        state = kwargs['state']
        code = kwargs['code']

        result = requests.post(conf.BASE_URL + '/callback/dropbox/',
                                data={
                                'code': code,
                                'state': state,
                                'userid': accounts.account_obj.getGoogleUserID()
                                })

        try:
            account_info = json.loads(result.text)
        except Exception:
            return result.text

        accounts.account_obj.dbaccount = accounts.DropboxAccounts(str(account_info['uid']), str(account_info['token']))
        info('Dropbox Account:'+str(account_info['uid']))
        info("Dropbox Token:"+str(account_info['token']))

        redis_obj.set('dropbox_token', account_info['token'])
        redis_obj.set('dropbox_account', account_info['uid'])

        accounts.writeAccounts(accounts.account_obj)
        accounts.dropboxAuthentication = True

        http_response = "Your dropbox account is now linked"
        return http_response

    @cherrypy.expose
    def callback(self, *args, **kwargs):
        """
        A callback handler for Google OAuth. It collects the state and code from the callback and posts them to the CloudCV API endpoint for Google callback.
        The response is stored in a local config file to avoid Auth process in future.
        """
        state = kwargs['state']
        code = kwargs['code']

        result = requests.post(conf.BASE_URL + '/callback/google/',
                                data={
                                'code': code,
                                'state': state
                                })
        debug(result.text)
        try:
            account_info = json.loads(result.text)

        except Exception:
            return result.text

        accounts.account_obj = accounts.Accounts()
        accounts.account_obj.gaccount = accounts.GoogleAccounts(str(account_info['id']), str(account_info['email']))
        accounts.writeAccounts(accounts.account_obj)
        accounts.googleAuthentication=True
        http_response = "You have been authenticated to CloudCV using your google account."
        return http_response

    def exit(self):
        """
        Quits the application.
        """

        threading.Timer(1, lambda: os._exit(0)).start()
        return "Local Server Stopped"

def GET(self, name, **params):
    """
    Sends a GET request to the Google callback endpoint of CloudCV API's.
    
    :param name: Specifies a flag for sending a request to Google callback endpoint. 
    :type name: str
    :return: The response of the GET request if name is 'google'.
    """
    info(str(params))

    if name is 'google':
        state = params.get('state')
        code = params.get('code')

        result = requests.post(accounts.BASE_URL + '/callback/google/',
                               data={
                                   'code': code,
                                   'state': state
                               })
        global server
        server.stop()
        return str(result.text)

    return 'not extracted'


class HTTPServer(threading.Thread):
    """
    Instantiates a HTTPserver object with condition variable `sync` that provides synchronization mechanism for multithreading.

    """
    def __init__(self):
        threading.Thread.__init__(self, name="CherryPy")
        self.sync = threading.Condition()

        

    def run(self):
        """
        Checks if port 8000 is free and starts running CherryPy server on the port.
        """
        

        with self.sync:
            try:
                cherrypy.process.servers.check_port('127.0.0.1', 8000)
            except IOError:
                sys.stderr.write("The port %s is not free\n" % 8000)

        
        
        

        cherrypy.server.socket_port = 8000
        config = {'global': {
                                   'log.screen': False,
                                   'log.error_file': '',
                                   'log.access_file': ''
                            }
                 }
        cherrypy.quickstart(Path(),'',config)
        

    def stop(self):
        """
        Stops CherryPy server. 
        """
        cherrypy.engine.exit()
        #cherrypy.server.stop()
        #cherrypy.process.bus.exit()
        debug('Local Server Stopped')

server = HTTPServer()