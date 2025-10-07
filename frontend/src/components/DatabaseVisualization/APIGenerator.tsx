import { useMemo, useState } from 'react'
import { Box, Heading, Text, Code, Button, VStack, HStack, Badge, Input } from '@chakra-ui/react'
import { FiCopy, FiTrash2, FiDownload } from 'react-icons/fi'
import { useFieldSelection } from '@/contexts/FieldSelectionContext'
import { toaster } from '@/components/ui/toaster'
import { Field } from '@/components/ui/field'

export default function APIGenerator() {
  const { selectedFields, clearSelection } = useFieldSelection()
  const [endpointName, setEndpointName] = useState('')

  const apiCode = useMemo(() => {
    if (selectedFields.length === 0) {
      return { pydantic: '', fastapi: '' }
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
    const mainTable = tables[0]
    const modelName = endpointName || mainTable.charAt(0).toUpperCase() + mainTable.slice(1).replace(/_/g, '')

    // Generate Pydantic schema
    const pydanticFields = selectedFields.map(f => {
      const pythonType = getPythonType(f.dataType)
      const optional = !f.isPrimaryKey ? ' | None = None' : ''
      return `    ${f.columnName}: ${pythonType}${optional}`
    }).join('\n')

    const pydanticSchema = `from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ${modelName}Response(BaseModel):
${pydanticFields}

    model_config = {"from_attributes": True}`

    // Generate FastAPI endpoint
    const routeName = endpointName.toLowerCase() || mainTable
    const fastapiEndpoint = `from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

router = APIRouter()

@router.get("/${routeName}", response_model=List[${modelName}Response])
async def get_${routeName}(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve ${routeName} with selected fields:
    ${selectedFields.map(f => `- ${f.tableName}.${f.columnName}`).join('\n    ')}
    """
    # TODO: Implement query logic based on your ORM models
    query = select(${mainTable})${tables.length > 1 ? `.join(...)  # Add joins` : ''}
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()`

    return { pydantic: pydanticSchema, fastapi: fastapiEndpoint }
  }, [selectedFields, endpointName])

  const handleCopy = async (code: string) => {
    if (code) {
      await navigator.clipboard.writeText(code)
      toaster.create({
        title: 'Copied to clipboard!',
        type: 'success',
        duration: 2000,
      })
    }
  }

  const handleDownload = () => {
    const blob = new Blob(
      [`# Pydantic Schema\n\n${apiCode.pydantic}\n\n# FastAPI Endpoint\n\n${apiCode.fastapi}`],
      { type: 'text/plain' }
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${endpointName || 'api'}_generated.py`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (selectedFields.length === 0) {
    return (
      <Box p={4} textAlign="center">
        <Text color="gray.500" fontSize="sm">
          Select fields from the tables to generate API code
        </Text>
      </Box>
    )
  }

  return (
    <VStack align="stretch" gap={3} p={4}>
      <HStack justify="space-between">
        <Heading size="sm">Generated API Code</Heading>
        <HStack>
          <Badge colorScheme="blue">{selectedFields.length} fields selected</Badge>
          <Button size="xs" variant="ghost" colorScheme="red" onClick={clearSelection} title="Clear selection">
            <FiTrash2 />
          </Button>
          <Button size="xs" onClick={handleDownload} title="Download Python file">
            <FiDownload /> Download
          </Button>
        </HStack>
      </HStack>

      <Field label="Endpoint Name (optional)">
        <Input
          size="sm"
          placeholder="e.g., UserOrders"
          value={endpointName}
          onChange={(e) => setEndpointName(e.target.value)}
        />
      </Field>

      {/* Pydantic Schema */}
      <Box>
        <HStack justify="space-between" mb={2}>
          <Text fontSize="sm" fontWeight="semibold">Pydantic Schema</Text>
          <Button size="xs" variant="ghost" onClick={() => handleCopy(apiCode.pydantic)}>
            <FiCopy /> Copy
          </Button>
        </HStack>
        <Box
          bg="gray.900"
          p={4}
          borderRadius="md"
          overflowX="auto"
          maxH="250px"
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
            {apiCode.pydantic}
          </Code>
        </Box>
      </Box>

      {/* FastAPI Endpoint */}
      <Box>
        <HStack justify="space-between" mb={2}>
          <Text fontSize="sm" fontWeight="semibold">FastAPI Endpoint</Text>
          <Button size="xs" variant="ghost" onClick={() => handleCopy(apiCode.fastapi)}>
            <FiCopy /> Copy
          </Button>
        </HStack>
        <Box
          bg="gray.900"
          p={4}
          borderRadius="md"
          overflowX="auto"
          maxH="250px"
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
            {apiCode.fastapi}
          </Code>
        </Box>
      </Box>
    </VStack>
  )
}

function getPythonType(dataType: string): string {
  const type = dataType.toUpperCase()
  if (type.includes('INT')) return 'int'
  if (type.includes('FLOAT') || type.includes('DOUBLE') || type.includes('DECIMAL')) return 'float'
  if (type.includes('BOOL')) return 'bool'
  if (type.includes('DATE') || type.includes('TIME')) return 'datetime'
  if (type.includes('TEXT') || type.includes('VARCHAR') || type.includes('CHAR')) return 'str'
  return 'str'
}
