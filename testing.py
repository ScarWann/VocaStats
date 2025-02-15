import requests
from sqlite3 import connect
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.axis import Axis   
from datetime import date

current_date = str(date.today())
mpl.style.use('bmh')
connection = connect("Vocaloid.db")
cursor = connection.cursor()

def rewrite_database():
    yuki_base = ["0, 292770, '2009-11-13', 'Cover', '±', 'Koya Matsuo'", "292770, '2009-11-13', 'Cover', '±', '歌愛ユキ'"]
    luka_base = ["-1, 165051, '2009-01-06', 'Original', 'afternoon sunshine', 'Unknown producer(s)'", "292770, '2009-01-06', 'Original', 'afternoon sunshine', '巡音ルカ'"]
    cursor.execute("DROP TABLE Songs")
    cursor.execute("CREATE TABLE Songs (ID int, VID int, ReleaseDate DATE, Type nvarchar(255), Name nvarchar(255), Artist nvarchar(255))")
    cursor.execute(f"INSERT INTO Songs (ID, VID, ReleaseDate, Type, Name, Artist) VALUES ({yuki_base[0]})")
    cursor.execute(f"INSERT INTO Songs (VID, ReleaseDate, Type, Name, Artist) VALUES ({yuki_base[1]})")
    cursor.execute(f"INSERT INTO Songs (ID, VID, ReleaseDate, Type, Name, Artist) VALUES ({luka_base[0]})")
    cursor.execute(f"INSERT INTO Songs (VID, ReleaseDate, Type, Name, Artist) VALUES ({luka_base[1]})")
    #cursor.execute("INSERT INTO Songs (VID, ReleaseDate, Type, Name, Artist) VALUES (292770, '2009-11-13', 'Cover', '±', '歌愛ユキ')")
    #print(cursor.execute("SELECT * FROM Songs").fetchall())
    #print(cursor.execute("SELECT * FROM Songs WHERE id=(SELECT max(ID) FROM Songs)").fetchall())
    connection.commit()
    connection.close()

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
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
            for occurence in occurences:
                if months[-1] != occurence[0][:7]:
                    months.append(occurence[0][:7])
                    amounts.append(occurence[1] + amounts[-1])
                else:
                    amounts[-1] += occurence[1]
            variable = months
        elif mode == "spm":
            months = [0]
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
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
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
            for occurence in occurences:
                if years[-1] != occurence[0][:4]:
                    years.append(occurence[0][:4])
                    amounts.append(occurence[1])
                else:
                    amounts[-1] += occurence[1]
            variable = years
        elif mode == "say":
            years = [0]
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
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
            occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
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
            occurence = cursor.execute(f"SELECT Artist, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY Artist").fetchone()
            artist = occurence[0]
            amounts = occurence[1]
            variable = artist
        elif mode == "spa":
            break
        elif mode == "spt":
            occurence = cursor.execute(f"SELECT Type, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY Type").fetchall()
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

def add_month(date: str, addition = 1) -> str:
    year, month, day = map(int, date.split("-"))
    month += addition
    if day > 28:
        day = 28
    if month > 12:
        year += 1
        month -= 12
    if month < 10:
        result = f"{str(year)}-0{str(month)}-{day}"
    else:
        result = f"{str(year)}-{str(month)}-{day}"
    return result

def add_days(date: str, addition = 1) -> str:
    year, month, day = map(int, date.split("-"))
    day += addition
    match month:
        case 1 | 3 | 5 | 7 | 8 | 10 | 12:
            if day > 31:
                month += 1
                day -= 31
        case 4 | 6 | 9 | 11:
            if day > 30:
                month += 1
                day -= 30
        case 2:
            if day > 28 and year % 4 != 0:
                month += 1
                day -= 28
            elif day > 29:
                month += 1
                day -= 29
    if month > 12:
        year += 1
        month -= 12
    return f"{str(year)}-{str(month)}-{day}"

def get_last_song_date_by_singer(singer: str) -> str:
    return cursor.execute(f"SELECT max(ReleaseDate) FROM (SELECT * FROM Songs WHERE Artist='{singer}')").fetchone()[0]

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
            sql_write(artist_ID, artist, add_days(first_date, i), 1, ignore_overflow)
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
            #db_song = cursor.execute(f"SELECT * FROM Songs WHERE VID={song['id']}").fetchone()
            if song["id"] == db_song[1]:
                passed += 1
                continue
        except:
            for producer in producers:
                cursor.execute(f"INSERT INTO Songs (VID, ReleaseDate, Type, Name, Artist) VALUES ({song["id"]}, '{date}', '{song["songType"]}', '{song["name"]}', '{producer}')")
            for singer in singers:
                cursor.execute(f"INSERT INTO Songs (ID, VID, ReleaseDate, Type, Name, Artist) VALUES ({last_id + i}, {song["id"]}, '{date}', '{song["songType"]}', '{song["name"]}', '{singer}')")
    print(f"Added {len(songs) - passed} songs, Passed {passed} songs, Total {len(songs)} received")
    if len(songs) == 100:
        return f"{first_date}"
    else:
        return None

def get_all_songs_by_artist(id: int, artist: str, start_date = "2007-6-1", stop_date = current_date):
    flag_date = start_date
    stop_year, stop_month, stop_day = stop_date.split("-")
    overflow_dates = []
    flag_year, flag_month, flag_day = flag_date.split("-")
    while flag_year < stop_year or flag_month < stop_month or flag_day <= stop_day :
        flag_year, flag_month, flag_day = flag_date.split("-")
        overflow_date = sql_write(id, artist, flag_date, 10, ignore_overflow=True)
        if overflow_date:
            overflow_dates.append(overflow_date)
        flag_date = add_days(flag_date, 10)
        time.sleep(0.001)
        connection.commit()
    print(f"Overflow dates: {overflow_dates}")
    return overflow_dates

def get_all_songs():
    overflowing_singers = []
    singer_list = [["鏡音レン", "15"],
                   ["重音テト", "116"],
                   ["可不", "83928"], 
                   ["v flower", "21165"], 
                   ["足立レイ", "74389"],
                   ["VY1", "117"],
                   ["MEIKO", "176"],
                   ["KAITO", "71"],
                   ["結月ゆかり", "623"],
                   ["東北きりたん", "36207"]]
    for singer, i in enumerate(singer_list):
        if i == 7 or i == 8:
            overflow_dates = get_all_songs_by_artist(singer[1], singer[0], date="2004-1-1")
        else:
            overflow_dates = get_all_songs_by_artist(singer[i][1], singer[i][0])
        overflowing_singers.append([singer[i][0], overflow_dates])
    print(overflowing_singers)
    connection.close()