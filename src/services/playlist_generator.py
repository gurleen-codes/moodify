from typing import List, Dict
from .music_service import MusicService
from ..api.models import MoodEnum, IntentEnum

class PlaylistGenerator:
    def __init__(self, music_service: MusicService):
        self.music_service = music_service
    
    async def generate_mood_playlist(
        self,
        mood: MoodEnum,
        intent: IntentEnum,
        context: str = None
    ) -> Dict:
        # Get recommendations
        tracks = await self.music_service.get_recommendations(mood)
        
        # Create playlist name
        playlist_name = f"Moodify - {mood}"
        if context:
            playlist_name += f" - {context[:30]}"
            
        # Create playlist
        playlist_id = await self.music_service.create_playlist(
            playlist_name,
            [track['id'] for track in tracks]
        )
        
        return {
            'playlist_id': playlist_id,
            'tracks': tracks,
            'mood': mood,
            'intent': intent
        } 