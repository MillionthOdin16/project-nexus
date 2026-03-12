import { useDroppable } from '@dnd-kit/core';
import { useState } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { tasksApi } from '../store/api';
import { Task, TaskStatus } from '../types';
import TaskCard from './TaskCard';

interface KanbanColumnProps {
  id: TaskStatus;
  title: string;
  tasks: Task[];
  boardId: number;
  onTaskClick: (task: Task) => void;
}

export default function KanbanColumn({ id, title, tasks, boardId, onTaskClick }: KanbanColumnProps) {
  const { isOver, setNodeRef } = useDroppable({ id });
  const [isAdding, setIsAdding] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const queryClient = useQueryClient();

  const createMutation = useMutation(
    (title: string) =>
      tasksApi.create({
        title,
        board_id: boardId,
        status: id,
        priority: 'medium',
      }),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['board', boardId]);
        setNewTaskTitle('');
        setIsAdding(false);
      },
    }
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newTaskTitle.trim()) {
      createMutation.mutate(newTaskTitle.trim());
    }
  };

  const columnColors: Record<TaskStatus, string> = {
    backlog: 'bg-gray-100 border-gray-200',
    todo: 'bg-blue-50 border-blue-200',
    in_progress: 'bg-yellow-50 border-yellow-200',
    review: 'bg-purple-50 border-purple-200',
    done: 'bg-green-50 border-green-200',
  };

  return (
    <div
      ref={setNodeRef}
      className={`flex-shrink-0 w-72 rounded-lg border-2 ${
        isOver ? 'border-primary-500 bg-primary-50' : columnColors[id]
      } transition-colors`}
    >
      <div className="p-3 border-b border-gray-200/50">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold text-gray-700">{title}</h3>
          <span className="text-xs bg-white px-2 py-1 rounded-full text-gray-500">
            {tasks.length}
          </span>
        </div>
      </div>

      <div className="p-3 space-y-3 min-h-[200px]">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onClick={() => onTaskClick(task)}
          />
        ))}

        {isAdding ? (
          <form onSubmit={handleSubmit} className="space-y-2">
            <input
              type="text"
              placeholder="Task title"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              autoFocus
              onBlur={() => !newTaskTitle && setIsAdding(false)}
            />
            <div className="flex space-x-2">
              <button
                type="submit"
                disabled={createMutation.isLoading}
                className="px-3 py-1 text-sm bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50"
              >
                Add
              </button>
              <button
                type="button"
                onClick={() => setIsAdding(false)}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <button
            onClick={() => setIsAdding(true)}
            className="w-full py-2 text-sm text-gray-500 hover:text-gray-700 hover:bg-white/50 rounded transition-colors"
          >
            + Add task
          </button>
        )}
      </div>
    </div>
  );
}
