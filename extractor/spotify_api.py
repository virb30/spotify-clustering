import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

class MaximumValue(Exception):
    pass


MAX_LIMIT = 50
MAX_SIZE = 1000

class SpotifyApi:
    def __init__(self, client_id, client_secret):
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def search_tracks(self, q, type='track', limit=MAX_LIMIT, size=MAX_SIZE, unique=True):
        artist_name = []
        track_name = []
        popularity = []
        track_id = []

        if limit > MAX_LIMIT:
            raise MaximumValue(f'limit value must be less than or equal {MAX_LIMIT}')

        if size > MAX_SIZE:
            raise MaximumValue(f'size value must be less than or equal {MAX_SIZE}')

        for i in range(0, size, limit):
            track_results = self.sp.search(q=q, type=type, limit=limit, offset=i)
            for j, t in enumerate(track_results['tracks']['items']):
                artist_name.append(t['artists'][0]['name'])
                track_name.append(t['name'])
                track_id.append(t['id'])
                popularity.append(t['popularity'])

        df_tracks = pd.DataFrame({
            'artist_name': artist_name,
            'track_name': track_name,
            'track_id': track_id,
            'popularity': popularity
        })

        if unique:
            df_tracks = self.remove_duplicates(df_tracks)

        df_audio_features = self.get_audio_features(df_tracks)
        df = pd.merge(df_tracks, df_audio_features, on='track_id', how='inner')
        df[df.duplicated(subset=['artist_name', 'track_name'], keep=False)]
        return df

    def get_audio_features(self, df, batchsize=100):
        rows = []
        None_counter = 0

        for i in range(0, len(df['track_id']), batchsize):
            batch = df['track_id'][i:i + batchsize]
            feature_results = self.sp.audio_features(batch)
            for j, t in enumerate(feature_results):
                if t is None:
                    None_counter += 1
                else:
                    rows.append(t)

        df_audio_features = pd.DataFrame.from_dict(rows, orient='columns')
        columns_to_drop = ['analysis_url', 'track_href', 'type', 'uri']
        df_audio_features.drop(columns_to_drop, axis=1, inplace=True)
        df_audio_features.rename(columns={'id': 'track_id'}, inplace=True)

        return df_audio_features

    @staticmethod
    def check_duplicates(df):
        grouped = df.groupby(['artist_name', 'track_name'], as_index=True).size()
        assert grouped[grouped > 1].count() == 0

    def remove_duplicates(self, df, subset=['artist_name', 'track_name']):
        try:
            self.check_duplicates(df)
        except AssertionError:
            df.drop_duplicates(subset=subset, inplace=True)
            self.check_duplicates(df)

        return df