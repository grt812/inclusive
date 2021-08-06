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
import random

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

#Read cell data
import csv

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
    # print("yt link: "+songLink)
    # 404 Error here????
    # videoStream = YouTube(songLink).streams
    #
    # #.filter(only_audio=True).order_by("abr").desc().first()
    # print(videoStream)
    #return base64.b64encode(videoStream)

    #Attempting pafy library instead
    #Dislike key error
    audioStream = pafy.new(songLink).getbestaudio()

    # print("Audio Stream URL:",audioStream.url)
    #To-Do: Base 64 audio
    # base64Audio = base64.b64encode(requests.get(audioStream.url).content)
    # print("Stream Base64:",base64Audio)
    # return '{"audio": "'+base64Audio.decode("utf-8")+'", "ext": "'+audioStream.extension+'" ,"img":"'+imageURL+'"}'
    # "ext": "'+audioStream.extension+'" ,
    tempResponse = '{"audio": "'+audioStream.url+'", "img":"'+imageURL+'"}'
    # print("Temp Response: "+tempResponse)
    return tempResponse

#Returns a list of songs that are similar to one song
#To-Do for Ethan (ANNOY)
#Column Constants
ID = 0
NAME = 1
# POPULARITY = 2
# EXPLICIT = 4
# ARTISTS = 5
# ID_ARTISTS = 6
# RELEASE = 7
DURATION = 3
ACOUSTICNESS = 8
ENERGY = 9
KEY = 10
LOUDNESS = 11
MODE = 12
SPEECHINESS = 13
ACOUSTICNESS = 14
INSTRUMENTALNESS = 15
LIVENESS = 16
VALENCE = 17
TEMPO = 18
TIME_SIGNATURE = 19

DURATION_WEIGHT = 0.01 * 0.001
ACOUSTICNESS_WEIGHT = 0.1
ENERGY_WEIGHT = 0.1
KEY_WEIGHT = 0.05
LOUDNESS_WEIGHT = 0.1
MODE_WEIGHT = 0.1
SPEECHINESS_WEIGHT = 0.1
ACOUSTICNESS_WEIGHT = 0.1
INSTRUMENTALNESS_WEIGHT = 0.1
LIVENESS_WEIGHT = 0.02
VALENCE_WEIGHT = 0.1
TEMPO_WEIGHT = 0.01
TIME_SIGNATURE_WEIGHT= 0.1

SAMPLE_SIZE = 1000

@app.route('/recommend', methods=['GET'])
def recommend():
    #request.args["id"] for spotify api
    #request.args["limit"]
    #request.args["repeats"] -optional for continuing queue
    #Thanks to https://stackoverflow.com/questions/17444679/reading-a-huge-csv-file

    #Get Song ID
    authToken = requestAuthorization()
    startAnalysis = requests.get("https://api.spotify.com/v1/audio-features/"+request.args["id"], headers = {"Authorization":"Bearer "+authToken})

    startDictionary = json.loads(startAnalysis.text);
    # print()

    print("Generating sample...")

    #Select 100 Random indecies according to file size
    songList = []
    dataSize = 0
    with open("tracks.csv", "rb") as csvfile:
        trackReader = csv.reader(csvfile)
        dataSize = sum(1 for row in csvfile)
        sampleList = random.sample(range(dataSize), 1000)
        print("Data Size:",dataSize)

    #Add rows matching random indcies to list
    with open("tracks.csv", "rb") as csvfile:
        # , delimiter=",", quoting=csv.QUOTE_NONE, escapechar="\\"
        trackReader = csv.reader(csvfile)
        index = 0
        for row in csvfile:
            index += 1
            # print("index:", index)
            if index in sampleList:
                songList.append(row)

    # for song in songList:
    #     print("Song: "+song.decode("utf-8"))

    # print("Song List: ",",".join(songList))
    #Run Algorithm
    scoreList = []
    # responseSongList
    tempIndex = 0
    for song in songList:
        decodedSong = song.decode("utf-8");
        # print("Song: "+decodedSong)

        #Substring to find list of artists
        # songArtistsString = decodedSong[decodedSong.index("["):decodedSong.index("]")+1]
        # subSongArtistString = decodedSong[decodedSong.index("[")+1:decodedSong.index("]")]
        # songArtists = subSongArtistString.split(",")
        # decodedSong = decodedSong.replace(songArtistsString, "artists")

        #Substring to find list of artist ids
        # songArtistIDsString = decodedSong[decodedSong.index("["):decodedSong.index("]") + 1]
        # subSongArtistIDsString = decodedSong[decodedSong.index("[") + 1:decodedSong.index("]")]
        # songArtistIDs = subSongArtistIDsString.split(",")
        # decodedSong = decodedSong.replace(songArtistIDsString, "artist ids")

        #Escape all commas in strings
        tempDecodedSong = decodedSong
        while tempDecodedSong.find("\"") != -1:
            # print("Temp Decoded Song Before: "+tempDecodedSong)
            #Find first quote and substring to it
            firstQuoteIndex = tempDecodedSong.find('"')
            tempSub = tempDecodedSong[firstQuoteIndex:]
            # print("Temp Sub: "+tempSub)
            #Find second quote and close the substring
            secondQuoteIndex = tempSub[1:].find('"')+1
            tempQuotes = tempSub[:secondQuoteIndex+1]
            # print("Temp Quotes: "+tempQuotes)
            #Escape commas within quotes
            tempNoComma = tempQuotes.replace(",", "{{comma}}")
            # print("Escaped Version:" + tempNoComma)
            #Replace quotes with comma escaped quotes
            decodedSong = decodedSong.replace(tempQuotes, tempNoComma)
            # print("Escaped Song WIP: "+decodedSong)
            # print("Temp Quotes Index: "+str(tempDecodedSong.find(tempQuotes)))
            # print("Cropping string at: "+str(tempDecodedSong.find(tempQuotes)+len(tempQuotes)+2))
            #Replace non escaped commas in quotes with escaped commas in quotes
            # tempDecodedSong.find(tempQuotes)+len(tempQuotes)+q
            tempDecodedSong = tempDecodedSong[firstQuoteIndex+secondQuoteIndex+1:]
            # print("Temp Decoded Song After: "+tempDecodedSong)

        # print("Escaped Song: "+decodedSong)
        # for cell in song:
        #     decodedSong.append(cell.decode("utf-8"))
        #     print(cell.decode("utf-8"))
        decodedSong = decodedSong.split(",")
        decodedSong = [item.replace("{{comma}}", ",") for item in decodedSong]
        # for i, cell in enumerate(decodedSong):
        #     print("Cell "+str(i)+":",cell)

        attributeList = []
        # Convert ms to s
        # print("STARTING DURATION: "+str(startDictionary["duration_ms"]))
        # print("DURATION: "+str(decodedSong[DURATION]))
        attributeList.append(abs(float(decodedSong[DURATION]) - startDictionary["duration_ms"]) * DURATION_WEIGHT)
        attributeList.append(abs(float(decodedSong[ACOUSTICNESS]) - startDictionary["danceability"]) * ACOUSTICNESS_WEIGHT)
        attributeList.append(abs(float(decodedSong[ENERGY]) - startDictionary["energy"]) * ENERGY_WEIGHT)
        attributeList.append(abs(float(decodedSong[KEY]) - startDictionary["key"]) * KEY_WEIGHT)
        attributeList.append(abs(float(decodedSong[LOUDNESS]) - startDictionary["loudness"]) * LOUDNESS_WEIGHT)
        attributeList.append(abs(float(decodedSong[MODE]) - startDictionary["mode"]) * MODE_WEIGHT)
        attributeList.append(abs(float(decodedSong[SPEECHINESS]) - startDictionary["speechiness"]) * SPEECHINESS_WEIGHT)
        attributeList.append(abs(float(decodedSong[ACOUSTICNESS]) - startDictionary["acousticness"]) * ACOUSTICNESS_WEIGHT)
        attributeList.append(abs(float(decodedSong[INSTRUMENTALNESS]) - startDictionary["instrumentalness"]) * INSTRUMENTALNESS_WEIGHT)
        attributeList.append(abs(float(decodedSong[LIVENESS]) - startDictionary["liveness"]) * LIVENESS_WEIGHT)
        attributeList.append(abs(float(decodedSong[VALENCE]) - startDictionary["valence"]) * VALENCE_WEIGHT)
        attributeList.append(abs(float(decodedSong[TEMPO]) - startDictionary["tempo"]) * TEMPO_WEIGHT)
        attributeList.append(abs(float(decodedSong[TIME_SIGNATURE]) - startDictionary["time_signature"]) * TIME_SIGNATURE_WEIGHT)

        # print("\nSong Index:"+str(tempIndex))
        # for attribute in attributeList:
        #     print(" Attributes:"+str(attribute)+", ")
        # attributeList.append(abs(song[DANCEABILITY] - startDictionary["danceability"]) * DANCEABILITY_WEIGHT)
        # print("Starting duration: "+str(startDictionary["duration_ms"]))
        # print("Song duration: "+str(song[DURATION]))
        score = sum(attributeList)/len(attributeList)
        scoreList.append({"score":score, "index":tempIndex, "id":decodedSong[ID]})
        # print("Score: "+str(score))
        tempIndex += 1

    # for i in scoreList:
    #     print(i["id"])

    #Sort scores from lowest to highest
    sortedScoreList = sorted(scoreList, key=lambda k: k["score"])

    #Limit results
    sortedScoreList = sortedScoreList[:int(request.args["limit"])]
    #Request songs for thumbnails:
    print("Songs Request URL: "+"https://api.spotify.com/v1/tracks?ids="+",".join(str(i["id"]) for i in sortedScoreList))
    tracksResponse = requests.get("https://api.spotify.com/v1/tracks?ids="+",".join(str(i["id"]) for i in sortedScoreList), headers = {"Authorization":"Bearer "+authToken})
    # print(tracksResponse.text)
    for index, track in enumerate(json.loads(tracksResponse.text)["tracks"]):
        sortedScoreList[index]["img"] = track["album"]["images"][0]["url"];
        sortedScoreList[index]["name"] = track["name"];
        sortedScoreList[index]["artists"] = ", ".join((artist["name"] for artist in track["artists"]));



    for score in sortedScoreList:
        print("Song: "+str(score["name"])+", Artists: "+str(score["artists"])+", Score: "+str(score["score"]))

    return ",".join(json.dumps(i) for i in sortedScoreList)

# def getStuff(filename, criterion):


def generateSample():
    pass
        # for i in sampleList:
        #     print(str(i))
        # print(*lst, sep = "\n")
        # print(str(sampleList))
        #Is this really necessary?
        #     try:
        #         yield row
        #     except StopIteration:
        #         return
        # try:
        #     headerRow = next(trackReader)
        # except StopIteration:
        #     return

#Static Hosting
@app.route('/')
def index():
    return app.send_static_file('index.html')



# @app.route('/')
# def index():
#     return render_template('../client/index.html')

if __name__ == '__main__':
    app.run(debug=True)
