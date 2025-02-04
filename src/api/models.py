from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class MoodEnum(str, Enum):
    """Available mood levels for tracking"""
    HAPPY = "HAPPY"
    CALM = "CALM"
    NEUTRAL = "NEUTRAL"
    TENSE = "TENSE"
    UPSET = "UPSET"

class IntentEnum(str, Enum):
    """User's intent for playlist generation"""
    IMPROVE = "improve"  # Generate uplifting music to improve mood
    RELATE = "relate"   # Generate music that relates to current mood

class MoodRequest(BaseModel):
    """
    Request model for recording user's mood
    """
    mood: MoodEnum = Field(..., description="User's current mood")
    context: Optional[str] = Field(None, 
        description="What is causing this mood? (e.g., 'work stress', 'exciting news')",
        max_length=500)
    activities: Optional[List[str]] = Field(default_factory=list,
        description="Activities associated with this mood")
    tags: Optional[List[str]] = Field(default_factory=list,
        description="Tags to categorize the mood entry")

    class Config:
        schema_extra = {
            "example": {
                "mood": "HAPPY",
                "context": "Got a promotion at work",
                "activities": ["working", "celebrating"],
                "tags": ["work", "achievement"]
            }
        }

class PlaylistRequest(BaseModel):
    """
    Request model for generating a mood-based playlist
    """
    mood_id: str = Field(..., description="ID of the mood entry to base playlist on")
    intent: IntentEnum = Field(..., 
        description="Whether to improve mood or relate to current mood")
    context: Optional[str] = Field(None, 
        description="Additional context for playlist generation")

    class Config:
        schema_extra = {
            "example": {
                "mood_id": "1234567890",
                "intent": "improve",
                "context": "Need energy for workout"
            }
        }

class SongInfo(BaseModel):
    """Information about a song"""
    id: str = Field(..., description="Spotify track ID")
    name: str = Field(..., description="Song name")
    artist: str = Field(..., description="Artist name")
    url: HttpUrl = Field(..., description="Spotify URL for the track")

class LyricEntry(BaseModel):
    """Memorable lyrics from a song"""
    text: str = Field(..., description="The lyric text")
    song: str = Field(..., description="Song title")
    artist: Optional[str] = Field(None, description="Artist name")

class JournalRequest(BaseModel):
    """
    Request model for saving a journal entry
    """
    mood_id: str = Field(..., description="ID of the associated mood entry")
    text: str = Field(..., 
        description="Journal entry text",
        min_length=1,
        max_length=5000)
    liked_songs: Optional[List[SongInfo]] = Field(default_factory=list,
        description="Songs that resonated during this session")
    memorable_lyrics: Optional[List[LyricEntry]] = Field(default_factory=list,
        description="Memorable lyrics from the playlist")
    tags: Optional[List[str]] = Field(default_factory=list,
        description="Tags for the journal entry")

    class Config:
        schema_extra = {
            "example": {
                "mood_id": "1234567890",
                "text": "Today was a great day...",
                "liked_songs": [{
                    "id": "spotify:track:123",
                    "name": "Happy",
                    "artist": "Pharrell Williams",
                    "url": "https://open.spotify.com/track/123"
                }],
                "memorable_lyrics": [{
                    "text": "Clap along if you feel...",
                    "song": "Happy",
                    "artist": "Pharrell Williams"
                }],
                "tags": ["grateful", "productive"]
            }
        }

class MonthlyReviewResponse(BaseModel):
    """
    Response model for monthly mood and music review
    """
    mood_trends: Dict = Field(..., 
        description="Distribution and trends of moods over the month")
    favorite_songs: List[SongInfo] = Field(...,
        description="Most liked/played songs for the month")
    memorable_lyrics: List[LyricEntry] = Field(...,
        description="Collection of saved lyrics")
    common_themes: Dict[str, int] = Field(...,
        description="Frequently occurring themes/tags with counts")

    class Config:
        schema_extra = {
            "example": {
                "mood_trends": {
                    "average_mood": 4.2,
                    "mood_distribution": {
                        "HAPPY": 15,
                        "CALM": 8,
                        "NEUTRAL": 5,
                        "TENSE": 2,
                        "UPSET": 0
                    }
                },
                "favorite_songs": [{
                    "id": "spotify:track:123",
                    "name": "Happy",
                    "artist": "Pharrell Williams",
                    "url": "https://open.spotify.com/track/123"
                }],
                "memorable_lyrics": [{
                    "text": "Clap along if you feel...",
                    "song": "Happy",
                    "artist": "Pharrell Williams"
                }],
                "common_themes": {
                    "work": 10,
                    "exercise": 8,
                    "family": 5
                }
            }
        } 