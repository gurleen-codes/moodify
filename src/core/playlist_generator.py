from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .mood_tracker import MoodLevel

class PlaylistGenerator:
    def __init__(self, spotify_credentials: Dict[str, str]):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(**spotify_credentials))
        
        # Mood to music attribute mappings
        self.mood_mappings = {
            MoodLevel.HAPPY: {
                'improve': {'valence': 0.8, 'energy': 0.8, 'tempo': (120, 140)},
                'relate': {'valence': 0.7, 'energy': 0.7, 'tempo': (110, 130)}
            },
            MoodLevel.CALM: {
                'improve': {'valence': 0.6, 'energy': 0.4, 'tempo': (70, 100)},
                'relate': {'valence': 0.5, 'energy': 0.3, 'tempo': (60, 90)}
            },
            MoodLevel.NEUTRAL: {
                'improve': {'valence': 0.6, 'energy': 0.6, 'tempo': (90, 120)},
                'relate': {'valence': 0.5, 'energy': 0.5, 'tempo': (80, 110)}
            },
            MoodLevel.TENSE: {
                'improve': {'valence': 0.7, 'energy': 0.4, 'tempo': (70, 100)},
                'relate': {'valence': 0.3, 'energy': 0.6, 'tempo': (90, 120)}
            },
            MoodLevel.UPSET: {
                'improve': {'valence': 0.8, 'energy': 0.5, 'tempo': (85, 110)},
                'relate': {'valence': 0.2, 'energy': 0.4, 'tempo': (60, 90)}
            }
        }

    def get_recommendations(self, mood: MoodLevel, intent: str, limit: int = 20) -> List[Dict]:
        """Get song recommendations based on mood and intent"""
        params = self.mood_mappings[mood][intent]
        
        # Get user's top tracks and artists for better recommendations
        top_tracks = self.sp.current_user_top_tracks(limit=5, time_range='short_term')
        top_artists = self.sp.current_user_top_artists(limit=5, time_range='short_term')
        
        seed_tracks = [track['id'] for track in top_tracks['items'][:2]]
        seed_artists = [artist['id'] for artist in top_artists['items'][:3]]
        
        recommendations = self.sp.recommendations(
            seed_tracks=seed_tracks,
            seed_artists=seed_artists,
            target_valence=params['valence'],
            target_energy=params['energy'],
            min_tempo=params['tempo'][0],
            max_tempo=params['tempo'][1],
            limit=limit
        )
        
        return recommendations['tracks']

    def create_playlist(self, 
                       user_id: str, 
                       mood_entry: 'MoodEntry', 
                       intent: str,
                       name: Optional[str] = None) -> str:
        """Create a new playlist based on mood and intent"""
        # Generate playlist name if not provided
        if not name:
            name = f"Moodify - {mood_entry.mood.name} - {intent.capitalize()}"
            if mood_entry.context:
                name += f" - {mood_entry.context[:30]}"
        
        # Create playlist
        playlist = self.sp.user_playlist_create(
            user_id,
            name,
            public=False,
            description=f"Created by Moodify for {mood_entry.mood.name} mood"
        )
        
        # Get recommendations and add to playlist
        tracks = self.get_recommendations(mood_entry.mood, intent)
        track_uris = [track['uri'] for track in tracks]
        
        self.sp.playlist_add_items(playlist['id'], track_uris)
        
        return playlist['id']

    def generate_playlist(self, mood_entry: 'MoodEntry', intent: str) -> List[Dict]:
        """
        Generate playlist based on mood and intent
        intent: 'improve' or 'relate'
        """
        # Implementation will use Spotify API to generate playlists
        # based on mood and whether user wants to improve or relate to their mood
        pass

    def save_playlist(self, user_id: str, tracks: List[str], name: str) -> str:
        """Save playlist to user's Spotify account"""
        pass 