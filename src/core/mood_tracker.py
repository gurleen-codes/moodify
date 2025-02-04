from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass, field

class MoodLevel(Enum):
    HAPPY = 5
    CALM = 4
    NEUTRAL = 3
    TENSE = 2
    UPSET = 1

@dataclass
class MoodEntry:
    mood: MoodLevel
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)
    journal_entry: Optional['JournalEntry'] = None
    playlist_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert mood entry to dictionary for storage"""
        return {
            'mood': self.mood.name,
            'mood_value': self.mood.value,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'tags': self.tags,
            'activities': self.activities,
            'playlist_id': self.playlist_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MoodEntry':
        """Create MoodEntry from dictionary"""
        return cls(
            mood=MoodLevel[data['mood']],
            timestamp=datetime.fromisoformat(data['timestamp']),
            context=data.get('context'),
            tags=data.get('tags', []),
            activities=data.get('activities', []),
            playlist_id=data.get('playlist_id')
        )

class MoodTracker:
    def __init__(self):
        self.entries: List[MoodEntry] = []
        
    def add_entry(self, entry: MoodEntry) -> None:
        """Add a new mood entry"""
        self.entries.append(entry)
        
    def get_entries_by_date(self, 
                           start_date: datetime, 
                           end_date: Optional[datetime] = None) -> List[MoodEntry]:
        """Get mood entries within a date range"""
        if end_date is None:
            end_date = datetime.now()
            
        return [
            entry for entry in self.entries 
            if start_date <= entry.timestamp <= end_date
        ]
    
    def get_mood_trends(self, 
                       start_date: datetime, 
                       end_date: Optional[datetime] = None) -> Dict:
        """Calculate mood trends over time"""
        entries = self.get_entries_by_date(start_date, end_date)
        
        trends = {
            'average_mood': sum(e.mood.value for e in entries) / len(entries) if entries else 0,
            'mood_distribution': {mood.name: 0 for mood in MoodLevel},
            'common_contexts': {},
            'common_activities': {}
        }
        
        for entry in entries:
            trends['mood_distribution'][entry.mood.name] += 1
            
            if entry.context:
                trends['common_contexts'][entry.context] = \
                    trends['common_contexts'].get(entry.context, 0) + 1
                    
            for activity in entry.activities:
                trends['common_activities'][activity] = \
                    trends['common_activities'].get(activity, 0) + 1
        
        return trends 