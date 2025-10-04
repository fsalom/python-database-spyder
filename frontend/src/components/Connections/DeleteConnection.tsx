import { useMutation, useQueryClient } from "@tanstack/react-query"
import { FiTrash2 } from "react-icons/fi"

import { ConnectionsService } from "@/client"
import { MenuItem } from "@/components/ui/menu"
import useCustomToast from "@/hooks/useCustomToast"

const DeleteConnection = ({ connectionId }: { connectionId: string }) => {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const deleteConnection = async (id: string) => {
    await ConnectionsService.deleteConnectionApiV1ConnectionsConnectionIdDelete({
      connectionId: parseInt(id)
    })
  }

  const mutation = useMutation({
    mutationFn: deleteConnection,
    onSuccess: () => {
      showSuccessToast("Connection deleted successfully")
    },
    onError: () => {
      showErrorToast("An error occurred while deleting the connection")
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] })
    },
  })

  const handleDelete = (e: Event) => {
    e.preventDefault()
    if (window.confirm("Are you sure you want to delete this connection?")) {
      mutation.mutate(connectionId)
    }
  }

  return (
    <MenuItem
      value="delete"
      color="red.600"
      onClick={handleDelete}
    >
      <FiTrash2 />
      Delete
    </MenuItem>
  )
}

export default DeleteConnection
