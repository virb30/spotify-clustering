import os
from extractor import SpotifyApi

client_id = os.environ.get('SPOTIFY_CLIENT_ID', '')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', '')

if __name__ == '__main__':
    spotify_api = SpotifyApi(client_id, client_secret)
    df = spotify_api.search_tracks('year:2020', size=1000)
    df.to_csv(os.path.join('spotify_data.csv'))