import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Plus, MoreHorizontal, Pencil, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { KanbanColumn } from '@/components/kanban/KanbanColumn'
import { boardsApi, listsApi, cardsApi } from '@/lib/api'

interface List {
  id: string
  name: string
  color?: string
  position: number
  cards: Card[]
}

interface Card {
  id: string
  title: string
  description?: string
  priority: string
  position: number
  due_date?: string
  labels?: any[]
}

interface Board {
  id: string
  name: string
  description?: string
  lists: List[]
}

export function BoardPage() {
  const { boardId } = useParams<{ boardId: string }>()
  const [board, setBoard] = useState<Board | null>(null)
  const [loading, setLoading] = useState(true)
  const [editingTitle, setEditingTitle] = useState(false)
  const [newListName, setNewListName] = useState('')
  const [addingList, setAddingList] = useState(false)

  useEffect(() => {
    if (boardId) {
      loadBoard()
    }
  }, [boardId])

  const loadBoard = async () => {
    try {
      const { data } = await boardsApi.get(boardId!)
      setBoard(data)
    } catch (error) {
      console.error('Failed to load board:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateTitle = async () => {
    if (!board) return
    try {
      await boardsApi.update(board.id, { name: board.name })
      setEditingTitle(false)
    } catch (error) {
      console.error('Failed to update board:', error)
    }
  }

  const handleAddList = async () => {
    if (!board || !newListName.trim()) return
    try {
      await listsApi.create(board.id, { name: newListName.trim() })
      setNewListName('')
      setAddingList(false)
      loadBoard()
    } catch (error) {
      console.error('Failed to create list:', error)
    }
  }

  const handleDeleteList = async (listId: string) => {
    if (!confirm('Delete this list and all its cards?')) return
    try {
      await listsApi.delete(listId)
      loadBoard()
    } catch (error) {
      console.error('Failed to delete list:', error)
    }
  }

  const handleCardMove = async (cardId: string, targetListId: string, position: number) => {
    try {
      await cardsApi.move(cardId, targetListId, position)
      loadBoard()
    } catch (error) {
      console.error('Failed to move card:', error)
    }
  }

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <div className="text-muted-foreground">Loading board...</div>
      </div>
    )
  }

  if (!board) {
    return (
      <div className="p-8 flex items-center justify-center h-full">
        <div className="text-muted-foreground">Board not found</div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Board Header */}
      <div className="p-4 border-b bg-card">
        <div className="flex items-center gap-4">
          {editingTitle ? (
            <Input
              value={board.name}
              onChange={(e) => setBoard({ ...board, name: e.target.value })}
              onBlur={handleUpdateTitle}
              onKeyDown={(e) => e.key === 'Enter' && handleUpdateTitle()}
              className="text-xl font-bold"
              autoFocus
            />
          ) : (
            <h1
              className="text-xl font-bold cursor-pointer hover:text-primary"
              onClick={() => setEditingTitle(true)}
            >
              {board.name}
            </h1>
          )}
        </div>
        {board.description && (
          <p className="text-sm text-muted-foreground mt-1">{board.description}</p>
        )}
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto p-4">
        <div className="flex gap-4 h-full min-w-max">
          {/* Lists */}
          {board.lists.map((list) => (
            <KanbanColumn
              key={list.id}
              list={list}
              onCardMove={handleCardMove}
              onDelete={() => handleDeleteList(list.id)}
              onCardUpdate={loadBoard}
            />
          ))}

          {/* Add List */}
          <div className="w-72 flex-shrink-0">
            {addingList ? (
              <div className="bg-card rounded-lg border p-3">
                <Input
                  placeholder="List name..."
                  value={newListName}
                  onChange={(e) => setNewListName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddList()}
                  autoFocus
                />
                <div className="flex gap-2 mt-2">
                  <Button size="sm" onClick={handleAddList}>
                    Add
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setAddingList(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => setAddingList(true)}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add List
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
