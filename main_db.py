import requests
from sqlite3 import connect
import time
from math import ceil
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.axis import Axis   
from datetime import date, datetime, timedelta


current_date = str(date.today())
mpl.style.use('bmh')
connection = connect("Vocaloid.db")
cursor = connection.cursor()


def main():
    bulk_fetch_songs(1)

def reinitialise_main_database():
    cursor.execute("DROP TABLE Songs")
    cursor.execute("CREATE TABLE Songs (ID INTEGER PRIMARY KEY, VID int, Type nvarchar(255), ReleaseDate Date, Name nvarchar(255), TrackedStatus BOOLEAN)")
    #cursor.execute("INSERT INTO Songs (VID, ReleaseDate, Type, Name, Artist) VALUES (292770, '2009-11-13', 'Cover', '±', '歌愛ユキ')")
    #print(cursor.execute("SELECT * FROM Songs").fetchall())
    #print(cursor.execute("SELECT * FROM Songs WHERE id=(SELECT max(ID) FROM Songs)").fetchall())
    connection.commit()

def reinitialize_artist_database():
    cursor.execute("DROP TABLE SongArtists")
    cursor.execute("CREATE TABLE SongArtists (ID INTEGER PRIMARY KEY, SongVID int, ReleaseDate Date, Name nvarchar(255))")
    connection.commit()

def analysis(artists: list):
    plt.rcParams['font.family'] = "Noto Sans CJK JP"
    mode = input("Enter mode:\nSongs per months - spm\nSongs at month - sam\nSongs increase per year - siy\nSongs per year - spy\nSongs at year - say\nSongs per artist - sba\n")
    fig, ax = plt.subplots()
    lines = []
    sorted_artists = artists.copy()
    singer_color = {
        '初音ミク': 'cyan',
        '巡音ルカ': 'pink',
        '鏡音リン': 'yellow',
        '鏡音レン': 'orange',
        'GUMI': 'green',
        '重音テト': 'red',
        'v flower': 'purple',
        '可不': 'navy',
        '歌愛ユキ': 'black',
        'MEIKO': 'brown',
        'KAITO': 'blue',
        '稲葉曇': 'gray'
    }
    if mode != "sba" and mode != "spt" and mode != "spa":
        plot_mode = True
    else:
        plot_mode = False
    if plot_mode:
        singers_stats = []
    else: 
        singers_stats = [[], []]
    for artist in artists:
        amounts = [0]
        variable = [0]
        if mode == "sam":
            months = [0]
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM SongArtists WHERE Name LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
            for occurence in occurences:
                if months[-1] != occurence[0][:7]:
                    months.append(occurence[0][:7])
                    amounts.append(occurence[1] + amounts[-1])
                else:
                    amounts[-1] += occurence[1]
            variable = months
        elif mode == "spm":
            months = [0]
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM SongArtists WHERE Name LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
            for occurence in occurences:
                if artist != "鏡音レン":
                    if months[-1] != occurence[0][:7]:
                        months.append(occurence[0][:7])
                        amounts.append(occurence[1])
                    else:
                        amounts[-1] += occurence[1]
                else:
                    if months[-1] != occurence[0][:7]:
                        months.append(occurence[0][:7])
                        amounts.append(occurence[1])
                    else:
                        amounts[-1] += occurence[1]
            variable = months
        elif mode == "spy":
            years = [0]
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM SongArtists WHERE Name LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
            for occurence in occurences:
                if years[-1] != occurence[0][:4]:
                    years.append(occurence[0][:4])
                    amounts.append(occurence[1])
                else:
                    amounts[-1] += occurence[1]
            variable = years
        elif mode == "say":
            years = [0]
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM SongArtists WHERE Name LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
            for occurence in occurences:
                if years[-1] != occurence[0][:4]:
                    years.append(occurence[0][:4])
                    amounts.append(occurence[1] + amounts[-1])
                else:
                    amounts[-1] += occurence[1]
            variable = years
            print(artist, amounts)
        elif mode == "siy":
            change = []
            years = [2009]
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM SongArtists WHERE Name LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
            for occurence in occurences:
                if years[-1] != occurence[0][:4]:
                    years.append(occurence[0][:4])
                    amounts.append(occurence[1])
                else:
                    amounts[-1] += occurence[1]
            for i in range(len(amounts)):
                if i == 0:
                    change.append(amounts[i])
                else:
                    change.append(amounts[i] - amounts[i - 1])
            variable = years
            amounts = change
        elif mode == "sba":
            occurence = cursor.execute(f"SELECT Artist, count(*) as '' FROM (SELECT * FROM SongArtists WHERE Name LIKE '{artist}') GROUP BY Artist").fetchone()
            artist = occurence[0]
            amounts = occurence[1]
            variable = artist
        elif mode == "spa":
            break
        elif mode == "spt":
            occurence = cursor.execute(f"SELECT Type, count(*) as '' FROM (SELECT * FROM SongArtists WHERE Name LIKE '{artist}') GROUP BY Type").fetchall()
            type = occurence[0]
            amounts = occurence[1]
            variable = type
            print(occurence)
        else:
            pass
            #raise Exception("Wrong input")
        
        if plot_mode:
            singers_stats.append([variable, amounts])
        else:
            singers_stats[0].append(variable)
            singers_stats[1].append(amounts)
    
    if mode == "spa":
        occurences = cursor.execute(f"SELECT Artist, count(*) as '' FROM (SELECT * FROM Songs WHERE ID IS NOT NULL) GROUP BY Artist").fetchall()
        artists = []
        amounts = []
        for occurence in occurences:
            artists.append(occurence[0])
            amounts.append(occurence[1])
        variable = artists

    if not plot_mode:
        counts, variables = list(zip(*sorted(zip(amounts, variable), reverse = True)))[0], list(zip(*sorted(zip(amounts, variable), reverse = True)))[1]
        ax.bar(variables[1:40], counts[1:40], width=1, edgecolor="white", linewidth=0.7)
    else:
        lens = []
        for singer_stats in singers_stats:
            lens.append(len(singer_stats[0]))
        _, singers_stats, sorted_artists = zip(*sorted(zip(lens, singers_stats, sorted_artists), reverse = True))
        #_, sorted_artists = zip(*sorted(zip(lens, sorted_artists), reverse = True))
        sorted_artists = list(sorted_artists)
        singers_stats = list(singers_stats)
        for i, singer_stats in enumerate(singers_stats):
            #ax.plot(singer_stats[0][1:], singer_stats[1][1:])
            line, = ax.plot(singer_stats[0][1:], singer_stats[1][1:], color=singer_color[sorted_artists[i]], label=sorted_artists[i])
            lines.append(line)
        print(sorted_artists)

    if plot_mode:
        plt.legend()
    formatter = ticker.FormatStrFormatter('%i') 
    Axis.set_major_formatter(ax.yaxis, formatter)  
    mpl.style.use('seaborn-v0_8')   
    plt.show()    

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

def sql_write(artist_ID: int, artist: str, first_date: str, increase = 1, ignore_overflow = False):
    passed = 0
    last_id = get_last_id()
    second_date = add_days(first_date, increase)
    print(first_date)
    
    response = requests.get(f'https://vocadb.net/api/songs?afterDate={first_date}&beforeDate={second_date}&artistId%5B%5D={artist_ID}&start=0&maxResults=200')
    songs = response.json()["items"]
    if not ignore_overflow:
        if len(songs) == 100 and increase == 1:
            raise Exception("Too many songs")
    elif len(songs) == 100 and increase != 1:
        for i in range(increase):
            sql_write(artist_ID, artist, add_days(first_date, i), ceil(increase / 2), ignore_overflow)
            return None
    for i, song in enumerate(songs, 1):
        song["name"] = song["name"].replace("'", "")
        song["artistString"] = song["artistString"].replace("'", "")
        date = song["publishDate"].split("T00:")[0]
        try:
            producers, singers = song["artistString"].split(" feat. ")
        except:
            producers, singers = "exception", artist
        producers = producers.split(", ")
        singers = singers.split(", ")
        try:
            db_song = cursor.execute(f"SELECT * FROM Songs WHERE VID={song['id']}").fetchone()
            if song["id"] == db_song[0]:
                passed += 1
                continue
        except:
            for producer in producers:
                cursor.execute(f"INSERT INTO Songs (VID, ReleaseDate, Type, Name, Artist) VALUES ({song["id"]}, '{date}', '{song["songType"]}', '{song["name"]}', '{producer}')")
            for singer in singers:
                cursor.execute(f"INSERT INTO Songs (ID, VID, ReleaseDate, Type, Name, Artist) VALUES ({last_id + i}, {song["id"]}, '{date}', '{song["songType"]}', '{song["name"]}', '{singer}')")
        cursor.execute(f"INSERT INTO Songs (ID, VID, ReleaseDate, Type, Name, Artist) VALUES ({last_id + i}, {song["id"]}, '{date}', '{song["songType"]}', '{song["name"]}', '{singer}')")
    print(f"Added {len(songs) - passed} songs, Passed {passed} songs, Total {len(songs)} received")
    if len(songs) == 100:
        return f"{first_date}"
    else:
        return None
    
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
                    artist = artist.replace("'", "")
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
    
def get_all_songs_by_artist(id: int, artist: str, start_date = "2007-6-1", stop_date = current_date): #OUTDATED
    flag_date = start_date
    stop_year, stop_month, stop_day = stop_date.split("-")
    overflow_dates = []
    flag_year, flag_month, flag_day = flag_date.split("-")
    while flag_year < stop_year or flag_month < stop_month or flag_day <= stop_day :
        flag_year, flag_month, flag_day = flag_date.split("-")
        overflow_date = sql_write(id, artist, flag_date, 27, ignore_overflow=True)
        if overflow_date:
            overflow_dates.append(overflow_date)
        flag_date = add_days(flag_date, 10)
        time.sleep(0.001)
        connection.commit()
    print(f"Overflow dates: {overflow_dates}")
    return overflow_dates

def get_all_songs(): #OUTDATED
    overflowing_singers = []
    singer_dict = { 1 : ["鏡音レン", "15"],
                    2 : ["重音テト", "116"],
                    3 : ["可不", "83928"], 
                    4 : ["v flower", "21165"], 
                    5 : ["足立レイ", "74389"],
                    6 : ["VY1", "117"],
                    7 : ["MEIKO", "176"],
                    8 : ["KAITO", "71"],
                    9 : ["結月ゆかり", "623"],
                    10: ["東北きりたん", "36207"]
                    }
    for i in range(2, 11):
        if i == 7 or i == 8:
            overflow_dates = get_all_songs_by_artist(singer_dict[i][1], singer_dict[i][0], date="2004-1-1")
        else:
            overflow_dates = get_all_songs_by_artist(singer_dict[i][1], singer_dict[i][0])
        overflowing_singers.append([singer_dict[i][0], overflow_dates])
    print(overflowing_singers)
    connection.close()

if __name__ == "__main__":
    main()