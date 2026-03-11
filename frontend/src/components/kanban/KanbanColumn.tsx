import { useState } from 'react'
import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { KanbanCard } from './KanbanCard'
import { cardsApi } from '@/lib/api'

interface Card {
  id: string
  title: string
  description?: string
  priority: string
  position: number
  due_date?: string
}

interface List {
  id: string
  name: string
  color?: string
  position: number
  cards: Card[]
}

interface Props {
  list: List
  onDelete: () => void
  onCardUpdate: () => void
}

export function KanbanColumn({ list, onDelete, onCardUpdate }: Props) {
  const [addingCard, setAddingCard] = useState(false)
  const [newCardTitle, setNewCardTitle] = useState('')
  const [editingName, setEditingName] = useState(false)
  const [name, setName] = useState(list.name)

  const { setNodeRef, isOver } = useDroppable({
    id: list.id,
  })

  const handleAddCard = async () => {
    if (!newCardTitle.trim()) return
    try {
      await cardsApi.create(list.id, {
        title: newCardTitle.trim(),
        priority: 'medium',
      })
      setNewCardTitle('')
      setAddingCard(false)
      onCardUpdate()
    } catch (error) {
      console.error('Failed to create card:', error)
    }
  }

  return (
    <div
      ref={setNodeRef}
      className={`w-72 flex-shrink-0 bg-muted/50 rounded-lg flex flex-col max-h-full ${
        isOver ? 'ring-2 ring-primary' : ''
      }`}
    >
      {/* List Header */}
      <div className="p-3 flex items-center justify-between gap-2">
        {editingName ? (
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={() => setEditingName(false)}
            onKeyDown={(e) => e.key === 'Enter' && setEditingName(false)}
            className="h-8"
            autoFocus
          />
        ) : (
          <h3 className="font-medium truncate flex-1">{list.name}</h3>
        )}
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onDelete}>
            <Trash2 className="w-3 h-3 text-destructive" />
          </Button>
        </div>
      </div>

      {/* Cards */}
      <div className="flex-1 overflow-y-auto px-2 pb-2">
        <SortableContext items={list.cards.map((c) => c.id)} strategy={verticalListSortingStrategy}>
          {list.cards.map((card) => (
            <KanbanCard key={card.id} card={card} onUpdate={onCardUpdate} />
          ))}
        </SortableContext>

        {/* Add Card */}
        {addingCard ? (
          <div className="mt-2">
            <Input
              placeholder="Card title..."
              value={newCardTitle}
              onChange={(e) => setNewCardTitle(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAddCard()}
              autoFocus
            />
            <div className="flex gap-2 mt-2">
              <Button size="sm" onClick={handleAddCard}>
                Add
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setAddingCard(false)}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Button
            variant="ghost"
            size="sm"
            className="w-full justify-start mt-2"
            onClick={() => setAddingCard(true)}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Card
          </Button>
        )}
      </div>
    </div>
  )
}
