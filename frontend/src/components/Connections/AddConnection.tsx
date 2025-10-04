import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
  Select,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaPlus } from "react-icons/fa"
import { ConnectionsService, type ConnectionCreate } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddConnection = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<ConnectionCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      database_type: "postgresql",
      host: "localhost",
      port: 5432,
      username: "",
      password: "",
      database: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ConnectionCreate) =>
      ConnectionsService.createConnectionApiV1ConnectionsPost({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Connection created successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["connections"] })
    },
  })

  const onSubmit: SubmitHandler<ConnectionCreateRequest> = (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button value="add-connection" my={4}>
          <FaPlus fontSize="16px" />
          Add Connection
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Add Database Connection</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>
              Enter the connection details for your database.
            </Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.name}
                errorText={errors.name?.message}
                label="Connection Name"
              >
                <Input
                  {...register("name", {
                    required: "Connection name is required",
                  })}
                  placeholder="My Database"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.database_type}
                errorText={errors.database_type?.message}
                label="Database Type"
              >
                <select
                  {...register("database_type")}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    borderRadius: "6px",
                    border: "1px solid #e2e8f0",
                    fontSize: "14px",
                    backgroundColor: "white"
                  }}
                >
                  <option value="postgresql">PostgreSQL</option>
                  <option value="mysql">MySQL</option>
                  <option value="sqlite">SQLite</option>
                </select>
              </Field>

              <Field
                required
                invalid={!!errors.host}
                errorText={errors.host?.message}
                label="Host"
              >
                <Input
                  {...register("host", {
                    required: "Host is required",
                  })}
                  placeholder="localhost"
                  type="text"
                />
              </Field>

              <Field
                required
                invalid={!!errors.port}
                errorText={errors.port?.message}
                label="Port"
              >
                <Input
                  {...register("port", {
                    required: "Port is required",
                    valueAsNumber: true,
                  })}
                  placeholder="5432"
                  type="number"
                />
              </Field>

              <Field
                required
                invalid={!!errors.username}
                errorText={errors.username?.message}
                label="Username"
              >
                <Input
                  {...register("username", {
                    required: "Username is required",
                  })}
                  placeholder="postgres"
                  type="text"
                />
              </Field>

              <Field
                invalid={!!errors.password}
                errorText={errors.password?.message}
                label="Password"
              >
                <Input
                  {...register("password")}
                  placeholder="Password"
                  type="password"
                />
              </Field>

              <Field
                required
                invalid={!!errors.database}
                errorText={errors.database?.message}
                label="Database Name"
              >
                <Input
                  {...register("database", {
                    required: "Database name is required",
                  })}
                  placeholder="mydb"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              Save
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddConnection
