# DxTx - Emotive AI Voice Agent for Patient Intake

A HIPAA-compliant AI voice agent system for medical patient intake with real-time transcription, empathetic dialogue, and structured clinical workflows.

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (TypeScript/React)
- **Database**: PostgreSQL
- **Caching/Sessions**: Redis
- **Telephony**: Telnyx WebRTC
- **Transcription**: TwinMind (primary), Deepgram (fallback)
- **Text-to-Speech**: ElevenLabs (primary), Deepgram (fallback)
- **LLM**: OpenAI GPT-4

### Directory Structure
```
DxTx/
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── models/        # Database models and schemas
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # External service integrations
│   │   ├── middleware/    # HIPAA audit logging, security
│   │   ├── config.py      # Configuration management
│   │   ├── database.py    # Database connection
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── web/                   # Next.js dashboard
│   ├── app/              # Next.js 14 App Router
│   ├── components/       # React components
│   ├── package.json
│   └── Dockerfile
├── agents/               # AI agent logic
│   ├── state_machine.py  # Conversation flow state machine
│   └── empathetic_agent.py  # LLM-powered empathetic dialogue
├── telephony/            # Telephony integrations
│   └── telnyx_service.py # Telnyx WebRTC handlers
├── docker-compose.yml    # Docker orchestration
└── .env.example         # Environment variables template
```

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- PostgreSQL 15+
- Redis 7+

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone https://github.com/wildhash/DxTx.git
cd DxTx
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the applications**
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development

#### Backend (FastAPI)
```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend (Next.js)
```bash
cd web
npm install
npm run dev
```

## 🔑 Configuration

Required environment variables (see `.env.example`):

### Telephony
- `TELNYX_API_KEY` - Telnyx API key
- `TELNYX_APP_ID` - Telnyx application ID
- `TELNYX_PHONE_NUMBER` - Your Telnyx phone number

### Transcription
- `TWINMIND_API_KEY` - TwinMind transcription API key
- `DEEPGRAM_API_KEY` - Deepgram API key (fallback)

### Text-to-Speech
- `ELEVENLABS_API_KEY` - ElevenLabs API key
- `ELEVENLABS_VOICE_ID` - Voice ID for synthesis

### AI/LLM
- `OPENAI_API_KEY` - OpenAI API key for GPT-4

### Security
- `API_SECRET_KEY` - Secret key for API security
- `ENCRYPTION_KEY` - 32+ character key for data encryption
- `NEXTAUTH_SECRET` - NextAuth session secret

## 🏥 Features

### Call Management
- **Outbound Calls**: Initiate calls to patients for intake
- **Inbound Calls**: Handle incoming patient calls
- **Real-time Status**: Track call status (initiated, ringing, answered, completed)
- **Call Controls**: Hang up, record, manage active calls

### AI-Powered Conversation
- **State Machine**: Structured conversation flow for patient intake
- **Empathetic Dialogue**: LLM-powered responses that show empathy
- **Information Extraction**: Automatically extract structured data
- **Sentiment Detection**: Monitor patient emotional state
- **Context Awareness**: Maintain conversation context throughout

### Real-time Transcription
- **Dual Service**: TwinMind primary, Deepgram fallback
- **Speaker Diarization**: Distinguish between agent and patient
- **Live Updates**: Real-time transcript streaming
- **Confidence Scoring**: Track transcription accuracy

### Voice Synthesis
- **Natural Voice**: ElevenLabs for human-like speech
- **Fallback TTS**: Deepgram for reliability
- **Empathetic Tone**: Voice adjusts to patient sentiment

### Dashboard Features
- **Call History**: View all past and active calls
- **Live Monitoring**: Real-time call status updates
- **Transcripts**: View full conversation transcripts
- **AI Summaries**: Automated clinical summaries
- **Statistics**: Call metrics and analytics
- **Workflow Controls**: Initiate calls, manage active sessions

### HIPAA Compliance
- **Audit Logging**: All actions logged with timestamps
- **Data Encryption**: Sensitive data encrypted at rest
- **Access Controls**: Role-based access (with NextAuth)
- **Data Retention**: Configurable retention policies
- **Secure Communication**: HTTPS/WSS only

## 📡 API Endpoints

### Calls
- `POST /calls/outbound` - Initiate outbound call
- `GET /calls` - List calls (with filtering)
- `GET /calls/{call_id}` - Get call details
- `POST /calls/{call_id}/hangup` - End active call

### Webhooks
- `POST /webhooks/telnyx` - Telnyx event handler
- `POST /webhooks/transcription` - Transcription updates

### Transcripts
- `GET /transcripts/{call_id}` - Get call transcript

### Monitoring
- `GET /health` - Health check
- `GET /stats` - Call statistics

## 🔄 Conversation Flow

The AI agent follows a structured patient intake flow:

1. **Greeting** - Warm introduction
2. **Name Collection** - Get patient's full name
3. **Date of Birth** - Verify patient identity
4. **Reason for Visit** - Chief complaint
5. **Symptoms** - Detailed symptom description
6. **Medical History** - Existing conditions
7. **Medications** - Current medications
8. **Allergies** - Known allergies
9. **Insurance** - Insurance information
10. **Confirmation** - Review collected data
11. **Closing** - Thank patient, final questions

## 🧪 Testing

```bash
# Backend tests
cd api
pytest

# Frontend tests
cd web
npm test
```

## 📊 Monitoring & Logs

- Application logs: Check Docker logs or API log files
- Audit logs: Stored in `audit_logs` table
- Call metrics: Available via `/stats` endpoint
- Health checks: `/health` endpoint for monitoring

## 🔒 Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Rotate keys regularly** - Especially encryption keys
3. **Enable HTTPS** - Use SSL certificates in production
4. **Review audit logs** - Monitor for suspicious activity
5. **Update dependencies** - Keep packages up to date
6. **Backup database** - Regular automated backups

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions, please open a GitHub issue or contact the development team.

## 🎯 Roadmap

- [ ] NextAuth integration for user authentication
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Call recording playback
- [ ] SMS notifications
- [ ] EHR integration
- [ ] Custom conversation flows
- [ ] Voice biometrics
