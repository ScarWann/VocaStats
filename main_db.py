import requests
from sqlite3 import connect
from datetime import date, datetime, timedelta


current_date = str(date.today())
connection = connect("Vocaloid.db")
cursor = connection.cursor()

def connected(func):

    def wrapper(*args, **kwargs):
        connection = connect("Vocaloid.db")
        cursor = connection.cursor()
        result = func(cursor, *args, **kwargs)
        cursor.close()
        connection.commit()
        connection.close()
        return result
    
    return wrapper


def reinitialise_main_database():
    try:
        cursor.execute("DROP TABLE Songs")
    except:
        pass
    cursor.execute("CREATE TABLE Songs (ID INTEGER PRIMARY KEY, VID int, Type nvarchar(255), ReleaseDate Date, Name nvarchar(255), TrackedStatus BOOLEAN, ImgURL nvarchar(255))")
    connection.commit()

def reinitialize_artist_database():
    try:
        cursor.execute("DROP TABLE SongArtists")
    except:
        pass
    cursor.execute("CREATE TABLE SongArtists (ID INTEGER PRIMARY KEY, SongVID int, ReleaseDate Date, Name nvarchar(255))")
    connection.commit()

def requestStatus(Response):
    if Response.status_code == 200:
        print("Request successful")
    else:
        print("Requst unsuccessful, error type --", Response.status_code)

def add_days(start_date: str, days: int):
    return str(datetime.strptime(start_date, "%Y-%m-%d") \
                              + timedelta(days))[:10]

def get_last_song_date_by_singer(singer: str) -> str:
    return cursor.execute(f"""SELECT max(ReleaseDate) FROM
                            (SELECT * FROM 
                            SongArtists WHERE Name='{singer}')""").fetchone()[0]

def get_last_id() -> int:
    return cursor.execute(f"SELECT max(ID) FROM Songs").fetchone()[0]
    
def bulk_fetch_songs(artist_ID: int, start_date = None, step = 1, min_length = None, max_length = None, console_report = True):
    if console_report:
        passed = 0
    if max_length:
        end_date = add_days(start_date, step)
        response = requests.get(f"https://vocadb.net/api/songs?afterDate={start_date}&beforeDate={end_date}&artistId%5B%5D={artist_ID}&start=0&maxResults=100&getTotalCount=true&minLength={min_length}&maxLength={max_length}")
    elif start_date:
        end_date = add_days(start_date, step)
        response = requests.get(f"https://vocadb.net/api/songs?afterDate={start_date}&beforeDate={end_date}&artistId%5B%5D={artist_ID}&start=0&maxResults=100&getTotalCount=true")
    else:                         
        response = requests.get(f"https://vocadb.net/api/songs?artistId%5B%5D={artist_ID}&start=0&maxResults=100&getTotalCount=true")
        if response.json()["totalCount"] > 100:
            bulk_fetch_songs(artist_ID, start_date = "2003-01-01", step = 16384)
    jresponse = response.json()
    if jresponse["totalCount"] > 100 and step > 1 and start_date:
        bulk_fetch_songs(artist_ID, start_date = start_date, step = step // 2)
        bulk_fetch_songs(artist_ID, start_date = add_days(start_date, step // 2), step = step // 2)
    elif jresponse["totalCount"] > 100 and step == 1 and start_date and not max_length :
        bulk_fetch_songs(artist_ID, start_date, min_length = 0, max_length = 1024)
    elif jresponse["totalCount"] > 100 and step == 1 and start_date and max_length and (max_length - min_length) > 1:
        bulk_fetch_songs(artist_ID, start_date, min_length = min_length, max_length = (max_length + min_length) // 2)
        bulk_fetch_songs(artist_ID, start_date, min_length = (max_length + min_length) // 2, max_length = max_length)
    elif jresponse["totalCount"] > 100 and step == 1 and start_date and max_length and (max_length - min_length) == 1:
        print(jresponse)
        raise Exception("Song overflow")
    elif jresponse["totalCount"] < 101:
        songs = jresponse["items"]
        for song in songs:
            song["name"] = song["name"].replace("'", "")
            song["artistString"] = song["artistString"].replace("'", "").replace(",", " ").replace(" feat. ", " ")
            date = song["publishDate"].split("T00:")[0]
            db_song = cursor.execute(f"SELECT * FROM Songs WHERE VID={song['id']}").fetchone()
            if db_song:
                if song["id"] == db_song[1]:
                    passed += 1
                    continue
            else:
                try:
                    artists = song["artistString"].split()
                except:
                    artists = fetch_song_artists(song["id"])
                for artist in artists:
                    #artist = artist.replace("'", "")
                    cursor.execute(f"INSERT INTO SongArtists (SongVID, ReleaseDate, Name) VALUES ({song["id"]}, '{date}', '{artist}')")
                cursor.execute(f"INSERT INTO Songs (VID, ReleaseDate, Type, Name) VALUES ({song["id"]}, '{date}', '{song["songType"]}', '{song["name"]}')")
                connection.commit()
        if start_date:
            print(start_date, end_date)
        print(f"Passed {passed} songs, appended {len(songs) - passed} songs, recieved {len(songs)} songs")
    
def fetch_song_artists(song_ID: int):
    artists = []
    response = requests.get(f"https://vocadb.net/api/songs/{song_ID}?fields=Artists")
    for artist in response.json()["artists"]:
        artists.append(artist["name"])
    return artists

def main():
    bulk_fetch_songs(106996)

if __name__ == "__main__":
    main()