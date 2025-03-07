from requests import get
from math import ceil
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
    cursor.execute("CREATE TABLE YoutubePromotionalVideos (SongVocadbID INTEGER PRIMARY KEY, YoutubeID nvarchar(12))")

@connected
def reinitialise_song_views_table(cursor = None):
    try:
        cursor.execute("DROP TABLE SongViews")
    except:
        pass
    cursor.execute("CREATE TABLE SongViews (SongVocadbID int, updateDate Date, YoutubeID nvarchar(12), viewCount int, PRIMARY KEY (SongVocadbID, updateDate))")

@connected
def reinitialise_artist_views_table(cursor = None):
    try:
        cursor.execute("DROP TABLE ArtistViews")
    except:
        pass
    cursor.execute("CREATE TABLE ArtistViews (ArtistVocadbID int, updateDate Date, viewCount int, PRIMARY KEY (ArtistVocadbID, updateDate))")

@connected
def append_youtube_promotional_video(id: int, cursor = None):
    YTPVs = []
    response = get(f'https://vocadb.net/api/songs/{id}?fields=PVs')
    PVs = response.json()["pvs"]
    for PV in PVs:
        if PV["service"] == "Youtube":
            cursor.execute(f"INSERT INTO YoutubePromotionalVideos (SongVocadbID, YoutubeID) VALUES ({id}, '{PV["url"][-11:]}')")
            YTPVs.append(PV["url"][-11:])
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
        return yt_request(youtubeID)["items"]["statistics"]["viewCount"]

@connected
def update(cursor = None):
    queue = cursor.execute("SELECT YoutubeID FROM YoutubePromotionalVideos WHERE TrackedStatus=TRUE").fetchall()

@connected
def daily_update(cursor = None):
    pass
    

            

def main():
    print(fetch_views("OvL8ptbBGIc,OvL8ptbBGIc"))

if __name__ == "__main__":
    main()