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
  useNodesState,
  useEdgesState,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { Box } from '@chakra-ui/react'
import dagre from 'dagre'
import TableNode from './TableNode'
import type { DiscoveredTableResponse } from '@/client'

interface ERDiagramProps {
  tables: DiscoveredTableResponse[]
}

const nodeWidth = 300
const nodeHeight = 200

const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))
  dagreGraph.setGraph({ rankdir: 'LR', ranksep: 150, nodesep: 100 })

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight })
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - nodeHeight / 2,
    }
  })

  return { nodes, edges }
}

export default function ERDiagram({ tables }: ERDiagramProps) {
  const nodeTypes: NodeTypes = useMemo(() => ({ tableNode: TableNode }), [])

  // Convert tables to nodes with handles
  const initialNodes: Node[] = useMemo(() => {
    return tables.map((table) => {
      return {
        id: table.id.toString(),
        type: 'tableNode',
        position: { x: 0, y: 0 }, // Will be set by dagre
        data: {
          table,
        },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      }
    })
  }, [tables])

  // Convert foreign keys to edges with better styling
  const initialEdges: Edge[] = useMemo(() => {
    const edgeList: Edge[] = []

    tables.forEach((table) => {
      table.columns?.forEach((column) => {
        if (column.is_foreign_key && column.foreign_key_table) {
          const targetTable = tables.find(
            (t) => t.table_name === column.foreign_key_table
          )

          if (targetTable) {
            edgeList.push({
              id: `${table.id}-${column.column_name}-${targetTable.id}`,
              source: table.id.toString(),
              target: targetTable.id.toString(),
              sourceHandle: 'right',
              targetHandle: 'left',
              label: column.column_name,
              type: 'smoothstep',
              animated: true,
              markerEnd: {
                type: MarkerType.ArrowClosed,
                width: 25,
                height: 25,
                color: '#805AD5',
              },
              style: {
                strokeWidth: 2.5,
                stroke: '#805AD5',
              },
              labelStyle: {
                fontSize: 11,
                fontWeight: 600,
                fill: '#2D3748',
              },
              labelBgStyle: {
                fill: '#fff',
                fillOpacity: 0.9,
                rx: 4,
                ry: 4,
              },
              labelBgPadding: [8, 4] as [number, number],
            })
          }
        }
      })
    })

    return edgeList
  }, [tables])

  // Apply layout
  const { nodes, edges } = useMemo(() => {
    return getLayoutedElements(initialNodes, initialEdges)
  }, [initialNodes, initialEdges])

  return (
    <Box height="600px" width="100%" border="1px solid" borderColor="gray.200" borderRadius="md">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.1}
        maxZoom={1.5}
        fitViewOptions={{ padding: 0.2 }}
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
