import { useState } from 'react'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Calendar, MoreHorizontal, Pencil, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card as CardUI, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { cardsApi } from '@/lib/api'

interface Card {
  id: string
  title: string
  description?: string
  priority: string
  position: number
  due_date?: string
}

interface Props {
  card: Card
  onUpdate: () => void
}

const priorityColors: Record<string, string> = {
  low: 'bg-slate-400',
  medium: 'bg-blue-500',
  high: 'bg-orange-500',
  urgent: 'bg-red-500',
}

export function KanbanCard({ card, onUpdate }: Props) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [title, setTitle] = useState(card.title)
  const [description, setDescription] = useState(card.description || '')
  const [priority, setPriority] = useState(card.priority)

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: card.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  const handleSave = async () => {
    try {
      await cardsApi.update(card.id, {
        title,
        description,
        priority,
      })
      setDialogOpen(false)
      onUpdate()
    } catch (error) {
      console.error('Failed to update card:', error)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this card?')) return
    try {
      await cardsApi.delete(card.id)
      onUpdate()
    } catch (error) {
      console.error('Failed to delete card:', error)
    }
  }

  return (
    <>
      <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
        <CardUI
          className={`mb-2 cursor-grab active:cursor-grabbing ${
            isDragging ? 'opacity-50' : ''
          }`}
          onClick={() => setDialogOpen(true)}
        >
          <CardContent className="p-3">
            {/* Priority indicator */}
            <div className="flex items-start gap-2">
              <div
                className={`w-1 h-full min-h-[20px] rounded-full ${priorityColors[card.priority]}`}
              />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{card.title}</p>
                {card.description && (
                  <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                    {card.description}
                  </p>
                )}
                {card.due_date && (
                  <div className="flex items-center gap-1 mt-2 text-xs text-muted-foreground">
                    <Calendar className="w-3 h-3" />
                    {new Date(card.due_date).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </CardUI>
      </div>

      {/* Edit Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Card</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Title</label>
              <Input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full mt-1 p-2 border rounded-md text-sm min-h-[100px]"
                placeholder="Add a description..."
              />
            </div>
            <div>
              <label className="text-sm font-medium">Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full mt-1 p-2 border rounded-md text-sm"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>
          <DialogFooter className="flex justify-between">
            <Button variant="destructive" onClick={handleDelete}>
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave}>Save</Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
