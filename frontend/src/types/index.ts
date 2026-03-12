export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  board_id: number;
  assignee_id: number | null;
  created_by: number;
  due_date: string | null;
  labels: string | null;
  position: number;
  claimed_by_ai: boolean;
  ai_agent_id: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  assignee?: User;
}

export interface Board {
  id: number;
  title: string;
  description: string | null;
  owner_id: number;
  created_at: string;
  updated_at: string;
  tasks?: Task[];
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  board_id: number;
  due_date?: string;
  labels?: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string | null;
  labels?: string;
  assignee_id?: number | null;
}
