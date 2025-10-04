import { IconButton } from "@chakra-ui/react"
import { useNavigate } from "@tanstack/react-router"
import { FiEdit, FiEye, FiMoreVertical, FiRefreshCw, FiTrash2 } from "react-icons/fi"

import type { ConnectionResponse } from "@/client"
import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu"
import DeleteConnection from "./DeleteConnection"
import EditConnection from "./EditConnection"
import IntrospectConnection from "./IntrospectConnection"

interface ConnectionActionsMenuProps {
  connection: ConnectionResponse
}

export function ConnectionActionsMenu({ connection }: ConnectionActionsMenuProps) {
  const navigate = useNavigate()

  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton
          variant="ghost"
          aria-label="Connection actions"
          size="sm"
        >
          <FiMoreVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <MenuItem
          value="view"
          onClick={() => navigate({ to: `/explorer/${connection.id}` })}
        >
          <FiEye />
          Explore Database
        </MenuItem>
        <IntrospectConnection connection={connection} />
        <EditConnection connection={connection} />
        <DeleteConnection connectionId={connection.id.toString()} />
      </MenuContent>
    </MenuRoot>
  )
}
