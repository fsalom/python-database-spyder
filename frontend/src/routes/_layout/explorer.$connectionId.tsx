import { Badge, Container, Flex, Heading, Table, Text, Card, Box, Tabs } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { FiDatabase, FiTable, FiGrid } from "react-icons/fi"

import { ConnectionsService, IntrospectionService } from "@/client"
import { Skeleton } from "@/components/ui/skeleton"
import ERDiagram from "@/components/DatabaseVisualization/ERDiagram"

export const Route = createFileRoute("/_layout/explorer/$connectionId")({
  component: Explorer,
})

function Explorer() {
  const { connectionId } = Route.useParams()

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
            <Text color="gray.500" textAlign="center">
              No tables found. Click "Introspect Database" to discover tables.
            </Text>
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
            <Table.Root>
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
                    asChild
                  >
                    <Link to={`/table/${table.id}`}>
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
                    </Link>
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
