from requests import get
from sqlite3 import connect
import os
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from main_db import connected

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

@connected
def initialise_PV_database(cursor):
    cursor.execute("CREATE TABLE YoutubePVs (ID INTEGER PRIMARY KEY, SongVID int, YTID nvarchar(12))")

@connected
def append_YTPV(cursor, id: int):
    YTPVs = []
    response = get(f'https://vocadb.net/api/songs/{id}?fields=PVs')
    PVs = response.json()["pvs"]
    for PV in PVs:
        if PV["service"] == "Youtube":
            cursor.execute(f"INSERT INTO YoutubePVs (SongVID, YTID) VALUES ({id}, '{PV["url"][-11:]}')")
            YTPVs.append(PV["url"][-11:])
    return YTPVs

def request_token(filename: str):
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', scopes)

    credentials = flow.run_local_server(port=0)

    with open(f'{filename}.json', 'w') as token_file:
        token_file.write(credentials.to_json())

def refresh_token(filename: str):
    
    credentials = Credentials.from_authorized_user_file(f'{filename}.json', scopes)

    if not credentials.valid and credentials.expired and credentials.refresh_token:
        from google.auth.transport.requests import Request

        credentials.refresh(Request())

    with open(f'{filename}.json', 'w') as token_file:
        token_file.write(credentials.to_json())

def yt_request(Id: str, filename: str):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    credentials = Credentials.from_authorized_user_file(f'{filename}.json', scopes)
    if not credentials.valid and credentials.expired and credentials.refresh_token:
        request_token(filename)
    else:
        refresh_token(filename)
    credentials = Credentials.from_authorized_user_file(f'{filename}.json', scopes)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=Id
    )
    response = request.execute()

    return response

def main():
    """YTPVs = append_YTPV(288238)
    ids = YTPVs[0]
    if len(YTPVs) > 1:
        for YTPV in YTPVs[1:]:
            ids = f"{ids},{YTPV}"""
    items = yt_request(f'Q89OdbX7A8E', "token1")["items"]
    #print(items)
    for item in items:
        print(item["snippet"]["localized"]["title"], item["statistics"])


if __name__ == "__main__":
    main()