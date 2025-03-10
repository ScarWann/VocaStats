from artists_handling import get_alias_holder_name, get_alias_holder_id
from app_decorators import connected

@connected
def fetch_songs(artist, comparison_type, date_type, cursor = None):
    rev_date_dict = {4 : ["year", "years", "yearly"],
                     7 : ["month", "months", "monthly"],
                     10 : ["day", "days", "daily"]}
    
    date_dict = {v:k for k,li in rev_date_dict.items() for v in li}
    if not artist.isdigit():
        temp = get_alias_holder_name(artist)
        print(temp)
        if temp != None:
            artist = temp
    date = date_dict[date_type]
    x_axis = [0]
    y_axis = [0]
    print(artist)
    occurences = cursor.execute(f"SELECT SongReleaseDate, count(*) AS '' FROM (SELECT * FROM SongArtists WHERE ArtistName LIKE '%{artist}%') GROUP BY SongReleaseDate").fetchall()
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
    return x_axis[1:], y_axis[1:]