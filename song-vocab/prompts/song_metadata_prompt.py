SONG_METADATA_PROMPT = """
Based on the query and lyrics below, identify the song title and artist.

QUERY: {query}

LYRICS (excerpt): {lyrics_excerpt}...

Identify just the song title and artist name.
""" 