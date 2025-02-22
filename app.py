import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_songs(artist, comparison_type, date_type):
    rev_date_dict = {4 : ["year", "years", "yearly"],
                     7 : ["month", "months", "monthly"],
                     10 : ["day", "days", "daily"]}
    rev_alias_list = {"初音ミク": ["Hatsune Miku", "Miku", "ミク", "1"],
                      "巡音ルカ": ["Megurine Luka", "Luka", "ルカ", "2"],
                      "鏡音リン": ["Kagamine Rin", "Rin", "リン", "14"],
                      "鏡音レン": ["Kagamine Len", "Len", "レン", "15"],
                      "重音テト": ["Kasane Teto", "Teto", "テト", "116"],
                      "歌愛ユキ": ["Kaai Yuki", "Yuki", "ユキ", "191"]}
    date_dict = {v:k for k,li in rev_date_dict.items() for v in li}
    alias_dict = {v:k for k,li in rev_alias_list.items() for v in li}
    try:
        artist = alias_dict[artist]
    except:
        pass
    date = date_dict[date_type]
    connection = sqlite3.connect("Vocaloid.db")
    cursor = connection.cursor()
    if comparison_type != "increase":
        x_axis = [0]
        y_axis = [0]
        occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
        for occurence in occurences:
            if x_axis[-1] != occurence[0][:date]:
                x_axis.append(occurence[0][:date])
                if comparison_type == "per":
                    y_axis.append(occurence[1])
                elif comparison_type == "at":
                    y_axis.append(occurence[1] + y_axis[-1])
            else:
                y_axis[-1] += occurence[1]
    else:
        temp = [0]
        y_axis = [0]
        x_axis = [0]
        occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
        for occurence in occurences:
            if x_axis[-1] != occurence[0][:date]:
                x_axis.append(occurence[0][:date])
                temp.append(occurence[1])
            else:
                temp[-1] += occurence[1]
        for i in range(len(temp)):
            if i == 0:
                y_axis.append(temp[i])
            else:
                y_axis.append(temp[i] - temp[i - 1])
    connection.close()
    return x_axis[1:], y_axis[1:]

def get_song_views(songVID, comparison_type, date_type):
    
    date_dict = {v:k for k,li in rev_date_dict.items() for v in li}
    date = date_dict
    connection = sqlite3.connect("Views.db")
    cursor = connection.cursor()
    views = cursor.execute(f"SELECT Name, TotalViews, FROM Youtube WHERE VID IS {songVID}")
    if comparison_type != "increase":
        pass
        

@app.route("/songViews.json", methods = ["POST"])
def return_song_views():
    response = {
        'status': 200,
        'message': 'OK',
        'body': []
        }
    if request.json["type"] == "songs":
        for songVocaID in request.json["songsVocaIDs"]:
            match request.json["subtype"]:
                case "vpd":
                    pass

@app.route("/songAmounts.json", methods = ["POST"])
def return_song_amounts():
    response = {
        'status': 200,
        'message': 'OK',
        'body': []
        }
    for artist in request.json["artists"]:
        match request.json["subtype"]:
            case "spd":
                x_axis, y_axis = get_songs(artist, "per", "day")
            case "sam":
                x_axis, y_axis = get_songs(artist, "at", "month")
            case "spm":
                x_axis, y_axis = get_songs(artist, "per", "month")
            case "sim":
                x_axis, y_axis = get_songs(artist, "increase", "monthly")
            case "say":
                x_axis, y_axis = get_songs(artist, "at", "year")
            case "spy":
                x_axis, y_axis = get_songs(artist, "per", "year")
            case "siy":
                x_axis, y_axis = get_songs(artist, "increase", "yearly")
        response["body"].append({'x': x_axis,
                                 'y': y_axis,
                                 'mode': 'lines',
                                 'plot_bgcolor': 'aliceblue',
                                 'autosize': True})
    return jsonify(response)
    
@app.route("/")
def return_template():
    return render_template("main.html")