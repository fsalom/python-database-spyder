import { useMemo, useState } from 'react'
import { Box, Heading, Text, Code, Button, VStack, HStack, Badge, Table, Spinner } from '@chakra-ui/react'
import { FiCopy, FiTrash2, FiPlay } from 'react-icons/fi'
import { useFieldSelection } from '@/contexts/FieldSelectionContext'
import { toaster } from '@/components/ui/toaster'
import { QueryService } from '@/client'
import type { ExecuteQueryResponse } from '@/client'

export default function SQLQueryBuilder() {
  const { selectedFields, clearSelection, connectionId } = useFieldSelection()
  const [queryResult, setQueryResult] = useState<ExecuteQueryResponse | null>(null)
  const [isExecuting, setIsExecuting] = useState(false)

  const sqlQuery = useMemo(() => {
    if (selectedFields.length === 0) {
      return ''
    }

    // Group fields by table
    const tableGroups = selectedFields.reduce((acc, field) => {
      if (!acc[field.tableName]) {
        acc[field.tableName] = []
      }
      acc[field.tableName].push(field)
      return acc
    }, {} as Record<string, typeof selectedFields>)

    const tables = Object.keys(tableGroups)

    if (tables.length === 1) {
      // Simple single table query
      const tableName = tables[0]
      const columns = tableGroups[tableName].map(f => `  ${f.columnName}`).join(',\n')
      return `SELECT\n${columns}\nFROM ${tableName};`
    }

    // Multiple tables - build JOIN query
    const mainTable = tables[0]
    const mainColumns = tableGroups[mainTable].map(f => `  ${mainTable}.${f.columnName}`).join(',\n')

    let query = `SELECT\n${mainColumns}`

    // Add columns from other tables
    for (let i = 1; i < tables.length; i++) {
      const table = tables[i]
      const columns = tableGroups[table].map(f => `,\n  ${table}.${f.columnName}`)
      query += columns.join('')
    }

    query += `\nFROM ${mainTable}`

    // Add JOINs based on foreign keys
    for (let i = 1; i < tables.length; i++) {
      const table = tables[i]
      const fields = tableGroups[table]

      // Try to find a FK relationship
      const fkToMain = fields.find(f => f.foreignKeyTable === mainTable)
      const mainFieldsWithFk = tableGroups[mainTable].find(f => f.foreignKeyTable === table)

      if (fkToMain) {
        query += `\nLEFT JOIN ${table} ON ${mainTable}.${fkToMain.foreignKeyColumn} = ${table}.${fkToMain.columnName}`
      } else if (mainFieldsWithFk) {
        query += `\nLEFT JOIN ${table} ON ${mainTable}.${mainFieldsWithFk.columnName} = ${table}.${mainFieldsWithFk.foreignKeyColumn}`
      } else {
        query += `\n-- TODO: Add JOIN condition for ${table}`
      }
    }

    query += ';'
    return query
  }, [selectedFields])

  const handleCopy = async () => {
    if (sqlQuery) {
      await navigator.clipboard.writeText(sqlQuery)
      toaster.create({
        title: 'Copied to clipboard!',
        type: 'success',
        duration: 2000,
      })
    }
  }

  const handleExecute = async () => {
    if (!sqlQuery || !connectionId) return

    setIsExecuting(true)
    setQueryResult(null)

    try {
      const result = await QueryService.executeQueryApiV1QueryExecutePost({
        requestBody: {
          connection_id: connectionId,
          query: sqlQuery,
          limit: 100,
        },
      })

      setQueryResult(result)
      toaster.create({
        title: 'Query executed successfully!',
        description: `${result.row_count} rows returned in ${result.execution_time_ms}ms`,
        type: 'success',
        duration: 3000,
      })
    } catch (error: any) {
      toaster.create({
        title: 'Query execution failed',
        description: error.body?.detail || 'An error occurred',
        type: 'error',
        duration: 5000,
      })
    } finally {
      setIsExecuting(false)
    }
  }

  if (selectedFields.length === 0) {
    return (
      <Box p={4} textAlign="center">
        <Text color="gray.500" fontSize="sm">
          Select fields from the tables to generate SQL query
        </Text>
      </Box>
    )
  }

  return (
    <VStack align="stretch" gap={3} p={4}>
      <HStack justify="space-between">
        <Heading size="sm">Generated SQL Query</Heading>
        <HStack>
          <Badge colorScheme="blue">{selectedFields.length} fields selected</Badge>
          <Button size="xs" variant="ghost" colorScheme="red" onClick={clearSelection} title="Clear selection">
            <FiTrash2 />
          </Button>
          <Button size="xs" onClick={handleCopy} title="Copy to clipboard">
            <FiCopy /> Copy
          </Button>
          <Button
            size="xs"
            colorScheme="green"
            onClick={handleExecute}
            disabled={isExecuting || !connectionId}
            title="Execute query"
          >
            {isExecuting ? <Spinner size="sm" /> : <FiPlay />} Execute
          </Button>
        </HStack>
      </HStack>

      <Box
        bg="gray.900"
        p={4}
        borderRadius="md"
        overflowX="auto"
        maxH="300px"
        overflowY="auto"
      >
        <Code
          colorScheme="blue"
          fontSize="sm"
          display="block"
          whiteSpace="pre"
          color="green.300"
          bg="transparent"
        >
          {sqlQuery}
        </Code>
      </Box>

      <Box>
        <Text fontSize="xs" color="gray.600" fontWeight="semibold" mb={2}>
          Selected Fields:
        </Text>
        <HStack wrap="wrap" gap={1}>
          {selectedFields.map((field) => (
            <Badge
              key={`${field.tableId}-${field.columnName}`}
              size="sm"
              colorScheme={field.isPrimaryKey ? 'yellow' : field.isForeignKey ? 'purple' : 'gray'}
            >
              {field.tableName}.{field.columnName}
            </Badge>
          ))}
        </HStack>
      </Box>

      {queryResult && (
        <Box>
          <HStack justify="space-between" mb={2}>
            <Heading size="xs">Query Results</Heading>
            <HStack gap={2}>
              <Badge colorScheme="green">{queryResult.row_count} rows</Badge>
              <Badge colorScheme="blue">{queryResult.execution_time_ms}ms</Badge>
            </HStack>
          </HStack>
          <Box
            border="1px solid"
            borderColor="gray.200"
            borderRadius="md"
            overflowX="auto"
            maxH="400px"
            overflowY="auto"
          >
            <Table.Root size="sm" variant="outline">
              <Table.Header>
                <Table.Row>
                  {queryResult.columns.map((col) => (
                    <Table.ColumnHeader key={col} fontWeight="bold" bg="gray.50">
                      {col}
                    </Table.ColumnHeader>
                  ))}
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {queryResult.rows.map((row, idx) => (
                  <Table.Row key={idx}>
                    {queryResult.columns.map((col) => (
                      <Table.Cell key={col} fontSize="xs">
                        {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                      </Table.Cell>
                    ))}
                  </Table.Row>
                ))}
              </Table.Body>
            </Table.Root>
          </Box>
        </Box>
      )}
    </VStack>
  )
}
