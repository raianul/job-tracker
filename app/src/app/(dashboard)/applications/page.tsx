"use client";

import { Anchor, Badge, Box, Button, Group, Select, Table, TextInput } from "@mantine/core";
import { IconExternalLink } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { getApiUrl } from "../../../lib/api";
import { getAuthHeaders } from "../../../lib/auth";
import { PageContainer } from "@/components/PageContainer/PageContainer";
import { useState } from "react";

interface AppItem {
  id: number;
  source_url: string;
  applied_at: string;
  status: string;
  created_at: string;
  title: string | null;
  company: string | null;
  source_domain: string | null;
}

export default function ApplicationsPage() {
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const { data: apps = [], isLoading } = useQuery<AppItem[]>({
    queryKey: ["applications", statusFilter, search],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (statusFilter) params.set("status", statusFilter);
      if (search) params.set("search", search);
      const url = getApiUrl("/api/applications?" + params.toString());
      const res = await fetch(url, { headers: getAuthHeaders() });
      if (!res.ok) throw new Error("Failed to fetch");
      return res.json();
    },
  });

  return (
    <PageContainer title="Applications">
      <Group justify="space-between" mb="md">
        <Group gap="sm">
          <Select
            placeholder="Status"
            clearable
            data={[
              { value: "applied", label: "Applied" },
              { value: "in_progress", label: "In progress" },
              { value: "done", label: "Done" },
              { value: "rejected", label: "Rejected" },
              { value: "got_offer", label: "Got offer" },
            ]}
            value={statusFilter}
            onChange={setStatusFilter}
            w={160}
          />
          <TextInput
            placeholder="Search title or company"
            value={search}
            onChange={(e) => setSearch(e.currentTarget.value)}
            style={{ minWidth: 200 }}
          />
        </Group>
        <Button onClick={() => router.push("/applications/new")}>
          Add application
        </Button>
      </Group>
      <Table striped highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Title</Table.Th>
            <Table.Th>Company</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Applied</Table.Th>
            <Table.Th>Source</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {isLoading ? (
            <Table.Tr>
              <Table.Td colSpan={5}>Loading...</Table.Td>
            </Table.Tr>
          ) : (
            apps.map((app) => (
              <Table.Tr
                key={app.id}
                style={{ cursor: "pointer" }}
                onClick={() => router.push(`/applications/${app.id}`)}
              >
                <Table.Td>{app.title || "—"}</Table.Td>
                <Table.Td>{app.company || "—"}</Table.Td>
                <Table.Td>
                  <Badge size="sm" variant="light">
                    {app.status.replace("_", " ")}
                  </Badge>
                </Table.Td>
                <Table.Td>{new Date(app.applied_at).toLocaleDateString()}</Table.Td>
                <Table.Td onClick={(e) => e.stopPropagation()}>
                  {app.source_url ? (
                    <Anchor
                      href={app.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      size="sm"
                      inline
                    >
                      <Group gap={4} wrap="nowrap">
                        {app.source_domain || "Job link"}
                        <IconExternalLink size={14} />
                      </Group>
                    </Anchor>
                  ) : (
                    "—"
                  )}
                </Table.Td>
              </Table.Tr>
            ))
          )}
        </Table.Tbody>
      </Table>
      {!isLoading && apps.length === 0 && (
        <Box py="xl" ta="center">
          <p>No applications yet.</p>
          <Button mt="sm" onClick={() => router.push("/applications/new")}>
            Add your first application
          </Button>
        </Box>
      )}
    </PageContainer>
  );
}
