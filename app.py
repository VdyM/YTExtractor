import os
import requests
import key
import datetime
import filecmp


URL_PLAYLISTITEMS:str = 'https://youtube.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails'
URL_PLAYLISTS:str = 'https://youtube.googleapis.com/youtube/v3/playlists?part=contentDetails%2C%20snippet'
DIR_PATH:str = os.path.expanduser('~/Documents') + os.path.sep + "YTExtractor"


def checkDir(path:str) -> bool:
    return os.path.isdir(path)


def createDir(path:str):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


def checkCreateDir(path:str):
    if not checkDir(path):
        createDir(path)


def saveToFile(filename:str, data:list, dir_path:str=DIR_PATH):
    path:str = dir_path + os.path.sep + filename
    with open(path, 'w', encoding='utf-8') as file:
        for item in data:
            try:
                file.write(str(item)+'\n')
            except Exception as e:
                print("File write exeption\n", e)
                return
    print("The File {0} was created".format(filename))


def deleteFile(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("The file has been deleted: ", file_path)
    else:
        print("The file does not exist")


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
    return name, number


def getRequestAndPrint(playlist_ID: str, API_key: str, payload: dict):
    response = requests.get(URL_PLAYLISTITEMS, params=payload)
    if response.status_code != requests.codes.ok:
        print("Error with getPlaylistItem GET request playlist_ID:", playlist_ID)
        return
    jsonresponse: dict = response.json()
    data = []
    for item in jsonresponse["items"]:
        VideoTitle = item["snippet"]["title"]
        VideoId = item["contentDetails"]["videoId"]
        Position = item["snippet"]["position"]
        data.append('{0}\t{1}\t{2}'.format(str(Position), str(VideoId), VideoTitle))
    return jsonresponse, data


def getPlaylistItems(playlist_ID: str, API_key: str) -> list:
    payload = {'playlistId': playlist_ID, 'key': API_key}
    data = []
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



def main():
    today = datetime.datetime.now()
    date_now = today.strftime("%Y_%m_%d")
    print("Date :", today, date_now)
    checkCreateDir(DIR_PATH)
    for count, playlist_id in enumerate(key.PLAYLIST_IDS):
        playlist_name, itemCount = getNameAndNumber(playlist_id, key.API_KEY)
        playlist_name_array = playlist_name.split()
        directory_name = "_".join(playlist_name_array)
        playlist_Dir = DIR_PATH + os.path.sep + directory_name
        print(playlist_Dir)
        checkCreateDir(playlist_Dir)
        file1 = playlist_Dir + os.path.sep + "2021_04_05.txt"
        file2 = playlist_Dir + os.path.sep + "2021_04_04.txt "
        print(filecmp.cmp(file1, file2))
        break
        filename = date_now +".txt"
        playlist_items = getPlaylistItems(playlist_id, key.API_KEY)
        data = [playlist_id, playlist_name, itemCount] + playlist_items
        saveToFile(filename, data, playlist_Dir)


if __name__ == "__main__":
    main()