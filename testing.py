import requests
from sqlite3 import connect
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.axis import Axis   
from datetime import date
import os
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

current_date = str(date.today())
mpl.style.use('bmh')
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def initialise_PV_database():
    connection = connect("TrackedPVs.db")
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE YoutubePVs (ID INTEGER PRIMARY KEY, SongVID int, YTID nvarchar(12))")
    cursor.close()

def append_YTPV(id: int):
    YTPVs = []
    connection = connect("TrackedPVs.db")
    cursor = connection.cursor()
    response = requests.get(f'https://vocadb.net/api/songs/{id}?fields=PVs')
    PVs = response.json()["pvs"]
    for PV in PVs:
        if PV["service"] == "Youtube":
            cursor.execute(f"INSERT INTO YoutubePVs (SongVID, YTID) VALUES ({id}, '{PV["url"][-11:]}')")
            YTPVs.append(PV["url"][-11:])
    connection.commit()
    connection.close()
    return YTPVs

def analysis(artists: list):
    connection = connect("Vocaloid.db")
    cursor = connection.cursor()
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

def request_token(filename: str):
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', scopes)

    credentials = flow.run_local_server(port=0)

    with open(f'{filename}.json', 'w') as token_file:
        token_file.write(credentials.to_json())

def refresh_token(filename: str):
    
    # Load the credentials from token.json
    credentials = Credentials.from_authorized_user_file(f'{filename}.json', scopes)

    # Check if the token is expired and refresh it
    if not credentials.valid and credentials.expired and credentials.refresh_token:
        from google.auth.transport.requests import Request

        credentials.refresh(Request())

    # Save the refreshed credentials
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