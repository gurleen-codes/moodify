from fastapi import FastAPI, HTTPException, Depends, Query, Request, Form
from typing import Dict, List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from .models import (
    MoodRequest, PlaylistRequest, JournalRequest, 
    MonthlyReviewResponse, IntentEnum, MoodEnum, MusicServiceEnum
)
from ..core.mood_tracker import MoodTracker, MoodEntry, MoodLevel
from ..core.playlist_generator import PlaylistGenerator
from ..core.journal import JournalManager, JournalEntry
from ..core.database import Database, Collections
from ..services.music_service import MusicService
from ..services.factory import MusicServiceFactory
import os
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv, set_key

app = FastAPI(title="Moodify API")

# Dependency to get database instance
async def get_db() -> AsyncIOMotorDatabase:
    return await Database.get_db()

# In-memory storage (replace with database in production)
mood_tracker = MoodTracker()
journal_manager = JournalManager()
playlist_generator = None  # Will be initialized with Spotify credentials

# Mount static files and templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

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
    await Database.connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await Database.close_db()

@app.get("/")
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "moods": ["HAPPY", "CALM", "NEUTRAL", "TENSE", "UPSET"]
        }
    )

@app.post("/mood")
async def create_mood_and_playlist(
    request: Request,
    mood: str = Form(...),
    context: str = Form(None),
    service_type: str = Form(...)
):
    """Handle mood submission and playlist generation"""
    try:
        # Create mood entry
        mood_request = MoodRequest(
            mood=mood,
            context=context
        )
        
        # Get service credentials
        credentials = {}
        if service_type == "spotify":
            credentials = {
                'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
                'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
                'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI')
            }
            service_enum = MusicServiceEnum.SPOTIFY
        else:
            credentials = {
                'key_id': os.getenv('APPLE_MUSIC_KEY_ID'),
                'team_id': os.getenv('APPLE_MUSIC_TEAM_ID'),
                'secret_key': os.getenv('APPLE_MUSIC_SECRET_KEY')
            }
            service_enum = MusicServiceEnum.APPLE_MUSIC
        
        # Generate playlist
        music_service = MusicServiceFactory.get_service(service_enum, credentials)
        generator = PlaylistGenerator(music_service)
        playlist = await generator.generate_mood_playlist(
            mood=mood,
            intent=IntentEnum.IMPROVE,
            context=context
        )
        
        return templates.TemplateResponse(
            "playlist.html",
            {
                "request": request,
                "playlist": playlist,
                "mood": mood
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/playlists")
async def create_mood_playlist(
    request: PlaylistRequest,
    service_type: MusicServiceEnum,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    try:
        # Get appropriate credentials based on service type
        if service_type == MusicServiceEnum.SPOTIFY:
            credentials = {
                'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
                'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
                'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI')
            }
        else:  # Apple Music
            credentials = {
                'key_id': os.getenv('APPLE_MUSIC_KEY_ID'),
                'team_id': os.getenv('APPLE_MUSIC_TEAM_ID'),
                'secret_key': os.getenv('APPLE_MUSIC_SECRET_KEY')
            }
        
        music_service = MusicServiceFactory.get_service(service_type, credentials)
        generator = PlaylistGenerator(music_service)
        
        playlist = await generator.generate_mood_playlist(
            mood=request.mood,
            intent=request.intent,
            context=request.context
        )
        
        await db[Collections.PLAYLISTS].insert_one({
            'mood_id': request.mood_id,
            'service_type': service_type,
            'playlist_data': playlist,
            'timestamp': datetime.now()
        })
        
        return playlist
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

@app.get("/moods")
async def get_moods(
    start_date: Optional[datetime] = Query(None, description="Filter moods from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter moods until this date"),
    mood_type: Optional[MoodEnum] = Query(None, description="Filter by specific mood"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(10, description="Number of entries to return", ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get mood entries with filtering options"""
    try:
        # Build query filter
        filter_query = {}
        if start_date or end_date:
            filter_query["timestamp"] = {}
            if start_date:
                filter_query["timestamp"]["$gte"] = start_date
            if end_date:
                filter_query["timestamp"]["$lte"] = end_date
        
        if mood_type:
            filter_query["mood"] = mood_type
            
        if tags:
            filter_query["tags"] = {"$in": tags}
            
        # Execute query
        cursor = db[Collections.MOODS].find(filter_query)
        cursor = cursor.sort("timestamp", -1).limit(limit)
        
        # Convert to list
        moods = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for mood in moods:
            mood["_id"] = str(mood["_id"])
            
        return {"moods": moods}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/moods/{mood_id}")
async def update_mood(
    mood_id: str,
    request: MoodRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update an existing mood entry"""
    try:
        update_data = {
            "$set": {
                "mood": request.mood,
                "context": request.context,
                "activities": request.activities,
                "tags": request.tags
            }
        }
        
        result = await db[Collections.MOODS].update_one(
            {"_id": ObjectId(mood_id)},
            update_data
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Mood not found")
            
        return {
            "status": "success",
            "mood_id": mood_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/moods/{mood_id}")
async def delete_mood(
    mood_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a mood entry"""
    try:
        result = await db[Collections.MOODS].delete_one({"_id": ObjectId(mood_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Mood not found")
            
        return {
            "status": "success",
            "message": f"Mood entry {mood_id} deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/moods/{mood_id}")
async def get_mood(
    mood_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get a specific mood entry"""
    try:
        mood = await db[Collections.MOODS].find_one({"_id": ObjectId(mood_id)})
        if not mood:
            raise HTTPException(status_code=404, detail="Mood not found")
            
        mood["_id"] = str(mood["_id"])
        return mood
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/setup")
async def setup_page(request: Request):
    """Show the setup page"""
    return templates.TemplateResponse(
        "setup.html",
        {"request": request}
    )

@app.post("/setup/spotify")
async def setup_spotify(
    request: Request,
    client_id: str = Form(...),
    client_secret: str = Form(...)
):
    """Save Spotify credentials"""
    try:
        # Update .env file
        env_path = os.path.join(os.path.dirname(BASE_DIR), '.env')
        
        # Set the new values
        set_key(env_path, 'SPOTIFY_CLIENT_ID', client_id)
        set_key(env_path, 'SPOTIFY_CLIENT_SECRET', client_secret)
        
        # Reload environment variables
        load_dotenv(env_path, override=True)
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "moods": ["HAPPY", "CALM", "NEUTRAL", "TENSE", "UPSET"],
                "message": "Spotify credentials saved successfully!"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save credentials: {str(e)}"
        )