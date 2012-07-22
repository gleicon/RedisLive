from BaseController import BaseController
import dateutil.parser
import datetime
from twisted.internet import defer


class TopCommandsController(BaseController):
    @defer.inlineCallbacks
    def get(self):
        return_data = dict(data=[],
                           timestamp=datetime.datetime.now().isoformat())

        server = self.get_argument("server")
        from_date = self.get_argument("from", None)
        to_date = self.get_argument("to", None)

        if from_date==None or to_date==None:
            end = datetime.datetime.now()
            delta = datetime.timedelta(seconds=120)
            start = end - delta
        else:
            start = dateutil.parser.parse(from_date)
            end   = dateutil.parser.parse(to_date)
        
        tc = yield self.stats_provider.get_top_commands_stats(server, start, end)

        for data in tc:
            return_data['data'].append([data[0], data[1]])

        self.write(return_data)
