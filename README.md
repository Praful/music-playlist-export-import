# music-playlist-export-import

Export playlist from one web source and import them to YouTube Music.

The export scripts generate a CSV file (tab-separated) with columns: `Artist`, `Song`. These are used by the import script.

All scripts have a `--help` switch, eg

`python spotify_playlist_export.py --help`

There are several scripts:

## bbc_playlist_export.py

This scrapes a specific playlist from the BBC website. 

In practice, you'll have to create your own export playlist function. The `bbc_playlist_export.py` gives two examples of scraping website data: one using a dynamic website and the other using a static website.

## spotify_playlist_export.py

This exports a playlist from Spotify. This uses the  [unofficial spotipy API](https://spotipy.readthedocs.io/). I use the [Client Creditials Flow](https://spotipy.readthedocs.io/en/2.22.0/#client-credentials-flow). You'll need to generate a Spotify Client Id and Client Secret to use the API from the [Spotify Developer website](https://developer.spotify.com/dashboard/applications).


Use the URL of the playlist you want to export from a browser. For example: 
```
python .\spotify_playlist_export.py --csv reading-chill-out.csv --url https://open.spotify.com/playlist/37i9dQZF1DWXrDQedVqw6q
```

## youtube_music_import.py


This uses the [unofficial YouTube Music API](https://ytmusicapi.readthedocs.io/en/stable/index.html) to import a CSV playlist into YouTube Music. That documentation describes how to connect your Python script to YouTube Music and install the API on your computer.

Here's an example of running the import into YouTube Music using the output from the Spotify export above:

 ```
 python .\youtube_music_import.py --csv .\reading-chill-out.csv --name 'Reading Chill Out' --description 'Calm music to help you focus on your reading (imported from Spotify)'
 ```