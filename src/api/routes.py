from fastapi import FastAPI, HTTPException, Depends
from typing import Dict, List
from datetime import datetime
from .models import (
    MoodRequest, PlaylistRequest, JournalRequest, 
    MonthlyReviewResponse, IntentEnum
)
from ..core.mood_tracker import MoodTracker, MoodEntry, MoodLevel
from ..core.playlist_generator import PlaylistGenerator
from ..core.journal import JournalManager, JournalEntry

app = FastAPI(title="Moodify API")

# In-memory storage (replace with database in production)
mood_tracker = MoodTracker()
journal_manager = JournalManager()
playlist_generator = None  # Will be initialized with Spotify credentials

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global playlist_generator
    # Load Spotify credentials from environment variables or config
    spotify_credentials = {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "redirect_uri": "your_redirect_uri",
        "scope": "playlist-modify-private playlist-modify-public user-top-read"
    }
    playlist_generator = PlaylistGenerator(spotify_credentials)

@app.post("/mood", response_model=Dict)
async def record_mood(request: MoodRequest):
    """
    Record user's current mood
    This corresponds to the first screen in your prototype
    """
    try:
        mood_entry = MoodEntry(
            mood=MoodLevel[request.mood],
            context=request.context,
            activities=request.activities,
            tags=request.tags
        )
        mood_tracker.add_entry(mood_entry)
        return {"mood_id": str(mood_entry.timestamp.timestamp())}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-playlist")
async def generate_playlist(request: PlaylistRequest):
    """
    Generate playlist based on mood and intent
    This handles the 'improve mood' vs 'relate to mood' choice
    """
    try:
        # Find the mood entry
        entries = [e for e in mood_tracker.entries 
                  if str(e.timestamp.timestamp()) == request.mood_id]
        if not entries:
            raise HTTPException(status_code=404, detail="Mood entry not found")
        
        mood_entry = entries[0]
        playlist_id = playlist_generator.create_playlist(
            user_id="user_id",  # Get from auth
            mood_entry=mood_entry,
            intent=request.intent
        )
        
        # Update mood entry with playlist
        mood_entry.playlist_id = playlist_id
        
        return {
            "playlist_id": playlist_id,
            "mood": mood_entry.mood.name,
            "intent": request.intent
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/journal")
async def save_journal(request: JournalRequest):
    """
    Save journal entry with associated mood and music
    This handles the journaling feature shown in your prototype
    """
    try:
        # Find the mood entry
        entries = [e for e in mood_tracker.entries 
                  if str(e.timestamp.timestamp()) == request.mood_id]
        if not entries:
            raise HTTPException(status_code=404, detail="Mood entry not found")
        
        journal_entry = JournalEntry(
            mood_entry=entries[0],
            text=request.text,
            tags=request.tags or []
        )
        
        # Add any liked songs or memorable lyrics
        for song in request.liked_songs or []:
            journal_entry.add_liked_song(song)
        
        for lyric in request.memorable_lyrics or []:
            journal_entry.add_memorable_lyrics(
                lyrics=lyric["text"],
                song_title=lyric["song"]
            )
        
        journal_manager.add_entry(journal_entry)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/monthly-review/{year}/{month}", response_model=MonthlyReviewResponse)
async def get_monthly_review(year: int, month: int):
    """
    Get monthly mood and music review
    This generates the monthly review visualization shown in your prototype
    """
    try:
        summary = journal_manager.get_monthly_summary(year, month)
        return MonthlyReviewResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/share/{entry_id}")
async def share_entry(entry_id: str):
    """
    Share a journal entry anonymously
    This implements the sharing functionality shown in your prototype
    """
    try:
        # Find the journal entry
        entries = [e for e in journal_manager.entries 
                  if str(e.timestamp.timestamp()) == entry_id]
        if not entries:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        entry = entries[0]
        # Create anonymized version for sharing
        shared_data = {
            "mood": entry.mood_entry.mood.name,
            "liked_songs": entry.liked_songs,
            "memorable_lyrics": entry.memorable_lyrics,
            "tags": entry.tags
        }
        return shared_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 