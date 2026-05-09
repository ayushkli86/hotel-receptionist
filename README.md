# Hotel AI Receptionist

AI-powered hotel receptionist with FastAPI backend, PostgreSQL, and terminal kiosk.

## Setup

```bash
cd C:\Projects\hotel-receptionist
pip install -r requirements.txt
copy .env.example .env        # then fill in your keys
```

## Run

**Backend:**
```bash
uvicorn app.main:app --reload
```

**Terminal Kiosk:**
```bash
python kiosk/kiosk.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/rooms | List rooms (filter by ?status=available) |
| POST | /api/guests | Register guest |
| POST | /api/bookings | Create booking |
| POST | /api/bookings/{id}/checkin | Check in guest |
| POST | /api/bookings/{id}/checkout | Check out guest |
| POST | /api/service | Log service request |
| POST | /api/chat | AI chat endpoint |

## Requirements
- Python 3.11+
- PostgreSQL running locally
- OpenAI API key
