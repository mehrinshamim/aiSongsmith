# aiSongsmith
aiSongsmith analyzes your Spotify listening habits to understand your music preferences and emotional connection to songs. It provides personalized insights and mood-based song recommendations, creating an immersive, interactive music experience.


base
- recommend songs basedon mood/context according to your Spotify Taste profile
- play a song
- show/open up lyrics to that song while playing


endpoints
- /play-song/{songid}
- /list-recommendations //hardcoded list for now
-/open-lyrics

database
- store user info
    - spotify login info
    - taste profile should be fetched (/or the song playlist) everytime recommendation is asked

-temporary song storage
    no need of that atm

- History
    context : text
    song_list : List[song_details]
    user_id : uuid FK to profiles

- song_details: 
    song name
    artist(s)
    lyrics
    you like the song?
    order no in list
    context_id 
    ,userid(wont be needed cz context_id is there, which is connected to user_id)

- profiles
    user_id : UUID
    fname : text
    name : text
    //spotify login info/credentials