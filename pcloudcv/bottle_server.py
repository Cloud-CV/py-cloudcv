from bottle import route, run, request
import requests
import threading

from accounts import account_obj

class BottleServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    @route('/callback/<name>')
    def hello(name):
        state = request.query.state
        code = request.query.code

        result = requests.post('http://cloudcv.org/cloudcv/callback/google/',
                                data={
                                'code': code,
                                'state': state
                                })
        print str(result.text)
        return str(result.text)

    def run(self):
        run(host='localhost', port=8000, debug=True)