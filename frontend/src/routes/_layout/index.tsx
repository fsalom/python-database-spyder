import { Box, Container, Text, Grid, GridItem, Card, Heading, Badge, SimpleGrid, Flex, Icon } from "@chakra-ui/react"
import { createFileRoute, Link } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { FiDatabase, FiCheckCircle, FiXCircle, FiAlertCircle, FiTable, FiGitBranch } from "react-icons/fi"

import useAuth from "@/hooks/useAuth"
import { DashboardService } from "@/client"
import { Skeleton } from "@/components/ui/skeleton"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

interface StatCardProps {
  title: string
  value: number
  icon: React.ElementType
  colorScheme: string
}

function StatCard({ title, value, icon, colorScheme }: StatCardProps) {
  return (
    <Card.Root>
      <Card.Body>
        <Flex justify="space-between" align="center">
          <Box>
            <Text fontSize="sm" color="gray.600" mb={1}>{title}</Text>
            <Text fontSize="3xl" fontWeight="bold">{value}</Text>
          </Box>
          <Icon as={icon} boxSize={12} color={`${colorScheme}.500`} />
        </Flex>
      </Card.Body>
    </Card.Root>
  )
}

function Dashboard() {
  const { user: currentUser } = useAuth()

  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => DashboardService.getDashboardStatsApiV1DashboardGet(),
  })

  return (
    <Container maxW="full">
      <Box pt={12} pb={4}>
        <Text fontSize="2xl" fontWeight="bold" mb={2}>
          Hi, {currentUser?.full_name || currentUser?.email} 👋
        </Text>
        <Text color="gray.600" mb={6}>Welcome back! Here's what's happening with your databases.</Text>
      </Box>

      {isLoading ? (
        <>
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={4} mb={8}>
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} height="120px" />
            ))}
          </SimpleGrid>
          <Skeleton height="300px" />
        </>
      ) : dashboardData ? (
        <>
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={4} mb={8}>
            <StatCard
              title="Total Connections"
              value={dashboardData.stats.total_connections}
              icon={FiDatabase}
              colorScheme="blue"
            />
            <StatCard
              title="Active Connections"
              value={dashboardData.stats.active_connections}
              icon={FiCheckCircle}
              colorScheme="green"
            />
            <StatCard
              title="Total Tables"
              value={dashboardData.stats.total_tables}
              icon={FiTable}
              colorScheme="purple"
            />
            <StatCard
              title="Total Relations"
              value={dashboardData.stats.total_relations}
              icon={FiGitBranch}
              colorScheme="orange"
            />
          </SimpleGrid>

          {dashboardData.recent_connections.length > 0 && (
            <Card.Root>
              <Card.Header>
                <Heading size="md">Recent Connections</Heading>
              </Card.Header>
              <Card.Body>
                <Box>
                  {dashboardData.recent_connections.map((connection) => (
                    <Link
                      key={connection.id}
                      to="/explorer/$connectionId"
                      params={{ connectionId: connection.id.toString() }}
                      style={{ textDecoration: 'none' }}
                    >
                      <Flex
                        justify="space-between"
                        align="center"
                        p={3}
                        borderRadius="md"
                        _hover={{ bg: "gray.50", cursor: "pointer" }}
                        mb={2}
                      >
                        <Flex align="center" gap={3}>
                          <Icon as={FiDatabase} boxSize={5} color="blue.500" />
                          <Box>
                            <Text fontWeight="medium">{connection.name}</Text>
                            <Text fontSize="sm" color="gray.600">
                              {connection.host}:{connection.port} / {connection.database}
                            </Text>
                          </Box>
                        </Flex>
                        <Flex align="center" gap={2}>
                          <Badge colorScheme="blue">{connection.database_type}</Badge>
                          <Badge
                            colorScheme={
                              connection.status === "active" ? "green" :
                              connection.status === "error" ? "red" :
                              "gray"
                            }
                          >
                            {connection.status === "active" ? <FiCheckCircle /> : connection.status === "error" ? <FiXCircle /> : <FiAlertCircle />}
                            {" "}{connection.status}
                          </Badge>
                        </Flex>
                      </Flex>
                    </Link>
                  ))}
                </Box>
              </Card.Body>
            </Card.Root>
          )}
        </>
      ) : (
        <Text color="gray.500">No data available</Text>
      )}
    </Container>
  )
}
