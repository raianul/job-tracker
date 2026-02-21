"use client";

import { Switch, Table } from "@mantine/core";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getApiUrl } from "@/lib/api";
import { getAuthHeaders } from "@/lib/auth";
import { PageContainer } from "@/components/PageContainer/PageContainer";

interface UserRow {
  id: number;
  email: string;
  name: string | null;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
}

export default function AdminUsersPage() {
  const queryClient = useQueryClient();
  const { data: users = [], isLoading } = useQuery<UserRow[]>({
    queryKey: ["admin-users"],
    queryFn: async () => {
      const res = await fetch(getApiUrl("/api/admin/users"), {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error("Forbidden");
      return res.json();
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({
      userId,
      is_admin,
      is_active,
    }: {
      userId: number;
      is_admin?: boolean;
      is_active?: boolean;
    }) => {
      const body: Record<string, boolean> = {};
      if (is_admin !== undefined) body.is_admin = is_admin;
      if (is_active !== undefined) body.is_active = is_active;
      const res = await fetch(getApiUrl(`/api/admin/users/${userId}`), {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-users"] }),
  });

  return (
    <PageContainer title="Users">
      <Table striped highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Email</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Admin</Table.Th>
            <Table.Th>Active</Table.Th>
            <Table.Th>Created</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {isLoading ? (
            <Table.Tr>
              <Table.Td colSpan={5}>Loading...</Table.Td>
            </Table.Tr>
          ) : (
            users.map((u) => (
              <Table.Tr key={u.id}>
                <Table.Td>{u.email}</Table.Td>
                <Table.Td>{u.name || "—"}</Table.Td>
                <Table.Td>
                  <Switch
                    size="sm"
                    checked={u.is_admin}
                    onChange={(e) =>
                      updateMutation.mutate({
                        userId: u.id,
                        is_admin: e.currentTarget.checked,
                      })
                    }
                    disabled={updateMutation.isPending}
                  />
                </Table.Td>
                <Table.Td>
                  <Switch
                    size="sm"
                    checked={u.is_active}
                    onChange={(e) =>
                      updateMutation.mutate({
                        userId: u.id,
                        is_active: e.currentTarget.checked,
                      })
                    }
                    disabled={updateMutation.isPending}
                  />
                </Table.Td>
                <Table.Td>{new Date(u.created_at).toLocaleDateString()}</Table.Td>
              </Table.Tr>
            ))
          )}
        </Table.Tbody>
      </Table>
    </PageContainer>
  );
}
