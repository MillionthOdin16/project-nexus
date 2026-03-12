import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { Link } from 'react-router-dom';
import { boardsApi } from '../store/api';
import { Board } from '../types';

export default function Boards() {
  const [newBoardTitle, setNewBoardTitle] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const queryClient = useQueryClient();

  const { data: boards, isLoading } = useQuery('boards', boardsApi.getAll);

  const createMutation = useMutation(
    (title: string) => boardsApi.create(title),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('boards');
        setNewBoardTitle('');
        setIsCreating(false);
      },
    }
  );

  const deleteMutation = useMutation(
    (id: number) => boardsApi.delete(id),
    {
      onSuccess: () => queryClient.invalidateQueries('boards'),
    }
  );

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (newBoardTitle.trim()) {
      createMutation.mutate(newBoardTitle.trim());
    }
  };

  if (isLoading) {
    return <div className="text-center py-12">Loading boards...</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Boards</h1>
        <button
          onClick={() => setIsCreating(true)}
          className="btn-primary"
        >
          + New Board
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="mb-6 card">
          <h3 className="text-lg font-medium mb-4">Create New Board</h3>
          <input
            type="text"
            placeholder="Board title"
            className="input mb-4"
            value={newBoardTitle}
            onChange={(e) => setNewBoardTitle(e.target.value)}
            autoFocus
          />
          <div className="flex space-x-2">
            <button
              type="submit"
              disabled={createMutation.isLoading}
              className="btn-primary disabled:opacity-50"
            >
              {createMutation.isLoading ? 'Creating...' : 'Create'}
            </button>
            <button
              type="button"
              onClick={() => setIsCreating(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {boards?.map((board: Board) => (
          <div key={board.id} className="card hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-2">
              <Link to={`/boards/${board.id}`} className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 hover:text-primary-600">
                  {board.title}
                </h3>
              </Link>
              <button
                onClick={() => deleteMutation.mutate(board.id)}
                className="text-red-500 hover:text-red-700 text-sm"
                title="Delete board"
              >
                ×
              </button>
            </div>
            {board.description && (
              <p className="text-gray-600 text-sm mb-4">{board.description}</p>
            )}
            <div className="text-xs text-gray-400">
              Created {new Date(board.created_at).toLocaleDateString()}
            </div>
          </div>
        ))}
      </div>

      {boards?.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p>No boards yet. Create your first board to get started!</p>
        </div>
      )}
    </div>
  );
}
