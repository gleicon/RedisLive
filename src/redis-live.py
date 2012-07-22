#! /usr/bin/env python

from twisted.internet import reactor
import cyclone.options
import cyclone.web

from api.controller.BaseStaticFileHandler import BaseStaticFileHandler

from api.controller.ServerListController import ServerListController
from api.controller.InfoController import InfoController
from api.controller.MemoryController import MemoryController
from api.controller.CommandsController import CommandsController
from api.controller.TopCommandsController import TopCommandsController
from api.controller.TopKeysController import TopKeysController


# Bootup
application = cyclone.web.Application([
  (r"/api/servers", ServerListController),
  (r"/api/info", InfoController),
  (r"/api/memory", MemoryController),
  (r"/api/commands", CommandsController),
  (r"/api/topcommands", TopCommandsController),
  (r"/api/topkeys", TopKeysController),
  (r"/(.*)", BaseStaticFileHandler, {"path": "www"})
], debug="True")


if __name__ == "__main__":
  cyclone.options.parse_command_line()
  reactor.listenTCP(8888, application, interface="127.0.0.1")                 
  reactor.run()
