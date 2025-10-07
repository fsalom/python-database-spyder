import { createContext, useContext, useState, ReactNode } from 'react'

export interface SelectedField {
  tableId: number
  tableName: string
  columnName: string
  dataType: string
  isPrimaryKey: boolean
  isForeignKey: boolean
  foreignKeyTable?: string | null
  foreignKeyColumn?: string | null
}

interface FieldSelectionContextType {
  selectedFields: SelectedField[]
  addField: (field: SelectedField) => void
  removeField: (tableId: number, columnName: string) => void
  isFieldSelected: (tableId: number, columnName: string) => boolean
  clearSelection: () => void
  connectionId: number | null
  setConnectionId: (id: number | null) => void
}

const FieldSelectionContext = createContext<FieldSelectionContextType | undefined>(undefined)

export function FieldSelectionProvider({ children }: { children: ReactNode }) {
  const [selectedFields, setSelectedFields] = useState<SelectedField[]>([])
  const [connectionId, setConnectionId] = useState<number | null>(null)

  const addField = (field: SelectedField) => {
    setSelectedFields((prev) => {
      const exists = prev.some(
        (f) => f.tableId === field.tableId && f.columnName === field.columnName
      )
      if (exists) return prev
      return [...prev, field]
    })
  }

  const removeField = (tableId: number, columnName: string) => {
    setSelectedFields((prev) =>
      prev.filter((f) => !(f.tableId === tableId && f.columnName === columnName))
    )
  }

  const isFieldSelected = (tableId: number, columnName: string) => {
    return selectedFields.some(
      (f) => f.tableId === tableId && f.columnName === columnName
    )
  }

  const clearSelection = () => {
    setSelectedFields([])
  }

  return (
    <FieldSelectionContext.Provider
      value={{ selectedFields, addField, removeField, isFieldSelected, clearSelection, connectionId, setConnectionId }}
    >
      {children}
    </FieldSelectionContext.Provider>
  )
}

export function useFieldSelection() {
  const context = useContext(FieldSelectionContext)
  if (context === undefined) {
    throw new Error('useFieldSelection must be used within a FieldSelectionProvider')
  }
  return context
}
