from typing import Dict
from .music_service import MusicService
from .spotify_service import SpotifyService
# Comment out this line for now
# from .apple_music_service import AppleMusicService
from ..api.models import MusicServiceEnum

class MusicServiceFactory:
    @staticmethod
    def get_service(service_type: MusicServiceEnum, credentials: Dict) -> MusicService:
        if service_type == MusicServiceEnum.SPOTIFY:
            return SpotifyService(credentials)
        # Comment out this block for now
        # elif service_type == MusicServiceEnum.APPLE_MUSIC:
        #     return AppleMusicService(credentials)
        else:
            raise ValueError("Only Spotify is supported currently") 