from socketIO_client import SocketIO
import threading
import redis

socketio = None

class SocketIOConnection(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.ps = self.r.pubsub()
        self.ps.subscribe('intercomm2')
        redisThread = RedisListen(self.ps, self.r)
        redisThread.start()

    
    def run(self):
        print "Starting Socket Connection Thread"
        self.setupSocketIO(self.r)
        print "Exiting Socket Connection Thread"
        

    def connection(self, *args):
        print 'on Connection: ', args
    
    def on_aaa_response(self, *args):
        message = args[0] 
        #print 'on Message', str(message)

        if('socketid' in message):
                self.r.publish('intercomm', message['socketid'])
        if('name' in message):
            self.socketIO.emit('send_message','give output')

        if('data' in message):
            print '\n\n', message['data']
            self.r.publish('intercomm', '***end***')
            

    def setupSocketIO(self, r):
        global socketio

        try:
            self.socketIO = SocketIO('godel.ece.vt.edu', 8000)
            self.socketIO.on('connect', self.connection)

            self.socketIO.on('message', self.on_aaa_response)
            
            socketio=self.socketIO

            self.socketIO.wait()
        except Exception as e:
            print "\n\nConnection Refused, Exiting\n\n"
            print str(e)
            raise SystemExit
            
class RedisListen(threading.Thread):
    def __init__(self, ps, r):
        threading.Thread.__init__(self)
        self.r = r
        self.ps = ps
    def run(self):
    	print 'Listening Listing to Redis Channel'
        while(True):
            shouldEnd = listenToChannel(self.ps, self.r)
            if(shouldEnd):
                break
        print 'Ending Listing to Redis Channel'

def listenToChannel(ps, r):
    global socketio

    for item in ps.listen():
        if item['type'] == 'message':
            if '***endcomplete***' in item['data']:
                socketio.disconnect()
                return True
    return False
   
