
import os, sys
from CGIHTTPServer import CGIHTTPRequestHandler
import BaseHTTPServer

webdir = 'C:\Users\Varin_S\Projects\search\/test-ui\dist'
port = 8080

os.chdir(webdir)
srvaddr = ("", port)
srvobj = BaseHTTPServer.HTTPServer(srvaddr, CGIHTTPRequestHandler)
srvobj.serve_forever()

