# Project Nexus - Task Management Dashboard

## Project Overview

**Project Name:** Project Nexus  
**Type:** Full-stack Trello-like Task Management Web Application  
**Core Functionality:** A collaborative task management dashboard allowing humans and AI agents to track goals, tasks, notes, and brainstorm ideas through a Kanban-style interface.  
**Target Users:** Bradley (human) + Hermes Agent (AI)

---

## Architecture

### Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend** | FastAPI | Modern, fast, excellent API design, built-in docs, async WebSocket support |
| **Database** | PostgreSQL | Robust relational DB, excellent with structured task data, LISTEN/NOTIFY for real-time |
| **Frontend** | React + TypeScript | Most popular, great ecosystem, excellent DnD libraries |
| **UI Framework** | Tailwind CSS + shadcn/ui | Clean, modern, beautiful, accessible components |
| **Drag & Drop** | @dnd-kit | Modern, accessible, well-maintained (replaces abandoned react-beautiful-dnd) |
| **Real-time** | WebSockets + PostgreSQL LISTEN/NOTIFY | Live updates without polling |
| **Auth** | JWT Tokens | Stateless, works well for API access |
| **Deployment** | Docker Compose | Easy deployment, reproducibility |

### Project Structure

```
project-nexus/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── boards.py
│   │   │       │   ├── lists.py
│   │   │       │   ├── cards.py
│   │   │       │   ├── notes.py
│   │   │       │   └── comments.py
│   │   │       └── router.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── websocket.py
│   │   ├── db/
│   │   │   └── base.py
│   │   ├── models/
│   │   │   ├── sqlmodels.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   └── realtime.py
│   │   └── main.py
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/           # shadcn components
│   │   │   ├── board/        # Board components
│   │   │   ├── kanban/       # Kanban board components
│   │   │   └── layout/       # Layout components
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── pages/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Database Schema

### Tables

```sql
-- Users table
users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)

-- Boards table
boards (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID REFERENCES users(id),
    is_shared BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)

-- Board Members (for sharing)
board_members (
    board_id UUID REFERENCES boards(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(50) DEFAULT 'member',
    PRIMARY KEY (board_id, user_id)
)

-- Lists (columns within boards)
lists (
    id UUID PRIMARY KEY,
    board_id UUID REFERENCES boards(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    color VARCHAR(7),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)

-- Cards (tasks/items)
cards (
    id UUID PRIMARY KEY,
    list_id UUID REFERENCES lists(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    priority VARCHAR(20) DEFAULT 'medium',
    due_date TIMESTAMP,
    labels JSONB,
    assigned_to UUID REFERENCES users(id),
    created_by UUID REFERENCES users(id),
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)

-- Notes (standalone notes, not attached to cards)
notes (
    id UUID PRIMARY KEY,
    board_id UUID REFERENCES boards(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT,
    position JSONB,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)

-- Comments (on cards)
comments (
    id UUID PRIMARY KEY,
    card_id UUID REFERENCES cards(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
)

-- Activity Log
activity_log (
    id UUID PRIMARY KEY,
    board_id UUID REFERENCES boards(id),
    card_id UUID REFERENCES cards(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
)
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| POST | `/api/v1/auth/refresh` | Refresh JWT token |
| GET | `/api/v1/auth/me` | Get current user |

### Boards
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/boards` | List user's boards |
| POST | `/api/v1/boards` | Create new board |
| GET | `/api/v1/boards/{id}` | Get board with lists/cards |
| PUT | `/api/v1/boards/{id}` | Update board |
| DELETE | `/api/v1/boards/{id}` | Delete board |

### Lists
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/boards/{board_id}/lists` | Create list |
| PUT | `/api/v1/lists/{id}` | Update list |
| DELETE | `/api/v1/lists/{id}` | Delete list |
| PUT | `/api/v1/lists/reorder` | Reorder lists |

### Cards
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/lists/{list_id}/cards` | Create card |
| GET | `/api/v1/cards/{id}` | Get card details |
| PUT | `/api/v1/cards/{id}` | Update card |
| DELETE | `/api/v1/cards/{id}` | Delete card |
| PUT | `/api/v1/cards/{id}/move` | Move card to different list |
| PUT | `/api/v1/cards/reorder` | Reorder cards |

### Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/boards/{board_id}/notes` | List notes |
| POST | `/api/v1/boards/{board_id}/notes` | Create note |
| PUT | `/api/v1/notes/{id}` | Update note |
| DELETE | `/api/v1/notes/{id}` | Delete note |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cards/{card_id}/comments` | List comments |
| POST | `/api/v1/cards/{card_id}/comments` | Add comment |
| DELETE | `/api/v1/comments/{id}` | Delete comment |

### AI API (for Hermes)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/ai/tasks` | Get available tasks (priority ordered) |
| GET | `/api/v1/ai/boards` | Get all boards |
| POST | `/api/v1/ai/tasks/{id}/claim` | Claim a task |
| POST | `/api/v1/ai/tasks/{id}/complete` | Mark task complete |
| POST | `/api/v1/ai/tasks/{id}/progress` | Update progress |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| `/ws/{board_id}` | Real-time board updates |

---

## Features

### Core Features

1. **Kanban Boards**
   - Create multiple boards for different projects
   - Drag-and-drop cards between lists
   - Reorder lists and cards
   - Visual priority indicators (color-coded)

2. **Task Management**
   - Create, edit, delete tasks
   - Priority levels: Low, Medium, High, Urgent
   - Due dates with reminders
   - Labels/tags for categorization
   - Assign tasks to users

3. **Notes & Brainstorming**
   - Free-form notes on boards
   - Quick capture for ideas
   - Link notes to tasks

4. **Communication**
   - Comments on cards
   - Activity log
   - Real-time updates via WebSocket

5. **AI Integration**
   - API access for AI agent
   - Task queue with priorities
   - Task claiming and progress tracking
   - Natural language task creation

### User Features

1. **Authentication**
   - JWT-based auth
   - Login/logout
   - User profiles

2. **Dashboard**
   - Overview of all boards
   - Recent activity
   - My tasks

3. **Search & Filter**
   - Search across boards
   - Filter by priority, assignee, labels

---

## UI/UX Design

### Color Palette

| Role | Color | Hex |
|------|-------|-----|
| Primary | Deep Indigo | `#4F46E5` |
| Primary Hover | Indigo 700 | `#4338CA` |
| Secondary | Slate | `#64748B` |
| Background | White | `#FFFFFF` |
| Surface | Gray 50 | `#F8FAFC` |
| Border | Gray 200 | `#E2E8F0` |
| Text Primary | Gray 900 | `#0F172A` |
| Text Secondary | Gray 600 | `#475569` |
| Success | Emerald | `#10B981` |
| Warning | Amber | `#F59E0B` |
| Danger | Red | `#EF4444` |

### Priority Colors

| Priority | Color | Hex |
|----------|-------|-----|
| Low | Gray | `#94A3B8` |
| Medium | Blue | `#3B82F6` |
| High | Orange | `#F97316` |
| Urgent | Red | `#EF4444` |

### Layout

1. **Sidebar** (left, 250px)
   - Logo/app name
   - Board list
   - New board button
   - User profile/logout

2. **Main Content** (flex-1)
   - Board header (name, description, members)
   - Kanban columns (scrollable horizontal)
   - Cards within columns

3. **Card Modal** (overlay)
   - Title, description
   - Priority selector
   - Due date picker
   - Labels
   - Comments
   - Activity log

---

## Security Considerations

1. **Password Hashing**: bcrypt with salt
2. **JWT Tokens**: Short-lived access tokens (15 min), longer refresh tokens (7 days)
3. **CORS**: Configure allowed origins
4. **Rate Limiting**: Implement for API endpoints
5. **Input Validation**: Pydantic models
6. **SQL Injection**: SQLModel with parameterized queries

---

## Deployment

### Docker Compose Setup

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/nexus
      - SECRET_KEY=your-secret-key
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=nexus
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

---

## Development Workflow

### Setup

```bash
# Clone and setup
cp .env.example .env
# Edit .env with your values

# Start development
docker-compose up -d

# Backend runs on http://localhost:8000
# Frontend runs on http://localhost:3000
# API docs at http://localhost:8000/docs
```

### API Key for AI Access

AI agents will use a dedicated API key stored in environment:
```
AI_API_KEY=your-ai-api-key
```

---

## Success Criteria

1. Users can create accounts and log in
2. Users can create boards, lists, and cards
3. Drag-and-drop works smoothly
4. Real-time updates propagate to all clients
5. AI can access tasks via API
6. Beautiful, responsive UI
7. Fast page loads
8. Deployment works on aqualify server
