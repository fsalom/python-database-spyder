import { memo } from 'react'
import { Handle, Position } from 'reactflow'
import { Box, Text, VStack, Badge, Flex } from '@chakra-ui/react'
import { FiKey, FiLink } from 'react-icons/fi'
import type { DiscoveredTableResponse } from '@/client'

interface TableNodeProps {
  data: {
    table: DiscoveredTableResponse
  }
}

function TableNode({ data }: TableNodeProps) {
  const { table } = data

  return (
    <Box
      bg="white"
      border="2px solid"
      borderColor="blue.500"
      borderRadius="md"
      minW="280px"
      boxShadow="lg"
      _hover={{ boxShadow: 'xl' }}
      transition="box-shadow 0.2s"
    >
      {/* Handles for connections */}
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        style={{
          background: '#805AD5',
          width: 12,
          height: 12,
          border: '2px solid white'
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        style={{
          background: '#805AD5',
          width: 12,
          height: 12,
          border: '2px solid white'
        }}
      />

      {/* Table Header */}
      <Box bg="blue.500" color="white" px={3} py={2} borderTopRadius="md">
        <Text fontWeight="bold" fontSize="sm">
          {table.table_name}
        </Text>
        <Text fontSize="xs" opacity={0.9}>
          {table.schema_name}
        </Text>
      </Box>

      {/* Columns */}
      <VStack align="stretch" gap={0} maxH="300px" overflowY="auto">
        {table.columns?.slice(0, 10).map((column) => (
          <Flex
            key={column.column_name}
            px={3}
            py={1.5}
            borderBottom="1px solid"
            borderColor="gray.100"
            align="center"
            justify="space-between"
            fontSize="xs"
            _hover={{ bg: 'gray.50' }}
          >
            <Flex align="center" gap={1.5} flex={1}>
              {column.is_primary_key && (
                <FiKey color="gold" size={12} />
              )}
              {column.is_foreign_key && (
                <FiLink color="purple" size={12} />
              )}
              <Text fontWeight={column.is_primary_key ? 'bold' : 'normal'}>
                {column.column_name}
              </Text>
            </Flex>
            <Badge size="xs" colorScheme="gray" fontSize="9px">
              {column.data_type}
            </Badge>
          </Flex>
        ))}
        {table.columns && table.columns.length > 10 && (
          <Text fontSize="xs" color="gray.500" px={3} py={1} textAlign="center">
            +{table.columns.length - 10} more columns
          </Text>
        )}
      </VStack>
    </Box>
  )
}

export default memo(TableNode)
