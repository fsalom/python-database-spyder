import { Badge, Container, Flex, Heading, Table, Text } from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"

import { ConnectionsService } from "@/client"
import AddConnection from "@/components/Connections/AddConnection"
import { ConnectionActionsMenu } from "@/components/Connections/ConnectionActionsMenu"
import { Skeleton } from "@/components/ui/skeleton"

export const Route = createFileRoute("/_layout/connections")({
  component: Connections,
})

function ConnectionsTable() {
  const queryClient = useQueryClient()

  const { data: connections, isLoading } = useQuery({
    queryKey: ["connections"],
    queryFn: () => ConnectionsService.getAllConnectionsApiV1ConnectionsGet(),
  })

  if (isLoading) {
    return (
      <Table.Root>
        <Table.Body>
          {[1, 2, 3].map((i) => (
            <Table.Row key={i}>
              <Table.Cell><Skeleton height="20px" /></Table.Cell>
              <Table.Cell><Skeleton height="20px" /></Table.Cell>
              <Table.Cell><Skeleton height="20px" /></Table.Cell>
              <Table.Cell><Skeleton height="20px" /></Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
    )
  }

  if (!connections || connections.length === 0) {
    return (
      <Text color="gray.500" textAlign="center" py={8}>
        No database connections found. Create your first connection to get started.
      </Text>
    )
  }

  return (
    <Table.Root size={{ base: "sm", md: "md" }}>
      <Table.Header>
        <Table.Row>
          <Table.ColumnHeader>Name</Table.ColumnHeader>
          <Table.ColumnHeader>Database Type</Table.ColumnHeader>
          <Table.ColumnHeader>Host</Table.ColumnHeader>
          <Table.ColumnHeader>Status</Table.ColumnHeader>
          <Table.ColumnHeader>Actions</Table.ColumnHeader>
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {connections.map((connection) => (
          <Table.Row key={connection.id}>
            <Table.Cell fontWeight="medium">
              <Link
                to="/explorer/$connectionId"
                params={{ connectionId: connection.id.toString() }}
                style={{ color: '#3182CE', textDecoration: 'none' }}
                onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
              >
                {connection.name}
              </Link>
            </Table.Cell>
            <Table.Cell>
              <Badge colorScheme="blue">{connection.database_type}</Badge>
            </Table.Cell>
            <Table.Cell>{connection.host}:{connection.port}</Table.Cell>
            <Table.Cell>
              <Badge
                colorScheme={
                  connection.status === "active" ? "green" :
                  connection.status === "error" ? "red" :
                  "gray"
                }
              >
                {connection.status === "active" ? "Active" :
                 connection.status === "error" ? "Error" :
                 "Inactive"}
              </Badge>
            </Table.Cell>
            <Table.Cell>
              <ConnectionActionsMenu connection={connection} />
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    </Table.Root>
  )
}

function Connections() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12} pb={4}>
        Database Connections
      </Heading>
      <Text color="gray.600" mb={6}>
        Manage your database connections. Add new connections to explore their structure and create dynamic APIs.
      </Text>

      <AddConnection />
      <ConnectionsTable />
    </Container>
  )
}
