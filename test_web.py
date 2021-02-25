#!/usr/bin/env python

import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('login.html')

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([(r"/login",LoginHandler)],
      template_path = os.path.join(os.path.dirname(__file__),"templates"),
      static_path =os.path.join(os.path.dirname(__file__), "static"),
      debug = True				                       
          )   
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
