import tornado
import django

import sys
import os
sys.path.append(os.path.abspath('../menosic/'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'menosic.settings'

django.setup()

import views

app = tornado.web.Application([
    (r'/', views.TestWebSocket),
])

if __name__ == '__main__':
    app.listen(8001)
    tornado.ioloop.IOLoop.instance().start()
