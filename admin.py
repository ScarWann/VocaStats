from views_handling import reinitialise_promotional_video_table, reinitialise_song_views_table, reinitialise_artist_views_table, daily_update
from artists_handling import reinit_artist_table, reinit_alias_table
from main_db import reinitialise_song_info_table, reinitialize_song_artists_table
from main_db import bulk_fetch_songs

print("""Admin commands:\n
      help           -- show this text\n
      exit           -- close this program\n
      update         -- update viewcount for all tracked songs that were not already updated\n
      fetch *Artist* -- fetch all songs by artist (by VocadbID)\n
      reinit *Table* -- reinitialises a table\n
      reinit -a      -- reinitialises every table\n""")
while True:
    user_input = input("")
    match user_input.split()[0]:
        case "help":
            print("""Admin commands:\n
                    help           -- show this text\n
                    exit           -- close this program\n
                    update         -- update viewcount for all tracked songs that were not already updated\n
                    fetch *Artist* -- fetch all songs by artist (by VocadbID)\n
                    reinit *Table* -- reinitialises a table\n
                    reinit -a      -- reinitialises every table\n""")
        case "exit":
            break
        case "update":
            daily_update()
        case "fetch":
            bulk_fetch_songs(int(user_input.split()[1]))
        case "reinit":
            match user_input.split()[1]:
                case "-a":
                    reinitialise_song_info_table()
                    reinitialize_song_artists_table()
                    reinit_artist_table()
                    reinit_alias_table()
                    reinitialise_song_views_table()
                    reinitialise_artist_views_table()
                    reinitialise_promotional_video_table()
    