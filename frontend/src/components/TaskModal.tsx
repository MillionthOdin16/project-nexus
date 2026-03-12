import { useState } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { tasksApi } from '../store/api';
import { Task, TaskPriority, TaskStatus } from '../types';

interface TaskModalProps {
  task: Task | null;
  boardId: number;
  onClose: () => void;
}

export default function TaskModal({ task, boardId, onClose }: TaskModalProps) {
  const queryClient = useQueryClient();
  const isEditing = !!task;

  const [formData, setFormData] = useState({
    title: task?.title || '',
    description: task?.description || '',
    status: task?.status || 'todo' as TaskStatus,
    priority: task?.priority || 'medium' as TaskPriority,
    due_date: task?.due_date ? task.due_date.split('T')[0] : '',
    labels: task?.labels || '',
  });

  const saveMutation = useMutation(
    () => {
      if (isEditing) {
        return tasksApi.update(task!.id, formData);
      }
      return tasksApi.create({ ...formData, board_id: boardId });
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['board', boardId]);
        onClose();
      },
    }
  );

  const deleteMutation = useMutation(
    () => tasksApi.delete(task!.id),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['board', boardId]);
        onClose();
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    saveMutation.mutate();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-lg mx-4">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {isEditing ? 'Edit Task' : 'New Task'}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title *
              </label>
              <input
                type="text"
                required
                className="input"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                rows={3}
                className="input"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  className="input"
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as TaskStatus })}
                >
                  <option value="backlog">Backlog</option>
                  <option value="todo">To Do</option>
                  <option value="in_progress">In Progress</option>
                  <option value="review">Review</option>
                  <option value="done">Done</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Priority
                </label>
                <select
                  className="input"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as TaskPriority })}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Date
              </label>
              <input
                type="date"
                className="input"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Labels (comma separated)
              </label>
              <input
                type="text"
                placeholder="bug, feature, urgent"
                className="input"
                value={formData.labels}
                onChange={(e) => setFormData({ ...formData, labels: e.target.value })}
              />
            </div>

            <div className="flex justify-between pt-4">
              <div>
                {isEditing && (
                  <button
                    type="button"
                    onClick={() => deleteMutation.mutate()}
                    disabled={deleteMutation.isLoading}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Delete Task
                  </button>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saveMutation.isLoading}
                  className="btn-primary disabled:opacity-50"
                >
                  {saveMutation.isLoading ? 'Saving...' : (isEditing ? 'Save' : 'Create')}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
