import { useMutation, useQueryClient } from "@tanstack/react-query"
import { FiRefreshCw } from "react-icons/fi"

import { IntrospectionService } from "@/client"
import { MenuItem } from "@/components/ui/menu"
import useCustomToast from "@/hooks/useCustomToast"
import type { ConnectionResponse } from "@/client"

interface IntrospectConnectionProps {
  connection: ConnectionResponse
}

const IntrospectConnection = ({ connection }: IntrospectConnectionProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () =>
      IntrospectionService.introspectDatabaseApiV1IntrospectionPost({
        requestBody: { connection_id: connection.id }
      }),
    onSuccess: (data) => {
      showSuccessToast(`Discovered ${data.tables_count} tables with ${data.relations_count} relations`)
      queryClient.invalidateQueries({ queryKey: ["tables", connection.id] })
      queryClient.invalidateQueries({ queryKey: ["connection", connection.id] })
      queryClient.invalidateQueries({ queryKey: ["connections"] })
    },
    onError: () => {
      showErrorToast("Failed to introspect database")
      queryClient.invalidateQueries({ queryKey: ["connection", connection.id] })
      queryClient.invalidateQueries({ queryKey: ["connections"] })
    },
  })

  const handleIntrospect = (e: Event) => {
    e.preventDefault()
    mutation.mutate()
  }

  return (
    <MenuItem
      value="introspect"
      onClick={handleIntrospect}
      disabled={mutation.isPending}
    >
      <FiRefreshCw />
      {mutation.isPending ? "Introspecting..." : "Introspect Database"}
    </MenuItem>
  )
}

export default IntrospectConnection
