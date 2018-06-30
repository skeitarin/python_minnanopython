# coding: utf-8

import http.server
from http.server import HTTPServer, SimpleHTTPRequestHandler
import cgi
from httphandler import Response

funcs={}
def expose(func, func_name=''):
    if not func_name:
        func_name=func.__name__
    if func_name=='index':
        func_name=''
    funcs.update({func_name:func})
    return func

class SimpleAppServer(http.server.SimpleHTTPRequestHandler):
    static_dirs=['/static']

    def do_GET(self):
        for s_dir in self.static_dirs:
            if self.path.startswith(s_dir):
                http.server.SimpleHTTPRequestHandler.do_GET(self)
                return
        i=self.path.rfind('?')
        if i>=0:
            path, query=self.path[:i], self.path[i+1:]
        else:
            path=self.path
            query=''
        self.handle_query(path, query)

    def do_POST(self):
        length=self.headers.getheader('content-length')
        try:
            nbytes=int(length)
        except (TypeError, ValueError):
            nbytes=0
        data=self.rfile.read(nbytes)
        self.handle_query(self.path, data)
    
    def handle_query(self, path, query):
        args=[]
        path=path[1:]
        if path.find('/') != -1:
            args=path.split('/')[1:]
            path=path.split('/')[0]
        qdict=cgi.parse_qs(query, keep_blank_values=True)
        for k in qdict.keys():
            if isinstance(qdict[k], list) and len(qdict[k]):
                qdict[k]=qdict[k][0]
            else:
                qdict[k]=qdict[k]
        if path in funcs.keys():
            qdict.update({'_request':self})
            resp=funcs[path](*args, **qdict)
            self.send_response(resp.status, resp.status_message)
            self.wfile.write(bytes(resp))
        else:
            self.send_error(404, "No such handler function ({func_name})".format(func_name=path))

"""
for test
"""
def test(HandlerClass = SimpleAppServer,
         ServerClass = HTTPServer):
    http.server.test(HandlerClass, ServerClass)
