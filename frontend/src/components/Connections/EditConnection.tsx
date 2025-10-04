import { MenuItem } from "@/components/ui/menu"
import { FiEdit } from "react-icons/fi"
import type { ConnectionResponse } from "@/client"

interface EditConnectionProps {
  connection: ConnectionResponse
}

const EditConnection = ({ connection }: EditConnectionProps) => {
  // TODO: Implement edit functionality
  return (
    <MenuItem value="edit" disabled>
      <FiEdit />
      Edit
    </MenuItem>
  )
}

export default EditConnection
