# Project Nexus Specification

## Overview
Full-stack Kanban board application with AI agent integration for human-AI task collaboration.

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL
- **Auth**: JWT tokens
- **API**: RESTful + WebSocket ready

### Frontend (React)
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **DnD**: @dnd-kit
- **State**: React Query + Zustand

## Features

### Core
- Kanban boards with drag-and-drop
- Task cards with priorities, due dates, labels
- User authentication (JWT)
- Real-time updates (WebSocket)

### AI Integration
- Task queue for AI agents
- Claim/complete workflow
- API key authentication

## API Endpoints

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`

### Boards
- `GET /api/v1/boards`
- `POST /api/v1/boards`
- `GET /api/v1/boards/{id}`
- `PUT /api/v1/boards/{id}`
- `DELETE /api/v1/boards/{id}`

### Tasks
- `GET /api/v1/tasks`
- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{id}`
- `PUT /api/v1/tasks/{id}`
- `DELETE /api/v1/tasks/{id}`
- `PATCH /api/v1/tasks/{id}/move`

### AI
- `GET /api/v1/ai/tasks` - Available tasks
- `POST /api/v1/ai/tasks/{id}/claim` - Claim task
- `POST /api/v1/ai/tasks/{id}/complete` - Complete task
