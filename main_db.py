import requests
from datetime import date, datetime, timedelta
from app_decorators import connected

current_date = str(date.today())
det_overflows = ['2008-08-16', '2008-12-29', '2009-08-15', '2009-09-06', '2010-11-14', '2010-12-31', '2011-01-16', '2011-06-12', '2011-08-13', '2011-09-04', '2011-11-19', '2011-12-31', '2012-02-05', '2012-04-28', '2012-07-08', '2012-08-11', '2012-10-28', '2012-12-15', '2012-12-31', '2013-03-24', '2013-04-27', '2013-04-29', '2013-07-07', '2013-08-12', '2013-10-20', '2013-11-17', '2013-12-31', '2014-04-26', '2014-04-27', '2016-10-30', '2017-04-30', '2017-08-11', '2017-10-15', '2017-10-29', '2017-12-29', '2018-04-08', '2018-08-10', '2018-10-28', '2018-12-30', '2019-04-28', '2019-10-27', '2019-12-31', '2021-04-25', '2021-10-31', '2022-04-24', '2022-07-03', '2022-07-16', '2022-07-16', '2022-08-06', '2022-08-06', '2022-11-12', '2023-04-29', '2023-04-30', '2023-06-10', '2023-06-10', '2023-10-29', '2023-11-19', '2024-04-27', '2024-04-28', '2024-05-04', '2024-07-21', '2024-10-27', '2024-11-23']
new_overflows = []

@connected
def reinitialise_song_info_table(cursor = None):
    # General song info table, only used for the frontend and view updates
    try:
        cursor.execute("DROP TABLE SongInfo")
    except:
        pass
    cursor.execute("CREATE TABLE SongInfo (VocadbID INTEGER PRIMARY KEY, Name nvarchar(255), Type nvarchar(255), ReleaseDate Date, TrackedStatus BOOLEAN)")

@connected
def reinitialize_song_artists_table(cursor = None):
    # Main table for counting songs by artist per date
    try:
        cursor.execute("DROP TABLE SongArtists")
    except:
        pass
    cursor.execute("CREATE TABLE SongArtists (SongVocadbID int, SongReleaseDate Date, ArtistName nvarchar(255), PRIMARY KEY (ArtistName, SongVocadbID))")

def add_days(start_date: str, days: int):
    return str(datetime.strptime(start_date, "%Y-%m-%d") \
                              + timedelta(days))[:10]
    
@connected
def bulk_fetch_songs(artist_ID = 0, start_release_date = None, release_step = 1, min_length = None, max_length = None, exclude_miku = False, include_miku = False, logs = [0, 0, 0, 0], cursor = None):
    global new_overflows

    errors = 0
    passed = 0
    request_string = "https://vocadb.net/api/songs?start=0&maxResults=100&getTotalCount=true&fields=ThumbUrl"

    if artist_ID:
        request_string += f"&artistId%5B%5D={artist_ID}"
    if start_release_date:
        request_string += f"&afterDate={start_release_date}&beforeDate={add_days(start_release_date, release_step)}"
        if min_length:
            request_string += f"&minLength={min_length}&maxLength={max_length}"
            if exclude_miku:
                request_string += '&advancedFilters={%0A%20 "filterType"%3A "artistId"%2C%0A%20 "negate"%3A false%2C%0A%20 "param"%3A "1"%0A}'
            elif include_miku:
                request_string += "&artistId%5B%5D=1"

    response = requests.get(request_string).json()

    print(response["totalCount"])
    if response["totalCount"] > 100:
        if not start_release_date:
                logs = bulk_fetch_songs(artist_ID, start_release_date = "2003-01-01", release_step = 16384).append(response["totalCount"])
        elif release_step > 1:
            new_logs = bulk_fetch_songs(artist_ID, start_release_date = start_release_date, release_step = release_step // 2)
            logs = [sum(x) for x in zip(new_logs, bulk_fetch_songs(artist_ID, start_release_date = add_days(start_release_date, release_step // 2), release_step = release_step // 2))]
        elif not max_length :
            new_logs = bulk_fetch_songs(artist_ID, start_release_date, min_length = 0, max_length = 512)
            logs = [sum(x) for x in zip(new_logs, bulk_fetch_songs(artist_ID, start_release_date, min_length = 512, max_length = 100000))]
        elif max_length - min_length > 1:
            new_logs = bulk_fetch_songs(artist_ID, start_release_date, min_length = min_length, max_length = (max_length + min_length) // 2)
            logs = [sum(x) for x in zip(new_logs, bulk_fetch_songs(artist_ID, start_release_date, min_length = (max_length + min_length) // 2, max_length = max_length))]
        elif artist_ID != 1 and not exclude_miku and not include_miku:
            new_logs = bulk_fetch_songs(artist_ID, start_release_date, min_length = min_length, max_length = max_length, exclude_miku = True)
            logs = [sum(x) for x in zip(new_logs, bulk_fetch_songs(artist_ID, start_release_date, min_length = min_length, max_length = max_length, include_miku = True))]
        else:
            print(response["totalCount"])
            new_overflows.append(start_release_date)
            print("damn...")
            logs = [0, 0, 0, 0]
    else:
        songs = response["items"]
        for song in songs:
            song["name"] = song["name"].replace("'", "\'")
            song["artistString"] = song["artistString"].replace("'", "\'")
            try:
                date = song["publishDate"].split("T00:")[0]
            except:
                errors += 1
                continue
            db_song = cursor.execute(f"SELECT * FROM SongInfo WHERE VocadbID={song['id']}").fetchone()
            if db_song:
                if song["id"] == db_song[0]:
                    passed += 1
                    continue
            else:
                artists = song["artistString"].replace(" feat. ", ", ").split(", ")
                if "various" in artists:
                    artists = fetch_song_artists(song["id"])
                artists = set(artists)
                for artist in artists:
                    cursor.execute(f"INSERT INTO SongArtists (SongVocadbID, SongReleaseDate, ArtistName) VALUES ({song["id"]}, '{date}', (?))", (f"{artist}",))
                cursor.execute(f"INSERT INTO SongInfo (VocadbID, ReleaseDate, Type, Name, TrackedStatus) VALUES ({song["id"]}, '{date}', '{song["songType"]}', (?), FALSE)", (f"{song["name"]}",))
        logs = [passed, len(songs) - passed - errors, errors, len(songs)]

    return logs
    
def fetch_song_artists(song_ID: int):
    artists = []
    response = requests.get(f"https://vocadb.net/api/songs/{song_ID}?fields=Artists")
    for artist in response.json()["artists"]:
        artists.append(artist["name"])
    return artists

@connected
def main(cursor = None):
    pass
    #for overflow in det_overflows:
    #    logs = bulk_fetch_songs(start_release_date = overflow, release_step = 1)
    #print(f"{logs[4]} songs expected, {logs[3]} songs recieved, {logs[0]} songs passed, {logs[1]} songs appended, {logs[2]} songs caused an error")
    #print(f"{logs[3]} songs expected, {logs[3]} songs recieved, {logs[0]} songs passed, {logs[1]} songs appended, {logs[2]} songs caused an error")
    #print(new_overflows)

if __name__ == "__main__":
    main()