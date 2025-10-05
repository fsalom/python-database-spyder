import { useCallback, useMemo } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  NodeTypes,
  Position,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Box } from '@chakra-ui/react'
import TableNode from './TableNode'
import type { DiscoveredTableResponse } from '@/client'

interface ERDiagramProps {
  tables: DiscoveredTableResponse[]
}

export default function ERDiagram({ tables }: ERDiagramProps) {
  const nodeTypes: NodeTypes = useMemo(() => ({ tableNode: TableNode }), [])

  // Convert tables to nodes
  const nodes: Node[] = useMemo(() => {
    return tables.map((table, index) => {
      const x = (index % 3) * 400 + 50
      const y = Math.floor(index / 3) * 300 + 50

      return {
        id: table.id.toString(),
        type: 'tableNode',
        position: { x, y },
        data: {
          table,
        },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      }
    })
  }, [tables])

  // Convert foreign keys to edges
  const edges: Edge[] = useMemo(() => {
    const edgeList: Edge[] = []

    console.log('DEBUG: Building edges from tables:', tables)

    tables.forEach((table) => {
      console.log(`DEBUG: Processing table ${table.table_name}, columns:`, table.columns)
      table.columns?.forEach((column) => {
        console.log(`DEBUG: Column ${column.column_name}: is_fk=${column.is_foreign_key}, fk_table=${column.foreign_key_table}`)
        if (column.is_foreign_key && column.foreign_key_table) {
          const targetTable = tables.find(
            (t) => t.table_name === column.foreign_key_table
          )

          console.log(`DEBUG: Found target table for ${column.column_name}:`, targetTable)

          if (targetTable) {
            const edge = {
              id: `${table.id}-${column.column_name}-${targetTable.id}`,
              source: table.id.toString(),
              target: targetTable.id.toString(),
              label: column.column_name,
              type: 'smoothstep',
              animated: true,
              markerEnd: {
                type: MarkerType.ArrowClosed,
                width: 20,
                height: 20,
              },
              style: {
                strokeWidth: 2,
                stroke: '#805AD5',
              },
              labelStyle: {
                fontSize: 12,
                fontWeight: 500,
              },
              labelBgStyle: {
                fill: '#fff',
              },
            }
            console.log('DEBUG: Adding edge:', edge)
            edgeList.push(edge)
          }
        }
      })
    })

    console.log('DEBUG: Total edges created:', edgeList.length, edgeList)
    return edgeList
  }, [tables])

  return (
    <Box height="600px" width="100%" border="1px solid" borderColor="gray.200" borderRadius="md">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={1.5}
      >
        <Background />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            return '#4299E1'
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </Box>
  )
}
