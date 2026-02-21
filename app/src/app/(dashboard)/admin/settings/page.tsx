"use client";

import { Button, Card, Stack, Switch, TextInput } from "@mantine/core";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getApiUrl } from "lib/api";
import { getAuthHeaders } from "lib/auth";
import { PageContainer } from "@/components/PageContainer/PageContainer";
import { useState, useEffect } from "react";

export default function AdminSettingsPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["admin-settings"],
    queryFn: async () => {
      const res = await fetch(getApiUrl("/api/admin/settings"), {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error("Forbidden");
      return res.json();
    },
  });

  const [siteName, setSiteName] = useState("");
  const [maintenanceMode, setMaintenanceMode] = useState(false);

  useEffect(() => {
    if (data) {
      setSiteName(data.site_name || "");
      setMaintenanceMode(data.maintenance_mode ?? false);
    }
  }, [data]);

  const mutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(getApiUrl("/api/admin/settings"), {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({
          site_name: siteName,
          maintenance_mode: maintenanceMode,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-settings"] }),
  });

  return (
    <PageContainer title="Website settings">
      <Card withBorder maw={500}>
        {isLoading ? (
          <p>Loading...</p>
        ) : (
          <Stack gap="md">
            <TextInput
              label="Site name"
              value={siteName}
              onChange={(e) => setSiteName(e.currentTarget.value)}
            />
            <Switch
              label="Maintenance mode"
              checked={maintenanceMode}
              onChange={(e) => setMaintenanceMode(e.currentTarget.checked)}
            />
            <Button onClick={() => mutation.mutate()} loading={mutation.isPending}>
              Save
            </Button>
          </Stack>
        )}
      </Card>
    </PageContainer>
  );
}
