import json
import os
import threading
import time
import unittest
import urllib.request as req

from http_server import HTTPServer, HTTPServerHandler

HOST = 'localhost'
PORT = 8080

class HTTPServerTestCase(unittest.TestCase):
    HOST = 'localhost'
    PORT = 8080

    def setUp(self):
        self.host = 'localhost'
        self.port = 8080
        self.tablename = 'log'
        self.filename = 'test.db'
        self.url = f"http://{self.host}:{self.port}/{self.tablename}"
        self.row = {
            'col_int': 1,
            'col_str': 'Hello, World!',
            'col_float': 1.5
        }

        # waiting server to load
        time.sleep(2)
        # todo: http server working from testcase
        # self.server = HTTPServer(
        #     (self.host, self.port),
        #     HTTPServerHandler(filename=self.filename)
        # )


    # def tearDown(self):
    #     os.remove(self.filename)
        
    
    def test_post_get(self):
        # POST
        request = req.Request(
            url=self.url,
            data=bytes(json.dumps(self.row).encode('utf-8')),
            method='POST',
        )
        response = req.urlopen(request)

        # GET
        request = req.Request(
            url=self.url,
            method='GET',
        )
        response = req.urlopen(request)
        raw_data = response.read()
        data = json.loads(raw_data)
        self.assertEqual(data, [list(self.row.values())])
