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

#YouTube Search and Download
from youtubesearchpython import VideosSearch
from pytube import YouTube
import pafy
import urllib

app = Flask(__name__, static_url_path='', static_folder='')
# api = Api(app)

#Authorize Spotify
def requestAuthorization():
    clientAndSecret = base64.b64encode((keys.spotifyClient+":"+keys.spotifySecret).encode('ascii')).decode('ascii')
    # print("Authorization Header: "+"Basic "+clientAndSecret)
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
        #TO-Do: Add function for replacing apostraphes and double quotes
        for item in searchDictionary["tracks"]["items"]:
            artistList = [i["name"].replace("'", "{{apostrophe}}").replace('"', "{{double}}") for i in item["artists"]]
            modifiedItem = {"name":item["name"].replace("'", "{{apostrophe}}").replace('"', "{{double}}"), "image": item["album"]["images"][2]["url"].replace("'", "{{apostrophe}}").replace('"', "{{double}}"), "artists": artistList, "id": item["id"]}
            finalResult.append(modifiedItem)

        finalResult = ",".join([str(i) for i in finalResult])
        # print("Joined version:",finalResult)
        # finalResult = json.dumps(finalResult)
        # print("Double Quotes:",finalResult)
        finalResult = "[" + finalResult + "]"
        # print("Array version:",finalResult)
    # print(finalResult)

    return finalResult


#Handle song request
@app.route('/song', methods=['GET'])
def song():
    #request.args["name"]
    #request.args["artists"]
    #request.args["id"] (for image)
    # print("requesting song: "+request.args["name"])
    # print("artists: "+request.args["artists"])

    #Get High Res Image
    authToken = requestAuthorization()
    searchResults = requests.get("https://api.spotify.com/v1/tracks/"+request.args["id"], headers = {"Authorization":"Bearer "+authToken})
    imageURL = json.loads(searchResults.text)["album"]["images"][1]["url"];

    songSearch = VideosSearch(request.args["name"] + " "+request.args["artists"].replace(",", " "), limit = 1)
    # print("songLink: "+str(songSearch.result()))
    songLink = songSearch.result()["result"][0]["link"]
    print("yt link: "+songLink)
    # 404 Error here????
    # videoStream = YouTube(songLink).streams
    #
    # #.filter(only_audio=True).order_by("abr").desc().first()
    # print(videoStream)
    #return base64.b64encode(videoStream)

    #Attempting pafy library instead
    audioStream = pafy.new(songLink).getbestaudio()

    print("Audio Stream URL:",audioStream.url)
    #Base 64 unnecessary?
    # base64Audio = base64.b64encode(requests.get(audioStream.url).content)
    # print("Stream Base64:",base64Audio)
    # return '{"audio": "'+base64Audio.decode("utf-8")+'", "ext": "'+audioStream.extension+'" ,"img":"'+imageURL+'"}'
    # "ext": "'+audioStream.extension+'" ,
    tempResponse = '{"audio": "'+audioStream.url+'", "img":"'+imageURL+'"}'
    print("Temp Response: "+tempResponse)
    return tempResponse

#Returns a list of songs that are similar to one song
#To-Do for Ethan
@app.route('/recommend', methods=['GET'])
def recommend():
    #request.args["id"] for spotify api
    #request.args["limit"]
    #request.args["repeats"] -optional for continuing queue
    return "Response"

#Static Hosting
@app.route('/')
def index():
    return app.send_static_file('index.html')



# @app.route('/')
# def index():
#     return render_template('../client/index.html')

if __name__ == '__main__':
    app.run(debug=True)
