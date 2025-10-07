import { Badge, Container, Flex, Heading, Table, Text, Card, Box, Tabs, Button, VStack } from "@chakra-ui/react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { FiDatabase, FiTable, FiGrid, FiRefreshCw } from "react-icons/fi"
import { useState } from "react"

import { ConnectionsService, IntrospectionService } from "@/client"
import { Skeleton } from "@/components/ui/skeleton"
import ERDiagram from "@/components/DatabaseVisualization/ERDiagram"
import { toaster } from "@/components/ui/toaster"

export const Route = createFileRoute("/_layout/explorer/$connectionId")({
  component: Explorer,
})

function Explorer() {
  const { connectionId } = Route.useParams()
  const queryClient = useQueryClient()
  const [isIntrospecting, setIsIntrospecting] = useState(false)

  const { data: connection, isLoading: connectionLoading } = useQuery({
    queryKey: ["connection", connectionId],
    queryFn: () =>
      ConnectionsService.getConnectionApiV1ConnectionsConnectionIdGet({
        connectionId: parseInt(connectionId),
      }),
  })

  const { data: tables, isLoading: tablesLoading } = useQuery({
    queryKey: ["tables", connectionId],
    queryFn: () =>
      IntrospectionService.getTablesByConnectionApiV1IntrospectionConnectionsConnectionIdTablesGet({
        connectionId: parseInt(connectionId),
      }),
  })

  const introspectMutation = useMutation({
    mutationFn: () =>
      IntrospectionService.introspectDatabaseApiV1IntrospectionPost({
        requestBody: { connection_id: parseInt(connectionId) },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tables", connectionId] })
      queryClient.invalidateQueries({ queryKey: ["connection", connectionId] })
      queryClient.invalidateQueries({ queryKey: ["connections"] })
      toaster.create({
        title: "Introspection successful",
        description: "Database tables have been discovered",
        type: "success",
      })
      setIsIntrospecting(false)
    },
    onError: (error: any) => {
      queryClient.invalidateQueries({ queryKey: ["connection", connectionId] })
      queryClient.invalidateQueries({ queryKey: ["connections"] })
      toaster.create({
        title: "Introspection failed",
        description: error.body?.detail || "Failed to introspect database",
        type: "error",
      })
      setIsIntrospecting(false)
    },
  })

  const handleIntrospect = () => {
    setIsIntrospecting(true)
    introspectMutation.mutate()
  }

  if (connectionLoading) {
    return (
      <Container maxW="full">
        <Skeleton height="40px" width="300px" mt={12} mb={6} />
        <Skeleton height="20px" width="500px" mb={8} />
      </Container>
    )
  }

  if (!connection) {
    return (
      <Container maxW="full">
        <Text color="red.500" mt={12}>
          Connection not found
        </Text>
      </Container>
    )
  }

  return (
    <Container maxW="full">
      <Flex align="center" gap={3} pt={12} pb={4}>
        <FiDatabase size={32} />
        <Heading size="lg">{connection.name}</Heading>
        <Badge colorScheme="blue">{connection.db_type}</Badge>
      </Flex>

      <Text color="gray.600" mb={6}>
        {connection.host}:{connection.port} / {connection.database}
      </Text>

      {tablesLoading ? (
        <Box>
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} height="80px" mb={3} />
          ))}
        </Box>
      ) : !tables || tables.length === 0 ? (
        <Card.Root>
          <Card.Body>
            <VStack gap={4} py={8}>
              <FiDatabase size={48} color="gray" />
              <Text color="gray.500" textAlign="center" fontSize="lg">
                No tables found for this connection
              </Text>
              <Text color="gray.400" textAlign="center" fontSize="sm">
                Run introspection to discover the database structure
              </Text>
              <Button
                colorScheme="blue"
                onClick={handleIntrospect}
                loading={isIntrospecting}
                loadingText="Introspecting..."
              >
                <FiRefreshCw /> Introspect Database
              </Button>
            </VStack>
          </Card.Body>
        </Card.Root>
      ) : (
        <Tabs.Root defaultValue="diagram">
          <Tabs.List mb={4}>
            <Tabs.Trigger value="diagram">
              <FiGrid /> ER Diagram
            </Tabs.Trigger>
            <Tabs.Trigger value="list">
              <FiTable /> Tables List
            </Tabs.Trigger>
          </Tabs.List>

          <Tabs.Content value="diagram">
            <ERDiagram tables={tables} />
          </Tabs.Content>

          <Tabs.Content value="list">
            <Table.Root variant="outline">
              <Table.Header>
                <Table.Row>
                  <Table.ColumnHeader>Table Name</Table.ColumnHeader>
                  <Table.ColumnHeader>Schema</Table.ColumnHeader>
                  <Table.ColumnHeader>Columns</Table.ColumnHeader>
                  <Table.ColumnHeader>Primary Key</Table.ColumnHeader>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {tables.map((table) => (
                  <Table.Row
                    key={table.id}
                    _hover={{ bg: "gray.50", cursor: "pointer" }}
                    onClick={() => window.location.href = `/table/${table.id}`}
                  >
                    <Table.Cell>
                      <Flex align="center" gap={2}>
                        <FiTable />
                        <Text fontWeight="medium">{table.table_name}</Text>
                      </Flex>
                    </Table.Cell>
                    <Table.Cell>
                      <Badge size="sm">{table.schema_name}</Badge>
                    </Table.Cell>
                    <Table.Cell>
                      <Badge colorScheme="purple">{table.columns?.length || 0} columns</Badge>
                    </Table.Cell>
                    <Table.Cell>
                      <Text fontSize="sm" color="gray.600">
                        {table.primary_key_columns?.join(", ") || "None"}
                      </Text>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table.Root>
          </Tabs.Content>
        </Tabs.Root>
      )}
    </Container>
  )
}
