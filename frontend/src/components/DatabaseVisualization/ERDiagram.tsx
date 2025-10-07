import { useMemo } from 'react'
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
import { Box, Grid, GridItem, Tabs } from '@chakra-ui/react'
import { FiCode, FiDatabase } from 'react-icons/fi'
import dagre from 'dagre'
import TableNode from './TableNode'
import SQLQueryBuilder from './SQLQueryBuilder'
import APIGenerator from './APIGenerator'
import { FieldSelectionProvider } from '@/contexts/FieldSelectionContext'
import { useFieldSelection } from '@/contexts/FieldSelectionContext'
import type { DiscoveredTableResponse } from '@/client'

interface ERDiagramProps {
  tables: DiscoveredTableResponse[]
}

const nodeWidth = 300
const nodeHeight = 200

const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))

  // Increase spacing between nodes to prevent overlap
  dagreGraph.setGraph({
    rankdir: 'LR',      // Left to right layout
    ranksep: 250,       // Horizontal spacing between ranks (increased from 150)
    nodesep: 150,       // Vertical spacing between nodes (increased from 100)
    edgesep: 50,        // Spacing for edges
    marginx: 50,        // Margin on x-axis
    marginy: 50         // Margin on y-axis
  })

  // Calculate dynamic node height based on number of columns
  nodes.forEach((node) => {
    const table = node.data.table
    const columnCount = Math.min(table.columns?.length || 0, 10) // Max 10 visible
    const dynamicHeight = Math.max(200, 80 + (columnCount * 32)) // Header + columns

    dagreGraph.setNode(node.id, {
      width: nodeWidth,
      height: dynamicHeight
    })

    // Store the height for later use
    node.data.calculatedHeight = dynamicHeight
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    const height = node.data.calculatedHeight || nodeHeight

    node.position = {
      x: nodeWithPosition.x - nodeWidth / 2,
      y: nodeWithPosition.y - height / 2,
    }
  })

  return { nodes, edges }
}

function ERDiagramContent({ tables }: ERDiagramProps) {
  const nodeTypes: NodeTypes = useMemo(() => ({ tableNode: TableNode }), [])
  const { setConnectionId } = useFieldSelection()

  // Set connection ID when tables are loaded
  useMemo(() => {
    if (tables.length > 0) {
      setConnectionId(tables[0].connection_id)
    }
  }, [tables, setConnectionId])

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
    <Grid templateColumns="2fr 1fr" gap={4} height="600px">
      <GridItem>
        <Box height="100%" border="1px solid" borderColor="gray.200" borderRadius="md">
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
      </GridItem>

      <GridItem>
        <Box height="100%" border="1px solid" borderColor="gray.200" borderRadius="md" overflow="hidden">
          <Tabs.Root defaultValue="sql" height="100%">
            <Tabs.List>
              <Tabs.Trigger value="sql">
                <FiDatabase /> SQL Query
              </Tabs.Trigger>
              <Tabs.Trigger value="api">
                <FiCode /> API Generator
              </Tabs.Trigger>
            </Tabs.List>

            <Tabs.Content value="sql" height="calc(100% - 48px)" overflowY="auto">
              <SQLQueryBuilder />
            </Tabs.Content>

            <Tabs.Content value="api" height="calc(100% - 48px)" overflowY="auto">
              <APIGenerator />
            </Tabs.Content>
          </Tabs.Root>
        </Box>
      </GridItem>
    </Grid>
  )
}

export default function ERDiagram({ tables }: ERDiagramProps) {
  return (
    <FieldSelectionProvider>
      <ERDiagramContent tables={tables} />
    </FieldSelectionProvider>
  )
}
