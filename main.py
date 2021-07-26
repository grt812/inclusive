#thanks to https://towardsdatascience.com/3-lines-of-python-code-to-write-a-web-server-46a109666dbf for server code

# import os
# from http.server import HTTPServer, CGIHTTPRequestHandler
# # Make sure the server is created at current directory
# os.chdir('../client')
# # Create server object listening the port 80
# server_object = HTTPServer(server_address=('', 80), RequestHandlerClass=CGIHTTPRequestHandler)
# # Start the web server
# server_object.serve_forever()

# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
#
# birdy_uri = 'spotify:artist:2WX2uTcsvV5OnS0inACecP'
# spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
#
# results = spotify.artist_albums(birdy_uri, album_type='album')
# albums = results['items']
# while results['next']:
#     results = spotify.next(results)
#     albums.extend(results['items'])
#
# for album in albums:
#     print(album['name'])

import os
import json
import requests
import keys
import base64
import re

#Flask Webserver API
from flask import Flask
from flask import render_template
from flask import request
# from flask_restful import Resource, Api

app = Flask(__name__, static_url_path='', static_folder='')
# api = Api(app)

#Authorize Spotify
def requestAuthorization():
    clientAndSecret = base64.b64encode((keys.spotifyClient+":"+keys.spotifySecret).encode('ascii')).decode('ascii')
    print("Authorization Header: "+"Basic "+clientAndSecret)
    authorization = requests.post('https://accounts.spotify.com/api/token', headers = {"Authorization": "Basic "+clientAndSecret}, data = {"grant_type": "client_credentials"})
    accessToken = json.loads(authorization.text)["access_token"]
    return accessToken

#Handle search request
@app.route('/search', methods=['GET'])
def search():
    finalResult = []
    if request.args["q"].strip != "":
        authToken = requestAuthorization()
        searchResults = requests.get('https://api.spotify.com/v1/search?q='+request.args["q"]+"&type=track", headers = {"Authorization":"Bearer "+authToken})
        searchDictionary = json.loads(searchResults.text);

        #Format relevant data
        # finalResult = []
        for item in searchDictionary["tracks"]["items"]:
            artistList = [i["name"].replace("'", "{{apostrophe}}").replace('"', "{{double}}") for i in item["artists"]]
            modifiedItem = {"name":item["name"].replace("'", "{{apostrophe}}").replace('"', "{{double}}"), "image": item["album"]["images"][2]["url"].replace("'", "{{apostrophe}}").replace('"', "{{double}}"), "artists": artistList}
            finalResult.append(modifiedItem)

        finalResult = ",".join([str(i) for i in finalResult])
        print("Joined version:",finalResult)
        # finalResult = json.dumps(finalResult)
        # print("Double Quotes:",finalResult)
        finalResult = "[" + finalResult + "]"
        print("Array version:",finalResult)
    # print(finalResult)

    return finalResult


#Handle song request
@app.route('/song', methods=['GET'])
def song():
    return None

#Static Hosting
@app.route('/')
def index():
    return app.send_static_file('index.html')



# @app.route('/')
# def index():
#     return render_template('../client/index.html')

if __name__ == '__main__':
    app.run(debug=True)
