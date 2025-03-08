from flask import Flask, render_template, request, jsonify
from song_handling import fetch_songs
from views_handling import fetch_views

app = Flask(__name__)

@app.route("/songAmounts.json", methods = ["POST"])
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

@app.route("/viewsAmounts.json", methods = ["POST"])
def return_views():
    response = {
        'status': 200,
        'message': 'OK',
        'body': []
        }
    x_axis, y_axis = fetch_views(request.json["songs"])[0]
    response["body"].append({'x': x_axis,
                                'y': y_axis,
                                'mode': 'lines',
                                'plot_bgcolor': 'pink'})
    return jsonify(response)
    
@app.route("/")
def return_template():
    return render_template("main.html")