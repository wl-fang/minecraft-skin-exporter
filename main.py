import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import requests
import base64
import json
from PIL import Image
from io import BytesIO

def getPlayerUUID(username: str):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["id"]
    else:
        return None

def getPlayerSkinInfo(uuid: str):
    url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["properties"][0]["value"]
    else:
        return None

def getPlayerSkin(uuid: str):
    base64_encoded_data = getPlayerSkinInfo(uuid)
    if base64_encoded_data:
        # Decode the Base64 string into bytes
        decoded_data = base64.b64decode(base64_encoded_data)

        # Convert the bytes object to a string
        json_data = decoded_data.decode('utf-8')

        # Parse the string into a JSON object
        skin_info = json.loads(json_data)

        # Extract the skin URL
        skin_url = skin_info["textures"]["SKIN"]["url"]
        return skin_url
    else:
        return None

def downloadSkinTexture(skin_url: str):
    response = requests.get(skin_url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        return None

def rgb_to_hex(r, g, b):
    return f"{r:02x}{g:02x}{b:02x}"

def serializeSkinDataTo2DArray(image: Image.Image):
    width, height = image.size
    serialized_data = []

    for x in range(width):
        row = []
        for y in range(height):
            r, g, b, a = image.getpixel((x, y))
            color_hex = rgb_to_hex(r, g, b)
            row.append([color_hex, a])
        serialized_data.append(row)

    return json.dumps(serialized_data)


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if "data" in query_params:
            received_string = query_params["data"][0]  # Get the string from the query
            uuid = getPlayerUUID(received_string)
            skinUrl = getPlayerSkin(uuid)
            
            skin_url = getPlayerSkin(uuid)
            if skin_url:
                image = downloadSkinTexture(skin_url)
                if image:
                    serialized_data = serializeSkinDataTo2DArray(image)

                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(serialized_data.encode())  # Send the string back as response
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(b"Failed to download skin texture")
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Failed to retrieve skin url")
            
        else:
            # Handle case where no "data" parameter is provided
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"No data provided")

httpd = socketserver.TCPServer(("", 8080), MyHandler)
httpd.serve_forever()
