import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import urllib.parse
import datetime


ALL_TRACKS={}
SPOTIFY_API_BASE64_CLIENT='YmUxNDAwYWY1ZjRiNGFiMzk3MWNhODk0OTg3ZDczZjU6Mzc3ZDQ3M2UwNDE1NDI0YWE3ZDFhZDc0ZWUyYjExODE'
userID= "streetsmatter"
name = "New Albums Suggested by Pitchfork"
description= "New Albums taken from Pitchforks website recomendations"
access_token = "BQCiZyQ8dCJ7SF7XZXMSLK4FyR-bQrFDXZyPSyV5gczsqPNMvBOoNWcyXAVG4R8jU7cgLJatfdDyjeDY2C7IR4a_UUxzSL8U3hoYv1FpbHszQMBQYulpTOnf-Vv6AJleYR1uDp7KdS4d2pF4B04dWCHs-esf4MZlI3OYWtY15JxRjPtzJNCTjw"
SPOTIFY_API_CREATE_PLAYLIST =  f"https://api.spotify.com/v1/users/{userID}/playlists"
#SPOTIFY_API_PLAYLIST_TRACKS=f"https://api.spotify.com/v1/playlists/{playlistId}/tracks"
SPOTIFY_API_REFRESH_TOKEN= 'AQCShXSEipWsDzd_WAIKaKrEM5OYkGKJYp2WgwJp8O8aKsxTTaDUAHwJuvkiaPDvj-dmgPjj3XvVvm3z_Aeg44cZLeWQ7_jFxZx7DNOXlg6m0W9TF_QClaz0jrFT7MS4ZCw'
#SPOTIFY_GET_ALBUMS_TRACKS=f"https://api.spotify.com/v1/albums/{albumId}/tracks"
SPOTIFY_API_TOKEN = f'https://accounts.spotify.com/api/token'
#SPOTIFY_API_SEARCH_ARTIST = f'https://api.spotify.com/v1/search/{album}'
uris =[]




class Album():
    def __init__(self,name,artist):
        self.name=name
        self.artist=artist

def getAlbums():
    try:
        print("Parsing Album of the year.")

        # use the BeautifulSoup constructor to pass in the location of the html file, features tells the library the format of the html, and is set to the default html5lib.

        try:
            hnhhRequest = requests.get('https://pitchfork.com/reviews/best/albums/?page=1')
            hTML_FILE = hnhhRequest.text
        except:
            print('error getting top 100 list html')

        soup_parse = BeautifulSoup(hTML_FILE,'html.parser')

        # find all span elements with the name 'chart-element__information

        spans = soup_parse.find_all('div', {'class':'review'})


        if(len(spans) > 0):
            print('h')
            # iterate over the span elements extracting the track and artist names
            for h in spans:
                # extract the track name, and artist name
                album = Album(h.find('h2', {'class':'review__title-album'}).text,h.find('ul', {'class':'artist-list review__title-artist'}).text)
                #album = Album(h.find('ul', {'class':'artist-list review__title-artist'}).text,h.find('h2', {'class':'review__title-album'}).text)             
                # save track info in a dictionary
                ALL_TRACKS[album.name] = album.artist
    except:
        print("Parsing of html page failed.")
        raise


def addAlbumsPlaylist(playlistsId,albumUids,access_token):

    headers={"Accept" : "application/json", "Content-Type" : "application/json", "Authorization" : "Bearer {}".format(access_token)}
    SPOTIFY_GET = f"https://api.spotify.com/v1/playlists/{playlistsId}/tracks"

    try:
        
        request_body = json.dumps({
          "uris" : uris
        })

        
        #response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json",
        #              "Authorization":f"Bearer {token}"})

        count = requests.get(SPOTIFY_GET.format(playlistsId),headers=headers,verify=False)


          
        response = requests.post(SPOTIFY_API_PLAYLIST_TRACKS.format(playlistsId,albumUids),data = request_body,headers=headers,verify=False)
        
       
        #response = requests.post(url = SPOTIFY_API_PLAYLIST_TRACKS, data = request_body, headers=headers)


        if(response.status_code == 201):
            return response.json()
        else:
            print("[ERROR] " + response.text)
            raise
    except:
        raise

def createPlaylist(uid,name,description,access_token):
    headers={"Accept" : "application/json", "Content-Type" : "application/json", "Authorization" : "Bearer {}".format(access_token)}

    data = {}
    data['name'] = name
    data['description'] = description
    data['public'] = 'false'

    try:
        response = requests.post(SPOTIFY_API_CREATE_PLAYLIST.format(userID),data=json.dumps(data),headers=headers,verify=False)

        if(response.status_code == 201):
            return response.json()['id']
        else:
            if( 'error' in response.json() and 'The access token expired' in response.json()['error']['message']):
                print("[WARNING] The access token expired, requesting refresh.")
                access_token = getNewAccessToken()
                with open('.accesstoken',mode='w') as w:
                    w.writelines(access_token)
                w.close()

            createPlaylist(uid,name,description,access_token)


    except:
        raise

def getNewAccessToken():
    headers={"Authorization" : "Basic " + SPOTIFY_API_BASE64_CLIENT}
    data={}
    data['grant_type']="refresh_token"
    data['refresh_token']=SPOTIFY_API_REFRESH_TOKEN

    try:
        response = requests.post(SPOTIFY_API_TOKEN,data=data,headers=headers,verify=False)

        if(response.status_code == 200):
            return response.json()['access_token']
        else:
            print("[ERROR] Failed to get access token {}".format(response.text))
            raise
    except:
        print("[ERROR] Failed to send request to get new access token.")
        raise

def searchArtistId(album,access_token):
    headers={"Accept" : "application/json", "Content-Type" : "application/json", "Authorization" : "Bearer {}".format(access_token)}

    try:
        
        response = requests.get(SPOTIFY_API_SEARCH_ARTIST.format(album),headers=headers,verify=False)

        if(response.status_code == 200 and len(response.json()['albums']['items']) > 0):
            #print(response.text)
            return response.json()['albums']['items'][0]['id']
        else:
            
            if( 'error' in response.json() and 'The access token expired' in response.json()['error']['message']):
                print("[WARNING] The access token expired, requesting refresh.")
                access_token = getNewAccessToken()
                with open('.accesstoken',mode='w') as w:
                    w.writelines(access_token)
                w.close()

                searchArtistId(album,access_token)
            else:
                pass
    except:
        raise

def getArtistAlbum(artistId,access_token):
    headers={"Accept" : "application/json", "Content-Type" : "application/json", "Authorization" : "Bearer {}".format(access_token)}

    try:

        response = requests.get(SPOTIFY_GET_ALBUMS_TRACKS.format(albumId),headers=headers,verify=False)

        json_response = response.json()
        #print(json_response)
        #for result in json_response['tracks']['items']:
            #trackArtists = result['artists']
            #print(trackArtists)
        for i,j in enumerate(json_response['items']):
            if(len(uris)<=99):
                uris.append(j['uri'])
                print(f"{i+1} \"{j['name']}\" by {j['artists'][0]['name']}")

        if(response.status_code == 200):
            
            return response.json()
        else:
            print(response.status_code)
            raise
    except:
        raise


getAlbums()
print(ALL_TRACKS)
playlistId=createPlaylist(userID,name,description,access_token)
print(playlistId)
for album in ALL_TRACKS:
    print(album)
    SPOTIFY_API_SEARCH_ARTIST = f'https://api.spotify.com/v1/search?query={album}&offset=0&limit=30&type=album'
    albumId=searchArtistId(album,access_token)
    print(albumId)
    SPOTIFY_GET_ALBUMS_TRACKS=f"https://api.spotify.com/v1/albums/{albumId}/tracks"
    albumUids = getArtistAlbum(albumId,access_token)
SPOTIFY_API_PLAYLIST_TRACKS=f"https://api.spotify.com/v1/playlists/{playlistId}/tracks"
    #for song in albumUids:
addAlbumsPlaylist(playlistId,albumUids,access_token)

