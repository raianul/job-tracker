"use client";

import { Anchor, Card, Grid, GridCol, Group, Text } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { getApiUrl } from "@/lib/api";
import { getAuthHeaders } from "@/lib/auth";

interface UpcomingItem {
  application_id: number;
  session_id: number;
  session_name: string;
  scheduled_at: string | null;
  job_title: string | null;
  company: string | null;
}

interface DashboardStats {
  applied: number;
  rejected: number;
  success: number;
}

export function DashboardContent() {
  const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: async () => {
      const res = await fetch(getApiUrl("/api/dashboard/stats"), {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error("Failed to fetch");
      return res.json();
    },
  });

  const { data: upcoming = [], isLoading } = useQuery<UpcomingItem[]>({
    queryKey: ["upcoming-interviews"],
    queryFn: async () => {
      const res = await fetch(getApiUrl("/api/dashboard/upcoming-interviews"), {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error("Failed to fetch");
      return res.json();
    },
  });

  return (
    <Grid>
      <GridCol span={12}>
        <Group gap="md" mb="lg">
          <Card withBorder padding="md" radius="md" style={{ minWidth: 120 }}>
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
              Job Applied
            </Text>
            <Text size="xl" fw={700}>
              {statsLoading ? "—" : (stats?.applied ?? 0)}
            </Text>
            <Text size="xs" c="dimmed">Applications sent</Text>
          </Card>
          <Card withBorder padding="md" radius="md" style={{ minWidth: 120 }}>
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
              Rejected
            </Text>
            <Text size="xl" fw={700}>
              {statsLoading ? "—" : (stats?.rejected ?? 0)}
            </Text>
            <Text size="xs" c="dimmed">Rejections received</Text>
          </Card>
          <Card withBorder padding="md" radius="md" style={{ minWidth: 120 }}>
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>
              Success
            </Text>
            <Text size="xl" fw={700}>
              {statsLoading ? "—" : (stats?.success ?? 0)}
            </Text>
            <Text size="xs" c="dimmed">Offers received</Text>
          </Card>
        </Group>
      </GridCol>
      <GridCol span={12}>
        <Card withBorder padding="lg" radius="md">
          <Text size="lg" fw={600} mb="md">
            Your next interviews
          </Text>
          {isLoading ? (
            <Text c="dimmed">Loading...</Text>
          ) : upcoming.length === 0 ? (
            <Text c="dimmed">
              No upcoming interviews.{" "}
              <Anchor href="/applications">View your applications</Anchor> to add
              interview sessions.
            </Text>
          ) : (
            <Group gap="md">
              {upcoming.map((item) => (
                <Anchor
                  key={`${item.application_id}-${item.session_id}`}
                  href={`/applications/${item.application_id}`}
                  underline="never"
                >
                  <Card withBorder padding="md" radius="md" style={{ minWidth: 260 }}>
                    <Text fw={600}>{item.session_name}</Text>
                    <Text size="sm" c="dimmed">
                      {[item.job_title, item.company].filter(Boolean).join(" · ") || "—"}
                    </Text>
                    {item.scheduled_at && (
                      <Text size="xs" c="dimmed" mt="xs">
                        {new Date(item.scheduled_at).toLocaleString()}
                      </Text>
                    )}
                  </Card>
                </Anchor>
              ))}
            </Group>
          )}
        </Card>
      </GridCol>
    </Grid>
  );
}
