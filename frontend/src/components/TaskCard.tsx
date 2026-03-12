import { useDraggable } from '@dnd-kit/core';
import { Task, TaskPriority } from '../types';

interface TaskCardProps {
  task: Task;
  onClick: () => void;
}

const priorityColors: Record<TaskPriority, string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-blue-100 text-blue-600',
  high: 'bg-orange-100 text-orange-600',
  urgent: 'bg-red-100 text-red-600',
};

export default function TaskCard({ task, onClick }: TaskCardProps) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: task.id,
  });

  return (
    <div
      ref={setNodeRef}
      {...listeners}
      {...attributes}
      onClick={onClick}
      className={`bg-white p-3 rounded-lg shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow ${
        isDragging ? 'opacity-50' : ''
      }`}
    >
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-medium text-gray-900 text-sm">{task.title}</h4>
        {task.claimed_by_ai && (
          <span className="text-xs bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded">
            AI
          </span>
        )}
      </div>

      {task.description && (
        <p className="text-xs text-gray-500 mb-2 line-clamp-2">{task.description}</p>
      )}

      <div className="flex justify-between items-center">
        <span className={`text-xs px-2 py-0.5 rounded-full ${priorityColors[task.priority]}`}>
          {task.priority}
        </span>

        {task.due_date && (
          <span className={`text-xs ${
            new Date(task.due_date) < new Date() ? 'text-red-500' : 'text-gray-400'
          }`}>
            {new Date(task.due_date).toLocaleDateString()}
          </span>
        )}
      </div>

      {task.labels && (
        <div className="flex flex-wrap gap-1 mt-2">
          {task.labels.split(',').map((label) => (
            <span
              key={label}
              className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded"
            >
              {label.trim()}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
