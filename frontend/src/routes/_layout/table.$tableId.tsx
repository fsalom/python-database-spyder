import { Badge, Container, Flex, Heading, Table, Text, Card, Box, Tabs } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { FiTable, FiKey, FiLink } from "react-icons/fi"

import { IntrospectionService } from "@/client"
import { Skeleton } from "@/components/ui/skeleton"

export const Route = createFileRoute("/_layout/table/$tableId")({
  component: TableDetail,
})

function TableDetail() {
  const { tableId } = Route.useParams()

  const { data: table, isLoading } = useQuery({
    queryKey: ["table", tableId],
    queryFn: () =>
      IntrospectionService.getTableApiV1IntrospectionTablesTableIdGet({
        tableId: parseInt(tableId),
      }),
  })

  if (isLoading) {
    return (
      <Container maxW="full">
        <Skeleton height="40px" width="300px" mt={12} mb={6} />
        <Skeleton height="300px" />
      </Container>
    )
  }

  if (!table) {
    return (
      <Container maxW="full">
        <Text color="red.500" mt={12}>
          Table not found
        </Text>
      </Container>
    )
  }

  return (
    <Container maxW="full">
      <Flex align="center" gap={3} pt={12} pb={4}>
        <FiTable size={32} />
        <Heading size="lg">{table.table_name}</Heading>
        <Badge size="sm">{table.schema_name}</Badge>
      </Flex>

      <Tabs.Root defaultValue="columns" variant="enclosed">
        <Tabs.List mb={4}>
          <Tabs.Trigger value="columns">
            Columns ({table.columns?.length || 0})
          </Tabs.Trigger>
          <Tabs.Trigger value="relations">
            Relations
          </Tabs.Trigger>
        </Tabs.List>

        <Tabs.Content value="columns">
          <Table.Root>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader>Column Name</Table.ColumnHeader>
                <Table.ColumnHeader>Data Type</Table.ColumnHeader>
                <Table.ColumnHeader>Nullable</Table.ColumnHeader>
                <Table.ColumnHeader>Default</Table.ColumnHeader>
                <Table.ColumnHeader>Keys</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {table.columns?.map((column) => (
                <Table.Row key={column.column_name}>
                  <Table.Cell>
                    <Text fontWeight="medium">{column.column_name}</Text>
                  </Table.Cell>
                  <Table.Cell>
                    <Badge colorScheme="blue">{column.data_type}</Badge>
                  </Table.Cell>
                  <Table.Cell>
                    {column.is_nullable ? (
                      <Badge colorScheme="gray">Nullable</Badge>
                    ) : (
                      <Badge colorScheme="red">Not Null</Badge>
                    )}
                  </Table.Cell>
                  <Table.Cell>
                    <Text fontSize="sm" color="gray.600">
                      {column.column_default || "-"}
                    </Text>
                  </Table.Cell>
                  <Table.Cell>
                    <Flex gap={1}>
                      {table.primary_key_columns?.includes(column.column_name) && (
                        <Badge colorScheme="yellow">
                          <FiKey /> PK
                        </Badge>
                      )}
                      {column.is_foreign_key && (
                        <Badge colorScheme="purple">
                          <FiLink /> FK
                        </Badge>
                      )}
                    </Flex>
                  </Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table.Root>
        </Tabs.Content>

        <Tabs.Content value="relations">
          <Card.Root>
            <Card.Body>
              <Text color="gray.500" textAlign="center">
                Relations view coming soon
              </Text>
            </Card.Body>
          </Card.Root>
        </Tabs.Content>
      </Tabs.Root>
    </Container>
  )
}
