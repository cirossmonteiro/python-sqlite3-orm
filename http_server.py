
from collections import OrderedDict
import http
import http.server as hs
import json
import logging
import os
import threading as th
import urllib.parse as up
from typing import Union
from enum import Enum
from schema import Schema

import sql

HOST = 'localhost'
PORT = 8080

class BaseHTTPRequestHandler(hs.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        def callback(data):
            raw_data = bytes(json.dumps(data).encode('utf-8'))
            self.send_response(http.HTTPStatus.OK)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(raw_data)

        self.get(self.path, callback)
    
    def do_POST(self):
        raw_data = self.rfile.peek()
        data = json.loads(raw_data)

        self.post(self.path, data)

        self.send_response(http.HTTPStatus.OK)
        self.end_headers()

class HTTPServerHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.filename = kwargs.pop('filename', 'test.db')
        self.db = sql.SQLDatabase(self.filename)
        super().__init__(*args, **kwargs)
        print("HTTP SERVER'S STARTED SERVING...")

    def exit(self):
        os.remove(self.filename)

    def post(self, path, data):
        """
        POST /
        """
        tablename = path[1:]
        try:
            table = self.db[tablename]
        except RuntimeError:
            table = None
        if table is None:
            schema = Schema(mode='row', schema=data)
            self.db[tablename] = schema

        self.db[tablename].insert_into([data])

    def get(self, path, callback):
        """
        GET /
        """
        tablename = path[1:]
        data = self.db[tablename].select()
        callback(data)
        

class HTTPServer(hs.ThreadingHTTPServer):
    pass


if __name__ == "__main__":
    httpd = HTTPServer((HOST, PORT), HTTPServerHandler)
    httpd.serve_forever()