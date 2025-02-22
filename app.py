import sqlite3
from flask import Flask, render_template, request, jsonify
from artists_handling import get_alias_holder_name

app = Flask(__name__)

def fetch_songs(artist, comparison_type, date_type):
    rev_date_dict = {4 : ["year", "years", "yearly"],
                     7 : ["month", "months", "monthly"],
                     10 : ["day", "days", "daily"]}
    
    date_dict = {v:k for k,li in rev_date_dict.items() for v in li}
    if not artist.isdigit():
        artist = get_alias_holder_name()

    try:
        artist = alias_dict[artist]
    except:
        pass
    date = date_dict[date_type]
    connection = sqlite3.connect("Vocaloid.db")
    cursor = connection.cursor()
    x_axis = [0]
    y_axis = [0]
    occurences = cursor.execute(f"SELECT ReleaseDate, count(*) as '' FROM (SELECT * FROM Songs WHERE Artist LIKE '{artist}') GROUP BY ReleaseDate").fetchall()
    if comparison_type != "increase":
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

@app.route("/songData.json", methods = ["POST"])
def return_songs_by_artist():
    response = {
        'status': 200,
        'message': 'OK',
        'body': []
        }
    for artist in request.json["artists"]:
        match request.json["subtype"]:
            case "spd":
                x_axis, y_axis = fetch_songs(artist, "per", "day")
            case "sam":
                x_axis, y_axis = fetch_songs(artist, "at", "month")
            case "spm":
                x_axis, y_axis = fetch_songs(artist, "per", "month")
            case "sim":
                x_axis, y_axis = fetch_songs(artist, "increase", "monthly")
            case "say":
                x_axis, y_axis = fetch_songs(artist, "at", "year")
            case "spy":
                x_axis, y_axis = fetch_songs(artist, "per", "year")
            case "siy":
                x_axis, y_axis = fetch_songs(artist, "increase", "yearly")
        response["body"].append({'x': x_axis,
                                 'y': y_axis,
                                 'mode': 'lines',
                                 'plot_bgcolor': 'pink'})
    return jsonify(response)
    
@app.route("/")
def return_template():
    return render_template("main.html")