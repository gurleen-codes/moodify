from typing import Dict, List
from applemusicpy import AppleMusic
from .music_service import MusicService

class AppleMusicService(MusicService):
    def __init__(self, credentials: Dict[str, str]):
        self.am = AppleMusic(
            secret_key=credentials['secret_key'],
            key_id=credentials['key_id'],
            team_id=credentials['team_id']
        )
        
    async def get_recommendations(self, mood: str) -> List[Dict]:
        # Map moods to Apple Music genres and attributes
        mood_mappings = {
            'HAPPY': ['pop', 'dance'],
            'CALM': ['ambient', 'classical'],
            'NEUTRAL': ['pop', 'rock'],
            'TENSE': ['alternative', 'rock'],
            'UPSET': ['blues', 'alternative']
        }
        
        genres = mood_mappings.get(mood, ['pop'])
        
        # Get recommendations from Apple Music
        recommendations = []
        for genre in genres:
            results = self.am.search(genre, types=['songs'], limit=10)
            if 'songs' in results:
                recommendations.extend(results['songs']['data'])
        
        # Format tracks to match common structure
        return [{
            'id': track['id'],
            'name': track['attributes']['name'],
            'artist': track['attributes']['artistName'],
            'url': track['attributes']['url']
        } for track in recommendations[:20]]

    async def create_playlist(self, name: str, tracks: List[str]) -> str:
        # Create a new playlist in Apple Music
        playlist = self.am.create_playlist(
            name=name,
            description=f"Moodify playlist for {name}",
            track_ids=tracks
        )
        
        return playlist['id']

    async def get_track_info(self, track_id: str) -> Dict:
        track = self.am.song(track_id)
        return {
            'id': track['id'],
            'name': track['attributes']['name'],
            'artist': track['attributes']['artistName'],
            'url': track['attributes']['url']
        } 