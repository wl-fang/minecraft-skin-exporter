import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import requests
import base64

def some_function():
    print("some_function got called")

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if "data" in query_params:
            received_string = query_params["data"][0]  # Get the string from the query
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(received_string.encode())  # Send the string back as response
        else:
            # Handle case where no "data" parameter is provided
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"No data provided")

httpd = socketserver.TCPServer(("", 8080), MyHandler)
httpd.serve_forever()