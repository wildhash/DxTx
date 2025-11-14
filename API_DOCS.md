# API Documentation

## Overview

DxTx API provides RESTful endpoints for managing AI voice agent calls, transcripts, and patient intake workflows.

**Base URL**: `http://localhost:8000` (development) or `https://api.your-domain.com` (production)

**Interactive Documentation**: Visit `/docs` for Swagger UI or `/redoc` for ReDoc

## Authentication

Currently, the API uses API keys for authentication (NextAuth integration pending).

For protected endpoints, include the API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health & Monitoring

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "DxTx API",
  "version": "1.0.0"
}
```

#### GET /stats
Get call statistics.

**Response:**
```json
{
  "total_calls": 150,
  "active_calls": 3,
  "completed_calls": 142,
  "failed_calls": 5
}
```

### Calls

#### POST /calls/outbound
Initiate an outbound call to a patient.

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "patient_name": "John Doe",
  "context": {
    "appointment_id": "apt_12345",
    "reason": "pre-appointment intake"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "call_id": "550e8400-e29b-41d4-a716-446655440000",
  "direction": "outbound",
  "status": "initiated",
  "phone_number": "+1234567890",
  "patient_name": "John Doe",
  "started_at": "2024-01-15T10:30:00Z",
  "answered_at": null,
  "ended_at": null,
  "duration_seconds": null,
  "transcript": null,
  "ai_summary": null,
  "extracted_data": null
}
```

#### GET /calls
List all calls with optional filtering.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100)
- `status` (string): Filter by status (initiated, ringing, answered, in_progress, completed, failed, cancelled)

**Response:**
```json
[
  {
    "id": 1,
    "call_id": "550e8400-e29b-41d4-a716-446655440000",
    "direction": "outbound",
    "status": "completed",
    "phone_number": "+1234567890",
    "patient_name": "John Doe",
    "started_at": "2024-01-15T10:30:00Z",
    "answered_at": "2024-01-15T10:30:15Z",
    "ended_at": "2024-01-15T10:35:20Z",
    "duration_seconds": 305,
    "transcript": "Full conversation transcript...",
    "ai_summary": "Patient John Doe called for...",
    "extracted_data": {
      "name": "John Doe",
      "dob": "01/15/1980",
      "reason": "Annual checkup",
      "symptoms": "None reported",
      "medications": "None",
      "allergies": "None"
    }
  }
]
```

#### GET /calls/{call_id}
Get details of a specific call.

**Path Parameters:**
- `call_id` (string): The unique call identifier

**Response:**
Same as individual call object above.

#### POST /calls/{call_id}/hangup
End an active call.

**Path Parameters:**
- `call_id` (string): The unique call identifier

**Response:**
```json
{
  "message": "Call ended successfully",
  "call_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Transcripts

#### GET /transcripts/{call_id}
Get the full transcript for a completed call.

**Path Parameters:**
- `call_id` (string): The unique call identifier

**Response:**
```json
{
  "call_id": "550e8400-e29b-41d4-a716-446655440000",
  "entries": [
    {
      "speaker": "agent",
      "text": "Hello! I'm calling from the medical clinic...",
      "confidence": 98,
      "timestamp": "2024-01-15T10:30:15Z",
      "is_final": true
    },
    {
      "speaker": "patient",
      "text": "Yes, I have a moment.",
      "confidence": 95,
      "timestamp": "2024-01-15T10:30:20Z",
      "is_final": true
    }
  ]
}
```

### Webhooks

#### POST /webhooks/telnyx
Webhook endpoint for Telnyx call events.

**Note:** This endpoint is called by Telnyx service. Configure in Telnyx portal.

**Request Body:**
```json
{
  "data": {
    "event_type": "call.answered",
    "payload": {
      "call_control_id": "unique-call-control-id",
      "call_leg_id": "unique-call-leg-id"
    }
  }
}
```

**Response:**
```json
{
  "status": "ok"
}
```

#### POST /webhooks/transcription
Webhook endpoint for real-time transcription updates.

**Request Body:**
```json
{
  "call_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Patient is describing symptoms",
  "speaker": "patient",
  "confidence": 95,
  "is_final": true
}
```

**Response:**
```json
{
  "status": "ok"
}
```

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "detail": "Invalid phone number format"
}
```

**404 Not Found:**
```json
{
  "detail": "Call not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error message"
}
```

## Data Models

### Call Status
- `initiated`: Call has been initiated but not yet ringing
- `ringing`: Call is ringing
- `answered`: Call has been answered
- `in_progress`: Call is in progress
- `completed`: Call completed successfully
- `failed`: Call failed
- `cancelled`: Call was cancelled

### Call Direction
- `inbound`: Incoming call from patient
- `outbound`: Outgoing call to patient

### Conversation States
The AI agent progresses through these conversation steps:
1. `greeting` - Initial greeting
2. `name_collection` - Collect patient name
3. `dob_collection` - Collect date of birth
4. `reason_for_visit` - Main reason for visit
5. `symptoms` - Symptom description
6. `medical_history` - Medical history
7. `medications` - Current medications
8. `allergies` - Known allergies
9. `insurance` - Insurance information
10. `confirmation` - Confirm collected data
11. `closing` - Closing remarks
12. `completed` - Conversation complete

## Rate Limiting

API endpoints are rate-limited to:
- 100 requests per minute per IP
- 1000 requests per hour per IP

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response.

## Pagination

List endpoints support pagination:
- Use `skip` parameter to skip records
- Use `limit` parameter to control page size (max 100)

Example:
```
GET /calls?skip=20&limit=10
```

## Webhooks Setup

To receive webhook events:

1. **Telnyx Webhooks:**
   - Log into Telnyx portal
   - Configure webhook URL: `https://your-domain.com/webhooks/telnyx`
   - Enable events: call.initiated, call.answered, call.hangup

2. **Transcription Webhooks:**
   - Configure in your transcription service settings
   - Point to: `https://your-domain.com/webhooks/transcription`

## Best Practices

1. **Always use HTTPS in production**
2. **Store API keys securely**
3. **Implement exponential backoff for retries**
4. **Handle webhook failures gracefully**
5. **Validate phone numbers in E.164 format**
6. **Monitor rate limits**
7. **Log all API interactions for HIPAA compliance**

## Examples

### Python
```python
import requests

# Initiate a call
response = requests.post(
    "http://localhost:8000/calls/outbound",
    json={
        "phone_number": "+1234567890",
        "patient_name": "John Doe"
    }
)

call = response.json()
print(f"Call initiated: {call['call_id']}")

# Get call status
response = requests.get(f"http://localhost:8000/calls/{call['call_id']}")
status = response.json()
print(f"Status: {status['status']}")
```

### JavaScript
```javascript
// Initiate a call
const response = await fetch('http://localhost:8000/calls/outbound', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone_number: '+1234567890',
    patient_name: 'John Doe'
  })
});

const call = await response.json();
console.log('Call initiated:', call.call_id);

// Get call status
const statusResponse = await fetch(`http://localhost:8000/calls/${call.call_id}`);
const status = await statusResponse.json();
console.log('Status:', status.status);
```

### cURL
```bash
# Initiate a call
curl -X POST http://localhost:8000/calls/outbound \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1234567890", "patient_name": "John Doe"}'

# Get call status
curl http://localhost:8000/calls/550e8400-e29b-41d4-a716-446655440000

# List all calls
curl http://localhost:8000/calls

# Get statistics
curl http://localhost:8000/stats
```

## Support

For API support:
- Check interactive documentation at `/docs`
- Review error messages and logs
- Contact development team

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Call management endpoints
- Real-time transcription
- AI-powered conversation flow
- HIPAA-compliant audit logging
