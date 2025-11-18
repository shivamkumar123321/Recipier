# Weight Coach 🏋️

> AI-Powered Nutrition Coach - Your personal health companion

Weight Coach is an intelligent nutrition tracking web app that helps you achieve your health goals through AI-powered meal analysis, voice input, and personalized coaching.

## Features

- **Smart Meal Logging**: Log meals via text, voice, or photo
- **AI Nutrition Analysis**: Instant nutritional breakdown powered by GPT-4
- **Image Recognition**: Identify food from photos using AI Vision
- **Voice Input**: Speak your meals using Whisper speech-to-text
- **Personalized Coaching**: Get tailored nutrition advice based on your goals
- **Progress Tracking**: Visualize your journey with charts and insights

## Tech Stack

**Frontend**
- Next.js 14 (App Router)
- React + TypeScript
- Tailwind CSS
- shadcn/ui

**Backend**
- FastAPI (Python)
- PostgreSQL
- Redis
- OpenAI API (GPT-4, Whisper, Vision)

**Deployment**
- Vercel (Frontend)
- Railway (Backend)

## Project Structure

```
weight-coach/
├── frontend/          # Next.js app
├── backend/           # FastAPI server
├── docs/              # Documentation
├── CLAUDE.md          # Comprehensive project docs
└── README.md          # This file
```

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- OpenAI API key

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

API available at http://localhost:8000

### Environment Variables

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`.env`):
```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/weight_coach
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-secret-key
```

See `CLAUDE.md` for complete configuration details.

## Development

### Frontend Commands
```bash
npm run dev        # Start dev server
npm run build      # Build for production
npm run lint       # Lint code
npm run test       # Run tests
```

### Backend Commands
```bash
uvicorn app.main:app --reload    # Start dev server
pytest                           # Run tests
alembic upgrade head             # Run migrations
black app/ && isort app/         # Format code
```

## Documentation

- **CLAUDE.md**: Comprehensive project documentation, architecture, and conventions
- **docs/api.md**: API endpoint documentation
- **docs/deployment.md**: Deployment guide
- **docs/database-schema.md**: Database schema details

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

This is a hackathon project! Key principles:

1. Use conventional commit format
2. Test before pushing
3. Update CLAUDE.md for architectural changes
4. Keep code simple and maintainable

## License

MIT License - built for hackathon purposes

## Contact

Created for [Hackathon Name] - [Your Team Name]

---

**For detailed development guidelines, architecture details, and conventions, see CLAUDE.md**
