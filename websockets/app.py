import tornado
import views


app = tornado.web.Application([
    (r'/', views.WebSocketServer),
])

if __name__ == '__main__':
    app.listen(8001)
    tornado.ioloop.IOLoop.instance().start()
