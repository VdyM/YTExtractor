import os
import requests
import key
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
    data: list = [name, number]
    return data

def getRequestAndPrint(playlist_ID: str, API_key: str, payload: dict):
    response = requests.get(URL_PLAYLISTITEMS, params=payload)
    if response.status_code != requests.codes.ok:
        print("Error with getPlaylistItem GET request playlist_ID:", playlist_ID)
        return
    jsonresponse: dict = response.json()
    data:list = []
    for item in jsonresponse["items"]:
        VideoTitle = item["snippet"]["title"]
        VideoId = item["contentDetails"]["videoId"]
        Position = item["snippet"]["position"]
        data.append((Position, VideoId, VideoTitle))
    return jsonresponse, data

def getPlaylistItem(playlist_ID: str, API_key: str) -> list:
    payload = {'playlistId': playlist_ID, 'key': API_key}
    data: list = []
    jsonresponse, stepData = getRequestAndPrint(playlist_ID, API_key, payload)
    if not jsonresponse:
        return
    
    data.extend(stepData)
    while "nextPageToken" in jsonresponse.keys():
        nextPageToken = jsonresponse["nextPageToken"]
        payload = {"pageToken": nextPageToken, 'playlistId': playlist_ID, 'key': API_key}
        jsonresponse, tempData = getRequestAndPrint(playlist_ID, API_key, payload)
        data.extend(tempData)
    return data

def getAllItem(playlist_ID: str, API_key: str)->list :
    data:list = []
    data1 = getNameAndNumber(playlist_ID, API_key)
    data2 = getPlaylistItem(playlist_ID, API_key)
    data = [playlist_ID] +data1 + data2
    return data
    
    

def main():
    todayUTC = datetime.datetime.now(datetime.timezone.utc)
    print("Time :", todayUTC)
    checkCreateDir(dir_path)
    for count, playlist_id in enumerate(key.PLAYLIST_IDS):
        item = getAllItem(playlist_id, key.API_KEY)
        print('\n[{0}]'.format(count+1))
        for element in item:
            print(element)

if __name__ == "__main__":
    main()