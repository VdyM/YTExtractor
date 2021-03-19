import os
import requests
#import key
import datetime


URL_PLAYLISTITEMS:str = 'https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=50'
URL_PLAYLISTS:str = 'https://youtube.googleapis.com/youtube/v3/playlists?part=contentDetails%2C%20snippet'
dir_path:str = os.path.expanduser('~/Documents') + os.path.sep + "YTExtractor"


def checkDir(path:str) -> bool:
    return os.path.isdir(path)

def createDataDir(path:str):
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s " % path)

def checkCreateDir(path:str):
    if not checkDir(path):
        createDataDir(path)
    else:
        print("The directory exists!!! ")

def saveToFile(filename:str, data:list, dir_path=dir_path):
    path:str = dir_path + os.path.sep + filename
    with open(path, 'w') as file:
        for item in data:
            try:
                file.write(str(item))
            except Exception as e:
                print("File write exeption\n", e)
                return
    print("The File {0} was created".format(filename))

def getNameAndNumber(playlist_ID: str, API_key: str):
    payload = {'id': playlist_ID, 'key': API_key}
    print('\n', "*"*50, '\n', "getNameAndNumber for playlist_id: ", playlist_ID, '\n')
    try:
        response = requests.get(URL_PLAYLISTS, params=payload)
    except Exception as e:
        print("Here is error", e)
        return 
    if response.status_code != requests.codes.ok:
        print("Error with getNameAndNumber GET request playlist_id:", playlist_ID)
        return
    jsonresponse = response.json()
    result:int = jsonresponse["pageInfo"]["totalResults"]
    if result < 1:
        print("No result in getNameAndNumber")
        return
    number:int = jsonresponse["items"][0]["contentDetails"]["itemCount"]
    name:str = jsonresponse["items"][0]["snippet"]["title"]
    print('\t', (name, number))

def getRequestAndPrint(playlist_ID: str, API_key: str, payload: dict):
    response = requests.get(URL_PLAYLISTITEMS, params=payload)
    if response.status_code != requests.codes.ok:
        print("Error with getPlaylistItem GET request playlist_ID:", playlist_ID)
        return
    jsonresponse: dict = response.json()
    for item in jsonresponse["items"]:
        VideoTitle = item["snippet"]["title"]
        VideoId = item["contentDetails"]["videoId"]
        Position = item["snippet"]["position"]
        print(Position," ID:", VideoId, " Title: ", VideoTitle)
    return jsonresponse

def getPlaylistItem(playlist_ID: str, API_key: str):
    payload = {'playlistId': playlist_ID, 'key': API_key}
    jsonresponse = getRequestAndPrint(playlist_ID, API_key, payload)
    if not jsonresponse:
        return
    
    while "nextPageToken" in jsonresponse.keys():
        nextPageToken = jsonresponse["nextPageToken"]
        payload = {"pageToken": nextPageToken, 'playlistId': playlist_ID, 'key': API_key}
        jsonresponse = getRequestAndPrint(playlist_ID, API_key, payload)

    
    

def main():
    todayUTC = datetime.datetime.now(datetime.timezone.utc)
    print("Time :", todayUTC)
    checkCreateDir(dir_path)
    # for item in key.PLAYLISTS_ID:
    #     playlist_ID = item
    #     getNameAndNumber(playlist_ID, key.API_KEY)
    #     getPlaylistItem(playlist_ID, key.API_KEY)

if __name__ == "__main__":
    main()