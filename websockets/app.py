import tornado
import sys
import os

import views


app = tornado.web.Application([
    (r'/', views.TestWebSocket),
])

if __name__ == '__main__':
    app.listen(8001)
    tornado.ioloop.IOLoop.instance().start()
