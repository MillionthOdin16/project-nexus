import { useAuthStore } from './authStore';

const API_URL = '/api/v1';

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = useAuthStore.getState().token;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers,
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}

// Auth API
export const authApi = {
  login: (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    return fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    }).then(r => {
      if (!r.ok) throw new Error('Invalid credentials');
      return r.json();
    });
  },
  
  register: (email: string, username: string, password: string) =>
    fetchWithAuth('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    }),
  
  me: () => fetchWithAuth('/auth/me'),
};

// Boards API
export const boardsApi = {
  getAll: () => fetchWithAuth('/boards/'),
  getById: (id: number) => fetchWithAuth(`/boards/${id}`),
  create: (title: string, description?: string) =>
    fetchWithAuth('/boards/', {
      method: 'POST',
      body: JSON.stringify({ title, description }),
    }),
  update: (id: number, title: string, description?: string) =>
    fetchWithAuth(`/boards/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ title, description }),
    }),
  delete: (id: number) =>
    fetchWithAuth(`/boards/${id}`, { method: 'DELETE' }),
};

// Tasks API
export const tasksApi = {
  getAll: (boardId?: number) =>
    fetchWithAuth(`/tasks/${boardId ? `?board_id=${boardId}` : ''}`),
  getById: (id: number) => fetchWithAuth(`/tasks/${id}`),
  create: (task: { title: string; description?: string; board_id: number; status?: string; priority?: string }) =>
    fetchWithAuth('/tasks/', {
      method: 'POST',
      body: JSON.stringify(task),
    }),
  update: (id: number, updates: Record<string, unknown>) =>
    fetchWithAuth(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    }),
  move: (id: number, status: string, position: number) =>
    fetchWithAuth(`/tasks/${id}/move`, {
      method: 'PATCH',
      body: JSON.stringify({ status, position }),
    }),
  delete: (id: number) =>
    fetchWithAuth(`/tasks/${id}`, { method: 'DELETE' }),
};
