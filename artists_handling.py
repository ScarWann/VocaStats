from sqlite3 import connect
import requests

def init():
    connection = connect("Vocaloid.db")
    cursor = connection.cursor()
    cursor.execute("DROP TABLE Artists")
    cursor.execute("DROP TABLE Aliases")
    cursor.execute("CREATE TABLE Artists (VID int, Name nvarchar(255))")
    cursor.execute("CREATE TABLE Aliases (VID int, Alias nvarchar(255))")
    cursor.close()
    connection.commit()
    connection.close()

def get_alias_holder_id(alias):
    connection = connect("Vocaloid.db")
    cursor = connection.cursor()
    holder = cursor.execute(f"SELECT VID FROM Aliases WHERE Alias LIKE '%{alias}%'").fetchall()
    if not holder:
        response = requests.get(f"https://vocadb.net/api/artists?query={alias}&allowBaseVoicebanks=true&childTags=false&start=0&maxResults=1&getTotalCount=false&preferAccurateMatches=true&fields=AdditionalNames")
        response = response.json()["items"][0]
        if response:
            holder = response["id"]
            aliases = response["additionalNames"].split(", ")
            name = response["defaultName"]
            cursor.execute(f"INSERT INTO Artists (VID, Name) VALUES ({holder}, '{name}')")
            for alias in aliases:
                cursor.execute(f"INSERT INTO Aliases (VID, Alias) VALUES ({holder}, '{alias}')")
            cursor.close()
            connection.commit()
            connection.close()
            return holder
        else:
            cursor.close()
            connection.commit()
            connection.close()
            return None
    else:
        cursor.close()
        connection.commit()
        connection.close()
        return holder[0][0]
    
def get_alias_holder_name(alias):
    connection = connect("Vocaloid.db")
    cursor = connection.cursor()
    holder_id = get_alias_holder_id(alias)
    if holder_id:
        holder_name = cursor.execute(f"SELECT Name FROM Artists WHERE VID LIKE '%{holder_id}%'").fetchone()
        if holder_name:
            cursor.close()
            connection.commit()
            connection.close()
            return holder_name[0]
        else:
            cursor.close()
            connection.commit()
            connection.close()
            return None
    else:
        cursor.close()
        connection.commit()
        connection.close()
        return None

init()
print(get_alias_holder_name("Hatsune Miku"))