from typing import Dict, List
from .music_service import MusicService
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyService(MusicService):
    def __init__(self, credentials: Dict[str, str]):
        # Unpack credentials correctly for SpotifyOAuth
        auth_manager = SpotifyOAuth(
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            redirect_uri=credentials['redirect_uri'],
            scope='playlist-modify-public playlist-modify-private user-top-read'
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def generate_playlist(self, mood: str, intent: str) -> List[Dict]:
        # Basic implementation
        return []

    async def get_recommendations(self, mood: str) -> List[Dict]:
        # Map moods to audio features
        mood_features = {
            'HAPPY': {'valence': 0.8, 'energy': 0.8},
            'CALM': {'valence': 0.5, 'energy': 0.3},
            'NEUTRAL': {'valence': 0.5, 'energy': 0.5},
            'TENSE': {'valence': 0.3, 'energy': 0.7},
            'UPSET': {'valence': 0.2, 'energy': 0.5}
        }
        
        features = mood_features.get(mood, {'valence': 0.5, 'energy': 0.5})
        
        # Get recommendations from Spotify
        recommendations = self.sp.recommendations(
            seed_genres=['pop', 'rock'],
            target_valence=features['valence'],
            target_energy=features['energy'],
            limit=20
        )
        
        return recommendations['tracks']

    async def create_playlist(self, name: str, tracks: List[str]) -> str:
        # Create a new playlist
        user_id = self.sp.me()['id']
        playlist = self.sp.user_playlist_create(
            user_id,
            name,
            public=False,
            description=f"Moodify playlist for {name}"
        )
        
        # Add tracks to playlist
        if tracks:
            self.sp.playlist_add_items(playlist['id'], tracks)
            
        return playlist['id']

    async def get_track_info(self, track_id: str) -> Dict:
        track = self.sp.track(track_id)
        return {
            'id': track['id'],
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'url': track['external_urls']['spotify']
        }

class AppleMusicService(MusicService):
    def __init__(self, credentials: Dict[str, str]):
        self.client = AppleMusicClient(credentials)  # Apple Music SDK
    
    async def get_recommendations(self, mood: str) -> List[Dict]:
        # Apple Music-specific implementation
        pass 