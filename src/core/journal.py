from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from .mood_tracker import MoodEntry

@dataclass
class JournalEntry:
    """
    Represents a journal entry with associated mood and music information.
    This maps to the 'ADD JOURNAL ENTRY' section in your prototype.
    """
    mood_entry: MoodEntry
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Music-related fields
    liked_songs: List[Dict] = field(default_factory=list)  # List of Spotify track objects
    memorable_lyrics: List[str] = field(default_factory=list)
    playlist_feedback: Optional[str] = None
    
    # Tags for better organization and searching
    tags: List[str] = field(default_factory=list)
    
    def add_liked_song(self, track: Dict) -> None:
        """Add a song that resonated during this journaling session"""
        if track not in self.liked_songs:
            self.liked_songs.append(track)
    
    def add_memorable_lyrics(self, lyrics: str, song_title: str) -> None:
        """Add memorable lyrics with associated song"""
        self.memorable_lyrics.append({
            "lyrics": lyrics,
            "song": song_title,
            "timestamp": datetime.now()
        })
    
    def to_dict(self) -> Dict:
        """Convert journal entry to dictionary for storage"""
        return {
            "mood_data": self.mood_entry.to_dict(),
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "liked_songs": self.liked_songs,
            "memorable_lyrics": self.memorable_lyrics,
            "playlist_feedback": self.playlist_feedback,
            "tags": self.tags
        }

class JournalManager:
    """
    Manages journal entries and provides analysis capabilities.
    This handles the journal/music review functionality shown in your prototype.
    """
    def __init__(self):
        self.entries: List[JournalEntry] = []
        
    def add_entry(self, entry: JournalEntry) -> None:
        """Add a new journal entry"""
        self.entries.append(entry)
    
    def get_entries_by_date_range(self, 
                                start_date: datetime, 
                                end_date: Optional[datetime] = None) -> List[JournalEntry]:
        """Get all entries within a date range"""
        if end_date is None:
            end_date = datetime.now()
            
        return [
            entry for entry in self.entries 
            if start_date <= entry.timestamp <= end_date
        ]
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """
        Generate monthly summary of journal entries and music.
        This corresponds to the 'your music review' section in your prototype.
        """
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
            
        entries = self.get_entries_by_date_range(start_date, end_date)
        
        return {
            "total_entries": len(entries),
            "mood_distribution": self._calculate_mood_distribution(entries),
            "favorite_songs": self._get_top_songs(entries),
            "memorable_lyrics": self._collect_memorable_lyrics(entries),
            "common_themes": self._extract_common_themes(entries)
        }
    
    def _calculate_mood_distribution(self, entries: List[JournalEntry]) -> Dict:
        """Calculate mood distribution over entries"""
        distribution = {}
        for entry in entries:
            mood = entry.mood_entry.mood.name
            distribution[mood] = distribution.get(mood, 0) + 1
        return distribution
    
    def _get_top_songs(self, entries: List[JournalEntry], limit: int = 10) -> List[Dict]:
        """Get most liked songs across entries"""
        song_counts = {}
        for entry in entries:
            for song in entry.liked_songs:
                song_id = song['id']
                if song_id not in song_counts:
                    song_counts[song_id] = {'count': 0, 'song': song}
                song_counts[song_id]['count'] += 1
        
        # Sort by count and return top songs
        sorted_songs = sorted(
            song_counts.values(), 
            key=lambda x: x['count'], 
            reverse=True
        )
        return [item['song'] for item in sorted_songs[:limit]]
    
    def _collect_memorable_lyrics(self, entries: List[JournalEntry]) -> List[Dict]:
        """Collect all memorable lyrics from entries"""
        all_lyrics = []
        for entry in entries:
            all_lyrics.extend(entry.memorable_lyrics)
        return all_lyrics
    
    def _extract_common_themes(self, entries: List[JournalEntry]) -> Dict[str, int]:
        """
        Extract common themes/tags from journal entries
        This helps identify patterns in the user's emotional journey
        """
        theme_counts = {}
        for entry in entries:
            for tag in entry.tags:
                theme_counts[tag] = theme_counts.get(tag, 0) + 1
        return dict(sorted(
            theme_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )) 