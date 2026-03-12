import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  DndContext, 
  DragEndEvent, 
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import { boardsApi, tasksApi } from '../store/api';
import { Board as BoardType, Task, TaskStatus } from '../types';
import KanbanColumn from '../components/KanbanColumn';
import TaskCard from '../components/TaskCard';
import TaskModal from '../components/TaskModal';

const COLUMNS: { id: TaskStatus; title: string }[] = [
  { id: 'backlog', title: 'Backlog' },
  { id: 'todo', title: 'To Do' },
  { id: 'in_progress', title: 'In Progress' },
  { id: 'review', title: 'Review' },
  { id: 'done', title: 'Done' },
];

export default function Board() {
  const { id } = useParams<{ id: string }>();
  const boardId = parseInt(id || '0');
  const queryClient = useQueryClient();
  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const { data: board, isLoading } = useQuery(
    ['board', boardId],
    () => boardsApi.getById(boardId)
  );

  const moveMutation = useMutation(
    ({ taskId, status, position }: { taskId: number; status: TaskStatus; position: number }) =>
      tasksApi.move(taskId, status, position),
    {
      onSuccess: () => queryClient.invalidateQueries(['board', boardId]),
    }
  );

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    const task = board?.tasks?.find((t: Task) => t.id === event.active.id);
    if (task) setActiveTask(task);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const taskId = active.id as number;
    const overId = over.id as string;

    // Check if dropped on a column
    const column = COLUMNS.find(c => c.id === overId);
    if (column) {
      const tasksInColumn = board?.tasks?.filter((t: Task) => t.status === column.id) || [];
      moveMutation.mutate({
        taskId,
        status: column.id,
        position: tasksInColumn.length,
      });
    }
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsModalOpen(true);
  };

  const getTasksByStatus = (status: TaskStatus): Task[] => {
    return board?.tasks
      ?.filter((t: Task) => t.status === status)
      .sort((a: Task, b: Task) => a.position - b.position) || [];
  };

  if (isLoading) {
    return <div className="text-center py-12">Loading board...</div>;
  }

  if (!board) {
    return <div className="text-center py-12 text-red-600">Board not found</div>;
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{board.title}</h1>
        {board.description && (
          <p className="text-gray-600 mt-1">{board.description}</p>
        )}
      </div>

      <DndContext
        sensors={sensors}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="flex space-x-4 overflow-x-auto pb-4">
          {COLUMNS.map((column) => (
            <KanbanColumn
              key={column.id}
              id={column.id}
              title={column.title}
              tasks={getTasksByStatus(column.id)}
              boardId={boardId}
              onTaskClick={handleTaskClick}
            />
          ))}
        </div>

        <DragOverlay>
          {activeTask ? (
            <div className="opacity-90 rotate-2">
              <TaskCard task={activeTask} onClick={() => {}} />
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {isModalOpen && (
        <TaskModal
          task={selectedTask}
          boardId={boardId}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedTask(null);
          }}
        />
      )}
    </div>
  );
}
