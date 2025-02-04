# Moodify

A mood-based music recommendation and journaling application that helps users discover music based on their emotions and maintain a music-integrated mood journal.

## Features

- 🎭 Mood tracking with context and activities
- 🎵 Spotify-integrated playlist generation
- 📝 Music-integrated journaling
- 📊 Monthly mood and music analytics
- 🤝 Anonymous sharing of music discoveries

## Prerequisites

- Python 3.8+
- Spotify Developer Account
- PostgreSQL (optional, for production)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/moodify.git
cd moodify
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn pydantic spotipy python-dotenv
```

4. Set up Spotify:
- Create app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- Add `http://localhost:8000/callback` to Redirect URIs
- Copy Client ID and Secret

5. Create `.env` file:
```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8000/callback
```

6. Run the app:
```bash
uvicorn src.api.routes:app --reload
```

5. View API docs at:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Project Structure
```
moodify/
├── src/
│   ├── api/          # FastAPI routes & models
│   └── core/         # Business logic
├── .env              # Spotify credentials
└── requirements.txt  # Dependencies
```
