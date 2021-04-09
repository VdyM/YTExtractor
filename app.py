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


def saveToFile(file_path:str, data:list):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            try:
                file.write(str(item)+'\n')
            except Exception as e:
                print("File write exeption\n", e)
                return

    print("File {0} was created".format(file_path))


def deleteFile(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        print("The file has been deleted: ", file_path)
    else:
        print("The file does not exist")

def deleteSameLastFiles( path_dir:str ):
    files_list_Nsorted = os.listdir(path_dir)
    n = len(files_list_Nsorted)
    if n < 2 :
        return
    files_list = sorted(files_list_Nsorted, reverse=True) # new ... oldest
    last1_name, last2_name = files_list[0], files_list[1]
    print(last1_name, last2_name)
    last1_path = path_dir + os.path.sep + last1_name
    last2_path = path_dir + os.path.sep + last2_name
    if filecmp.cmp(last1_path, last2_path):
        deleteFile(last2_path)


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


def getRequest(playlist_ID: str, API_key: str, payload: dict):
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
    jsonresponse, stepData = getRequest(playlist_ID, API_key, payload)
    if not jsonresponse:
        return

    data.extend(stepData)
    while "nextPageToken" in jsonresponse.keys():
        nextPageToken = jsonresponse["nextPageToken"]
        payload = {"pageToken": nextPageToken, 'playlistId': playlist_ID, 'key': API_key}
        jsonresponse, tempData = getRequest(playlist_ID, API_key, payload)
        data.extend(tempData)
    return data



def main():
    today = datetime.datetime.now()
    date_now = today.strftime("%Y_%m_%d")
    print("Date :", today)
    checkCreateDir(DIR_PATH)
    for count, playlist_id in enumerate(key.PLAYLIST_IDS):
        playlist_name, itemCount = getNameAndNumber(playlist_id, key.API_KEY)
        playlist_name_array = playlist_name.split()
        directory_name = "_".join(playlist_name_array)
        playlist_Dir = DIR_PATH + os.path.sep + directory_name
        checkCreateDir(playlist_Dir)
        filename = date_now +".txt"
        file_path = playlist_Dir + os.path.sep + filename
        if os.path.isfile(file_path):
            print("File {0} exist".format(file_path))
            continue
        playlist_items = getPlaylistItems(playlist_id, key.API_KEY)
        data = [playlist_id, playlist_name, itemCount] + playlist_items
        saveToFile(file_path, data)
        deleteSameLastFiles(playlist_Dir)


if __name__ == "__main__":
    main()