from sqlite3 import connect
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.axis import Axis   
from datetime import date

current_date = str(date.today())
mpl.style.use('bmh')

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
            if artist in singer_color:
                line, = ax.plot(singer_stats[0][1:], singer_stats[1][1:], color=singer_color[sorted_artists[i]], label=sorted_artists[i])
            else:
                line, = ax.plot(singer_stats[0][1:], singer_stats[1][1:], label=sorted_artists[i])
            lines.append(line)
        print(sorted_artists)

    if plot_mode:
        plt.legend()
    formatter = ticker.FormatStrFormatter('%i') 
    Axis.set_major_formatter(ax.yaxis, formatter)  
    mpl.style.use('seaborn-v0_8')   
    plt.show()                      


def main():
    analysis(["歌愛ユキ", "NONE", "CircusP"])


if __name__ == "__main__":
    main()