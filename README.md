# Project Nexus

A Trello-like task management dashboard for human-AI collaboration.

## Features

- **Kanban Boards** - Create boards, lists, and cards with drag-and-drop
- **Task Management** - Priority levels, due dates, labels
- **Real-time Updates** - WebSocket support for live collaboration
- **AI Integration** - API access for AI agents to pull and complete tasks
- **Authentication** - JWT-based auth with user accounts
- **Beautiful UI** - Modern React + Tailwind CSS with shadcn/ui

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, PostgreSQL |
| Frontend | React, TypeScript, Tailwind CSS, @dnd-kit |
| Auth | JWT |
| Real-time | WebSockets |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- PostgreSQL (optional, provided by Docker)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/project-nexus.git
cd project-nexus
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your values:
```bash
SECRET_KEY=your-super-secret-key
AI_API_KEY=your-ai-api-key
POSTGRES_PASSWORD=your-password
```

4. Start the application:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost
- Backend API: http://localhost/api/docs
- API Docs: http://localhost/api/docs

### Default Credentials

After first run, register a new account through the UI.

## Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## AI API Usage

### Get Available Tasks

```bash
curl -H "X-API-Key: your-ai-api-key" \
  http://localhost/api/v1/ai/tasks
```

### Claim a Task

```bash
curl -X POST -H "X-API-Key: your-ai-api-key" \
  http://localhost/api/v1/ai/tasks/{task_id}/claim
```

### Complete a Task

```bash
curl -X POST -H "X-API-Key: your-ai-api-key" \
  http://localhost/api/v1/ai/tasks/{task_id}/complete
```

## Project Structure

```
project-nexus/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Config, security
│   │   ├── db/       # Database session
│   │   └── models/   # SQL models & schemas
│   └── requirements.txt
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   └── lib/
│   └── package.json
├── nginx/            # Nginx config
└── docker-compose.yml
```

## License

MIT
