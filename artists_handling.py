import requests
from app_decorators import connected

@connected
def reinit_artist_table(cursor = None):
    try:
        cursor.execute("DROP TABLE Artists")
    except:
        pass
    cursor.execute("CREATE TABLE Artists (VID int, Name nvarchar(255))")

@connected
def reinit_alias_table(cursor = None):
    try:
        cursor.execute("DROP TABLE Aliases")
    except:
        pass
    cursor.execute("CREATE TABLE Aliases (VID int, Alias nvarchar(255))")

@connected
def get_alias_holder_id(alias, cursor = None):
    holder = cursor.execute(f"SELECT VID FROM Aliases WHERE Alias LIKE '%{alias}%'").fetchall()
    if not holder:
        response = requests.get(f"https://vocadb.net/api/artists?query={alias}&allowBaseVoicebanks=true&childTags=false&start=0&maxResults=10&getTotalCount=false&sort=SongCount&preferAccurateMatches=false&nameMatchMode=Auto&fields=AdditionalNames")
        if response.json()["items"]:
            response = response.json()["items"][0]
            holder = response["id"]
            aliases = response["additionalNames"].split(", ")
            name = response["defaultName"]
            cursor.execute(f"INSERT INTO Artists (VID, Name) VALUES ({holder}, '{name}')")
            for alias in aliases:
                cursor.execute(f"INSERT INTO Aliases (VID, Alias) VALUES ({holder}, '{alias}')")
            return holder
        else:
            return None
    else:
        return holder[0][0]
    
@connected
def get_alias_holder_name(alias, cursor = None):
    holder_id = get_alias_holder_id(alias)
    if holder_id:
        holder_name = cursor.execute(f"SELECT Name FROM Artists WHERE VID LIKE '%{holder_id}%'").fetchone()
        if holder_name:
            return holder_name[0]
        else:
            return None
    else:
        return None

def main():
    print(get_alias_holder_name("Hatsune Miku"))

if __name__ == "__main__":
    main()