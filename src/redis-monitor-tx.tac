#! /usr/bin/env python

# twistd -ny redis-monitor-tx.tac

from api.util import settings
from dataprovider.dataprovider import RedisLiveDataProvider

import datetime, time

from twisted.internet import reactor                                                                                
from twisted.application import internet, service
from twisted.internet import defer
from cyclone import redis as txredisapi
from twisted.python import log

                                                                                
class DefaultMonitor(txredisapi.MonitorProtocol):                                  
    def connectionMade(self):                                                   
        log.msg("Monitoring server: %s" % self.transport.getPeer())
        self.monitor() # start monitoring
                                                                                
    def messageReceived(self, message):
        self._parse(message)                                        
                                                                                
    def connectionLost(self, reason):                                           
        print "lost connection:", reason                                        
    
    @defer.inlineCallbacks
    def _parse(self, message):

        parts = message.split(" ")

        if len(parts) > 1: 

            epoch = float(parts[0].strip())
            timestamp = datetime.datetime.fromtimestamp(epoch)

            # Strip '(db N)' and '[N x.x.x.x:xx]' out of the monitor str
            if (parts[1] == "(db") or (parts[1][0] == "["): parts = [parts[0]] + parts[3:]

            command = parts[1].replace('"', '').upper()

            if len(parts) > 2: keyname = parts[2].replace('"', '').strip()
            else: keyname = None

            if len(parts) > 3:
                # TODO: This is probably more efficient as a list
                # comprehension wrapped in " ".join()
                arguments = ""
                for x in xrange(3, len(parts)):
                    arguments += " " + parts[x].replace('"', '')
                arguments = arguments.strip()
            else:
                arguments = None
            h = self.transport.getPeer()
            server_id = h.host + ":" + str(h.port)
            if not command == 'INFO' and not command == 'MONITOR':
                yield self.factory.stats_provider.save_monitor_command(server_id, 
                                                    timestamp, 
                                                    command, 
                                                    str(keyname), 
                                                    str(arguments))
                                                                                
class MonitorFactory(txredisapi.MonitorFactory):                                     
    maxDelay = 120                                                              
    continueTrying = True                                                       
    protocol = DefaultMonitor                                                        
    stats_provider = RedisLiveDataProvider.get_provider("txredis") 



### info

def dictit(wot):
    l = wot.split('\n')
    return dict(map(lambda x: tuple(x.split(':')), l[:-1]))


@defer.inlineCallbacks
def info_task(server, port, password=None):
    """Does all the work.
    """
    stats_provider = RedisLiveDataProvider.get_provider("txredis")
    redis_client = yield txredisapi.Connection(server, port, 0)
    server_id = server + ":" + str(port)


    while True:
        ri = yield redis_client.info()
        redis_info = dictit(ri)
        current_time = datetime.datetime.now()
        used_memory = int(redis_info['used_memory'])

        # used_memory_peak not available in older versions of redis
        try:
            peak_memory = int(redis_info['used_memory_peak'])
        except:
            peak_memory = used_memory

        yield stats_provider.save_memory_info(server_id, current_time, 
                                        used_memory, peak_memory)
        yield stats_provider.save_info_command(server_id, current_time, 
                                         redis_info)

        time.sleep(1)

     

 
application = service.Application("redis-monitor-tx")

# redis_servers = settings.get_redis_servers()
# for redis_server in redis_servers:
#     server = redis_server["server"]
#     port = redis_server["port"]
#     pw = redis_server.get("password", None)

#     #TODO pw
#     # setup info
#     reactor.callLater(1, info_task, server, port, pw)
#     # setup monitor     
#     srv = internet.TCPClient(server, port, MonitorFactory)
#     print srv
#     srv.setServiceParent(application)

reactor.callLater(1, info_task, '127.0.0.1', 6379, None)
srv = internet.TCPClient('127.0.0.1', 6379, MonitorFactory())
srv.setServiceParent(application)

    #reactor.run()



    