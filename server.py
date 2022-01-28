#  coding: utf-8 
from posixpath import abspath
import socketserver
from urllib import response
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))

        req = self.data.split()[0].decode()
        uri = self.data.split()[1].decode()

        if (req!= 'GET'):
            self.method_not_allowed_405()

        else:
            self.response(uri)
        


    def response(self, uri):

        path = self.append_path(uri)
        mime_type = self.get_mime_type(uri)
        directory = os.path.abspath('www')

        if path.startswith(directory) == False:
            self.not_found_404() 
        elif os.path.exists(path) == False:
            self.not_found_404()
        elif os.path.isdir(path):
            self.redirect_301(path,uri)
        try:
            file = open(path, "r")
            content = file.read()
            self.ok_200(content, mime_type)
        except IOError:
            self.not_found_404()


        
    def ok_200(self,content, mime_type):
        date = self.get_time_formated()
        http_status = "HTTP/1.1 200 OK" 
        response = http_status + "\r\n" + \
                "Server: " + "Nick's Server" + "\r\n" + \
                "Date: " + str(date) + "\r\n" + \
                "Content-type: text/" + mime_type + "; charset=UTF-8" + "\r\n" \
                "Content-length: " + str(len(content)) + "\r\n\r\n" + \
                content + "\r\n"
        
        self.request.sendall(response.encode())



    #I kind of hardcoded this
    def redirect_301(self,path, uri):

        if uri[-1] == '/':
            path = path + "/index.html"
            try:
                mime_type = self.get_mime_type(uri)
                file = open(path, "r")
                content = file.read()
                self.ok_200(content, mime_type)
            except IOError:
                self.not_found_404()
        else:
            date = self.get_time_formated()
            http_status = "HTTP/1.1 301 Moved Permanently"
            location = "Location: http://127.0.0.1:8080/deep/"
            mime_type = 'html'

            content = "<HTML><HEAD>\r\n" + \
                      "<TITLE>301 Moved</TITLE></HEAD><BODY>\r\n" + \
                      "<H1>301 Moved</H1>\r\n" + \
                      "Redirect: \r\n" + \
                      "<A HREF=" + "/deep/>here</A>.\r\n" + \
                      "</BODY></HTML>"

            response = http_status + "\r\n" + \
                    location + "\r\n" + \
                    "Server: " + "Nick's Server" + "\r\n" + \
                    "Date: " + str(date) + "\r\n" + \
                    "Content-type: text/" + mime_type + "; charset=UTF-8" + "\r\n" \
                    "Content-length: " + str(len(content)) + "\r\n\r\n" + \
                    content + "\r\n"

            self.request.sendall(response.encode())
    


    def not_found_404(self):
        date = self.get_time_formated()
        http_status = "HTTP/1.1 404 Not Found"
        mime_type = "html"
        contents = "<html><head>\r\n" + \
                    "<title>404 Not Found</title>\r\n" + \
                    "</head><body>\r\n" + \
                    "<h2>Sorry, we cant find that page</h2>\r\n" + \
                    "<h3>Error code: 404</h3>\r\n" + \
                    "</body></html>"
        response = http_status + "\r\n" + \
                    "Server: " + "Nick's Server" + "\r\n" + \
                    "Date: " + str(date) + "\r\n" + \
                    "Content-type: text/" + mime_type + "; charset=UTF-8" + "\r\n" + \
                    "Content-length: " + str(len(contents)) + "\r\n\r\n" + \
                    contents + "\r\n"

        self.request.sendall(response.encode())



    def method_not_allowed_405(self):
        date = self.get_time_formated()
        http_status = "HTTP/1.1 405 Method Not Allowed"
        mime_type = 'html'
        contents = "<html><head>\r\n" + \
                        "<title>405 Method Not Allowed</title>\r\n" + \
                        "<h2>Sorry, that is not allowed.</h2>\r\n" + \
                        "<h3>Error code: 405</h3>\r\n" + \
                        "</body></html>"
        response = http_status + "\r\n" + \
                    "Server: " + "Nick's Server" + "\r\n" + \
                    "Date: " + str(date) + "\r\n" + \
                    "Content-type: text/" + mime_type + "; charset=UTF-8" + "\r\n" + \
                    "Content-length: " + str(len(contents)) + "\r\n\r\n" + \
                    contents + "\r\n"

        self.request.sendall(response.encode())



    def get_mime_type(self, uri):
        
        uri_type = uri.split(".")[-1]
        mime_type = 'html'

        if (uri_type == 'css'):
            mime_type = 'css'
        
        return mime_type


    def append_path(self, uri):
        file = os.path.abspath('www'+uri)
        return file

    def get_time_formated(self):
        now = datetime.now()
        stamp = mktime(now.timetuple())
        date = format_date_time(stamp)

        return date

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

