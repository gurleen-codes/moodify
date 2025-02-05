from abc import ABC, abstractmethod
from typing import Dict, List

class MusicService(ABC):
    @abstractmethod
    def __init__(self, credentials: Dict):
        pass

    @abstractmethod
    def generate_playlist(self, mood: str, intent: str) -> List[Dict]:
        pass

    @abstractmethod
    async def get_recommendations(self, mood: str) -> List[Dict]:
        pass
        
    @abstractmethod
    async def create_playlist(self, name: str, tracks: List[str]) -> str:
        pass

    @abstractmethod
    async def get_track_info(self, track_id: str) -> Dict:
        pass 