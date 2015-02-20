import threading
import json
import os
import sys

import requests
import cherrypy
from utility import accounts, conf
from mako.template import Template
from mako.lookup import TemplateLookup
import utility.job as job
import utility.conf as conf
import collections

lookup = TemplateLookup(directories=['html'])

"""
class MakoHandler(cherrypy.dispatch.LateParamPageHandler):


    def __init__(self, template, next_handler):
        self.template = template
        self.next_handler = next_handler

    def __call__(self):
        env = globals().copy()
        env.update(self.next_handler())
        try:
            return self.template.render(**env)
        except:
            # something went wrong rendering the template
            # this will generate a pretty error page with details
            cherrypy.response.status = "500"
            return cherrypy.exceptions.html_error_template().render()


class MakoLoader(object):

    def __init__(self):
        self.lookups = {}

    def __call__(self, filename, directories, module_directory=None,
                 collection_size=-1):
        # Find the appropriate template lookup.
        key = (tuple(directories), module_directory)
        try:
            lookup = self.lookups[key]
        except KeyError:
            lookup = TemplateLookup(directories=directories,
                                    module_directory=module_directory,
                                    collection_size=collection_size,
                                    )
            self.lookups[key] = lookup
        cherrypy.request.lookup = lookup

        # Replace the current handler.
        cherrypy.request.template = t = lookup.get_template(filename)
        cherrypy.request.handler = MakoHandler(t, cherrypy.request.handler)

main = MakoLoader()
cherrypy.tools.mako = cherrypy.Tool('on_start_resource', main)
cherrypy.tools.mako.collection_size = 500
cherrypy.tools.mako.directories = 'html'
"""

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
    def classify_output(name=None):
        template = Template(filename='html/index.html')
        imagepath = []

        output_dict = json.loads(job.job.output)
        result = []
        for k, v in output_dict.iteritems():
            imagepath.append(os.path.join(conf.BASE_URL+job.job.jobinfo['url'], k))
            scores = output_dict[k]
            sorted_scores = collections.OrderedDict(sorted(scores.items(), key=lambda t: t[1]))
            result.append(sorted_scores.items())

        return template.render(imagepath=imagepath, result = result)




    @cherrypy.expose
    def dropbox_callback(self, *args, **kwargs):
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
        accounts.writeAccounts(accounts.account_obj)
        accounts.dropboxAuthentication = True

        http_response = "Your dropbox account is now linked"
        return http_response

    @cherrypy.expose
    def callback(self, *args, **kwargs):
        state = kwargs['state']
        code = kwargs['code']

        result = requests.post(conf.BASE_URL + '/callback/google/',
                                data={
                                'code': code,
                                'state': state
                                })
        print result.text
        try:
            account_info = json.loads(result.text)

        except Exception:
            return result.text

        accounts.account_obj = accounts.Accounts()
        accounts.account_obj.gaccount = accounts.GoogleAccounts(str(account_info['id']), str(account_info['email']))
        accounts.writeAccounts(accounts.account_obj)
        accounts.googleAuthentication=True
        http_response = "You have been authenticated to CloudCV using your google account"
        return http_response

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
    def __init__(self):
        threading.Thread.__init__(self)
        self.sync = threading.Condition()

    def run(self):
        with self.sync:
            try:
                cherrypy.process.servers.check_port('127.0.0.1', 8000)
            except IOError:
                sys.stderr.write("The port %s is not free\n" % 8000)


        cherrypy.config.update({'log.screen': False,
                        'log.error_file': None,
                        #'log.error_log': None
                        })

        cherrypy.server.socket_port = 8000
        cherrypy.quickstart(Path())

    def stop(self):
        cherrypy.engine.exit()
        #cherrypy.server.stop()
        #cherrypy.process.bus.exit()
        print 'Local Server Stopped'

        #pass
server = HTTPServer()