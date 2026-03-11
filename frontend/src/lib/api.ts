import axios from 'axios'

const API_URL = '/api'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/v1/auth/login', new URLSearchParams({ username: email, password })),
  register: (data: { email: string; username: string; password: string }) =>
    api.post('/v1/auth/register', data),
  me: () => api.get('/v1/auth/me'),
  refresh: (refreshToken: string) =>
    api.post('/v1/auth/refresh', { refresh_token: refreshToken }),
}

// Boards API
export const boardsApi = {
  list: () => api.get('/v1/boards'),
  get: (id: string) => api.get(`/v1/boards/${id}`),
  create: (data: { name: string; description?: string }) =>
    api.post('/v1/boards', data),
  update: (id: string, data: { name?: string; description?: string }) =>
    api.put(`/v1/boards/${id}`, data),
  delete: (id: string) => api.delete(`/v1/boards/${id}`),
}

// Lists API
export const listsApi = {
  create: (boardId: string, data: { name: string; color?: string }) =>
    api.post(`/v1/boards/${boardId}/lists`, data),
  update: (id: string, data: { name?: string; color?: string; position?: number }) =>
    api.put(`/v1/lists/${id}`, data),
  delete: (id: string) => api.delete(`/v1/lists/${id}`),
  reorder: (boardId: string, items: { id: string; position: number }[]) =>
    api.post(`/v1/lists/reorder?board_id=${boardId}`, { items }),
}

// Cards API
export const cardsApi = {
  create: (listId: string, data: {
    title: string;
    description?: string;
    priority?: string;
    due_date?: string;
  }) => api.post(`/v1/lists/${listId}/cards`, data),
  get: (id: string) => api.get(`/v1/cards/${id}`),
  update: (id: string, data: {
    title?: string;
    description?: string;
    priority?: string;
    due_date?: string;
    assigned_to?: string;
  }) => api.put(`/v1/cards/${id}`, data),
  delete: (id: string) => api.delete(`/v1/cards/${id}`),
  move: (id: string, listId: string, position: number) =>
    api.post(`/v1/cards/move/${id}`, { list_id: listId, position }),
  reorder: (items: { id: string; position: number }[]) =>
    api.post('/v1/cards/reorder', { items }),
}

// Comments API
export const commentsApi = {
  list: (cardId: string) => api.get(`/v1/comments/card/${cardId}`),
  create: (cardId: string, content: string) =>
    api.post('/v1/comments', { card_id: cardId, content }),
  delete: (id: string) => api.delete(`/v1/comments/${id}`),
}
