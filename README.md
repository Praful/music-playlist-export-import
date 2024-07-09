# music-playlist-export-import

Export playlist from one web source and import them to YouTube Music.

The export scripts generate a CSV file (tab-separated) with columns: `Artist`, `Song`. These are used by the import script.

All scripts have a `--help` switch, eg

`python spotify_playlist_export.py --help`

When creating a new playlist (in the import scripts), a number of attempts are made to find the song. Sometimes, however, nothing is found. This may be because the song doesn't exist on the platform. I've also found that sometimes there are typos in the song title or artist on the platform from which the playlist was exported. You always have the option of manually adding tracks that could not be imported from the website or app.

You'll need some extra Python libraries, which can be installed using `pip`. From the top level directory, run:

```
pip install -r requirements.txt
```


When calling some of the scripts, depending on your operating system and settings, you may need to use a single quote for the URLs eg `--url 'https:/....'`.

There are several scripts:

### bbc_playlist_export.py

This scrapes a specific playlist from the BBC website. 

In practice, you'll have to create your own export playlist function. The `bbc_playlist_export.py` gives two examples of scraping website data: one using a dynamic website and the other using a static website.

### spotify_playlist_export.py

This exports a playlist from Spotify. This uses the  [unofficial spotipy API](https://spotipy.readthedocs.io/). I use the [Authorization Code Flow](https://spotipy.readthedocs.io/en/2.22.0/#authorization-code-flow). You'll need to generate a Spotify Client Id and Client Secret to use the API from the [Spotify Developer website](https://developer.spotify.com/dashboard/applications) and add a URL to redirect to. This can be anything. I use http://localhost. Once authenticated, copy the browser URL (starting http://localhost/?code...) to the prompt when running this script.

For exporting Spotify playlists, the Client Credentials Flow can be used. However, this can't be used for modifying user data, such as creating a playlist. To simplify the code, I use the same method for exporting and importing.

Once you have generated your Spotify client id and secret, set them using environment variables before running the script. For example (in Linux bash/zsh):
```
export SPOTIPY_CLIENT_ID='12345'
export SPOTIPY_CLIENT_SECRET='ABCD'
export SPOTIPY_REDIRECT_URI='127.0.0.1'
```
For Windows PowerShell, see [here](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/set_1).

Use the URL of the playlist you want to export from a browser. For example: 
```
python ./spotify_playlist_export.py --csv reading-chill-out.csv --url https://open.spotify.com/playlist/37i9dQZF1DWXrDQedVqw6q
```

### spotify_playlist_import.py

Imports playlist into Spotify for CSV file. Example:

```
python ./spotify_playlist_import.py --csv ./example1.csv --name 'test' --description 'Imported from YouTube Music'
```

### youtube_music_import.py


This uses the [unofficial YouTube Music API](https://ytmusicapi.readthedocs.io/en/stable/index.html) to import a CSV playlist into YouTube Music. That documentation describes how to connect your Python script to YouTube Music and install the API on your computer.

To save a playlist, you must provide credentials. Run
```
ytmusicapi browser --file headers_auth.json
```
and paste in the header from your browser once you've logged into YouTube Music. Copy the POST authentication headers from the browser so that the pasted credentials are saved in file `headers_auth.json`. To find the credentials in your browser, see [here](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html#copy-authentication-headers).

You can also create this file manually as described [here](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html#manual-file-creation).

Here's an example of running the import into YouTube Music using the output from the Spotify export above:

 ```
 python ./youtube_music_import.py --csv ./reading-chill-out.csv --name 'Reading Chill Out' --description 'Calm music to help you focus on your reading (imported from Spotify)'
 ```

### youtube_music_export.py

Exports a YouTube Music playlist. Use the URL of the playlist in the browser to specify which playlist to export. Example:

```
python ./youtube_music_export.py --url https://music.youtube.com/playlist?list=RDCLAK5uy_n1quIxbUdCfJDCklZQxyss75yUKLp1oMQ --csv example1.csv
```
