# DxTx API

FastAPI backend for the emotive AI voice agent.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (copy .env.example to .env and update)

3. Run database migrations:
```bash
alembic upgrade head
```

4. Start the API:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `POST /calls/outbound` - Initiate an outbound call
- `GET /calls` - List all calls
- `GET /calls/{call_id}` - Get call details
- `POST /calls/{call_id}/hangup` - Hang up a call
- `POST /webhooks/telnyx` - Telnyx webhook handler
- `POST /webhooks/transcription` - Transcription webhook handler
- `GET /transcripts/{call_id}` - Get call transcript
- `GET /health` - Health check
- `GET /stats` - Call statistics
