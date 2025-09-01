# Health Plan Agent Backend

FastAPI backend for health plan generation and management using the health-plan-agent system.

## 🚀 Features

- **Health Plan Generation**: AI-powered plan generation using multiple specialized agents
- **Database Integration**: Supabase integration for plan storage and retrieval
- **RESTful API**: Clean API endpoints for plan management
- **Railway Ready**: Optimized for Railway deployment

## 📋 API Endpoints

- `GET /health` - Health check
- `POST /api/v1/plans/generate` - Generate new health plan
- `GET /api/v1/plans/discover` - Get all available plans
- `GET /api/v1/plans/{plan_id}` - Get specific plan

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run locally
python railway_main.py
```

## 🚀 Railway Deployment

1. **Connect to Railway**: Link this repository to Railway
2. **Set Environment Variables**:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY` (optional)
3. **Deploy**: Railway will automatically deploy using the Procfile

## 📦 Project Structure

```
health-plan-agent-backend/
├── app/                    # FastAPI backend components
├── src/                    # Health-plan-agent system
├── railway_main.py         # Main application entry point
├── requirements.txt        # Python dependencies
├── Procfile               # Railway deployment config
└── README.md              # This file
```

## 🔧 Configuration

The backend integrates:
- **FastAPI**: Web framework
- **Supabase**: Database and authentication
- **Health-Plan-Agent**: AI-powered plan generation
- **OpenAI/Anthropic**: LLM providers for plan generation

## 📝 Usage Example

```bash
# Generate a new health plan
curl -X POST "https://your-railway-app.railway.app/api/v1/plans/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "population": "senior_fitness",
    "goals": ["mobility", "strength"],
    "constraints": ["arthritis"],
    "timeline": "12_weeks",
    "fitness_level": "beginner"
  }'

# Discover all plans
curl "https://your-railway-app.railway.app/api/v1/plans/discover"
```
