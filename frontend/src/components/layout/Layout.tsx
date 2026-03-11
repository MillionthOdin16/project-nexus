import { Link, useNavigate, useParams } from 'react-router-dom'
import { Plus, Layout, LogOut, Settings, ChevronRight, Layers } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useEffect, useState } from 'react'
import { boardsApi } from '@/lib/api'
import { cn } from '@/utils'

interface Board {
  id: string
  name: string
  description?: string
}

export function LayoutComponent({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()
  const [boards, setBoards] = useState<Board[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadBoards()
  }, [])

  const loadBoards = async () => {
    try {
      const { data } = await boardsApi.list()
      setBoards(data)
    } catch (error) {
      console.error('Failed to load boards:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg">Nexus</span>
          </Link>
        </div>

        {/* Boards */}
        <div className="flex-1 overflow-y-auto p-2">
          <div className="px-2 py-1 text-xs font-medium text-muted-foreground uppercase">
            Your Boards
          </div>
          {loading ? (
            <div className="px-2 py-4 text-sm text-muted-foreground">Loading...</div>
          ) : boards.length === 0 ? (
            <div className="px-2 py-4 text-sm text-muted-foreground">
              No boards yet
            </div>
          ) : (
            <div className="space-y-1">
              {boards.map((board) => (
                <BoardLink key={board.id} board={board} />
              ))}
            </div>
          )}
        </div>

        {/* New Board Button */}
        <div className="p-2 border-t">
          <NewBoardButton onCreated={loadBoards} />
        </div>

        {/* User */}
        <div className="p-4 border-t">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium">U</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">User</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={handleLogout}>
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">{children}</main>
    </div>
  )
}

function BoardLink({ board }: { board: Board }) {
  const { boardId } = useParams()
  const isActive = boardId === board.id

  return (
    <Link
      to={`/board/${board.id}`}
      className={cn(
        'flex items-center gap-2 px-2 py-1.5 rounded-md text-sm transition-colors',
        isActive
          ? 'bg-primary/10 text-primary'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground'
      )}
    >
      <Layout className="w-4 h-4 flex-shrink-0" />
      <span className="truncate">{board.name}</span>
    </Link>
  )
}

function NewBoardButton({ onCreated }: { onCreated: () => void }) {
  const [name, setName] = useState('')
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return

    setLoading(true)
    try {
      await boardsApi.create({ name: name.trim() })
      setName('')
      setOpen(false)
      onCreated()
    } catch (error) {
      console.error('Failed to create board:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!open) {
    return (
      <Button variant="outline" className="w-full justify-start" onClick={() => setOpen(true)}>
        <Plus className="w-4 h-4 mr-2" />
        New Board
      </Button>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Board name..."
        className="w-full px-2 py-1.5 text-sm border rounded-md"
        autoFocus
      />
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={loading}>
          {loading ? 'Creating...' : 'Create'}
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
