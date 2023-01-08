# music-playlist-export-import

Export playlist from one web source and import them to YouTube Music. The initial version scrapes a playlist from the BBC website and uses the [unofficial YouTube Music API](https://ytmusicapi.readthedocs.io/en/stable/index.html) to import the playlist into YouTube Music. That documentation describes how to connect your Python script to YouTube Music and install the API on your computer.

In practice, you'll have to create your own export playlist function. The `bbc_playlist_export.py` gives two examples of scraping website data: one using a dynamic webstite and the other using a static website.
