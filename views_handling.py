from requests import get
from datetime import datetime
import os
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from app_decorators import connected

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

@connected
def reinitialise_promotional_video_table(cursor = None):
    try:
        cursor.execute("DROP TABLE YoutubePromotionalVideos")
    except:
        pass
    cursor.execute("CREATE TABLE YoutubePromotionalVideos (SongVocadbID int, YoutubeID nvarchar(12), HighPriority boolean)")

@connected
def reinitialise_song_views_table(cursor = None):
    try:
        cursor.execute("DROP TABLE SongViews")
    except:
        pass
    cursor.execute("CREATE TABLE SongViews (SongVocadbID int, updateDate Date, viewCount int, PRIMARY KEY (SongVocadbID, updateDate))")

@connected
def reinitialise_artist_views_table(cursor = None):
    try:
        cursor.execute("DROP TABLE ArtistViews")
    except:
        pass
    cursor.execute("CREATE TABLE ArtistViews (ArtistVocadbID int, updateDate Date, viewCount int, PRIMARY KEY (ArtistVocadbID, updateDate))")

@connected
def append_youtube_promotional_video(id: int, cursor = None):
    YTPVs = ""
    response = get(f'https://vocadb.net/api/songs/{id}?fields=PVs')
    PVs = response.json()["pvs"]
    for i, PV in enumerate(PVs):
        if PV["service"] == "Youtube":
            cursor.execute(f"INSERT INTO YoutubePromotionalVideos (SongVocadbID, YoutubeID) VALUES ({id}, '{PV['url'][-11:]}')")
            if i:
                YTPVs = f"{YTPVs},{PV['url'][-11:]}"
            else:
                YTPVs = f"{PV['url'][-11:]}"
    return YTPVs

def request_token(filename: str):
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', scopes)

    credentials = flow.run_local_server(port=0)

    with open(f'{filename}.json', 'w') as token_file:
        token_file.write(credentials.to_json())

def refresh_token():
    
    credentials = Credentials.from_authorized_user_file(f'token.json', scopes)

    if not credentials.valid and credentials.expired and credentials.refresh_token:
        from google.auth.transport.requests import Request

        credentials.refresh(Request())

    with open(f'token.json', 'w') as token_file:
        token_file.write(credentials.to_json())

def yt_request(Id: str):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    credentials = Credentials.from_authorized_user_file('token.json', scopes)
    if not credentials.valid and credentials.expired and credentials.refresh_token:
        request_token()
    else:
        refresh_token()
    credentials = Credentials.from_authorized_user_file('token.json', scopes)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=Id
    )
    response = request.execute()

    return response

def fetch_views(youtubeID: str):
    response = yt_request(youtubeID)
    if type(response["items"]) == list:
        return [item["statistics"]["viewCount"] for item in response["items"]]
    else:
        return response["items"]["statistics"]["viewCount"]

@connected
def fetch_views_by_vocadb_id(vocadb_ID: int, cursor = None):
    urls = cursor.execute(f"SELECT YoutubeID FROM YoutubePromotionalVideos WHERE SongVocadbID IS {vocadb_ID}").fetchall()
    url_string = ""
    if not urls:
        url_string = append_youtube_promotional_video(vocadb_ID)
    else:
        for i, url in enumerate(urls):
            if not i: 
                url_string = url[0]
            else:
                url_string = f"{url_string},{url[0]}"
    return sum(map(int, fetch_views(url_string)))

@connected
def update_views_for_song(vocadb_ID: int, cursor = None):
    cursor.execute(f"INSERT INTO SongViews (SongVocadbID, updateDate, viewCount) VALUES ({vocadb_ID}, {str(datetime.now())[:10]}, {fetch_views_by_vocadb_id(vocadb_ID)})")

@connected
def update_all_songs(cursor = None):
    queue = cursor.execute(f"SELECT SongVocadbID FROM SongInfo WHERE TrackedStatus=TRUE").fetchall()
    for song in queue:
        if True:
            pass


def main():
    print(fetch_views_by_vocadb_id(365620))


if __name__ == "__main__":
    main()