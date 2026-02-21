"use client";

import {
  Anchor,
  Button,
  Card,
  Group,
  Input,
  Modal,
  Stack,
  Text,
  Textarea,
  TextInput,
  Title,
} from "@mantine/core";
import { IconExternalLink } from "@tabler/icons-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { getApiUrl } from "../../../../lib/api";
import { getAuthHeaders } from "../../../../lib/auth";
import { PageContainer } from "@/components/PageContainer/PageContainer";
import { useEffect, useState } from "react";

interface Application {
  id: number;
  job_id: number;
  applied_at: string;
  status: string;
  notes: string | null;
  job: {
    id: number;
    source_url: string;
    title: string | null;
    company: string | null;
    description: string | null;
    location: string | null;
    source_domain: string | null;
  };
  interview_sessions: Array<{
    id: number;
    name: string;
    scheduled_at: string | null;
    sort_order: number | null;
    notes: string | null;
  }>;
}

const STATUS_OPTIONS = [
  { value: "applied", label: "Applied" },
  { value: "in_progress", label: "In progress" },
  { value: "rejected", label: "Rejected" },
  { value: "got_offer", label: "Got offer" },
] as const;

/** From each status, which statuses the user can transition to (one-way steps). */
const ALLOWED_NEXT_STATUS: Record<string, readonly string[]> = {
  applied: ["in_progress", "rejected"],
  in_progress: ["rejected", "got_offer"],
  rejected: [],
  got_offer: [],
};

export default function ApplicationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const id = Number(params.id);

  const { data: app, isLoading } = useQuery<Application>({
    queryKey: ["application", id],
    queryFn: async () => {
      const res = await fetch(getApiUrl(`/api/applications/${id}`), {
        headers: getAuthHeaders(),
      });
      if (!res.ok) throw new Error("Not found");
      return res.json();
    },
    enabled: !Number.isNaN(id),
  });

  const [status, setStatus] = useState(app?.status ?? "applied");
  const [rejectedModalOpen, setRejectedModalOpen] = useState(false);
  const [rejectedFeedback, setRejectedFeedback] = useState("");

  useEffect(() => {
    if (app?.status != null) setStatus(app.status);
  }, [app?.status]);

  const updateMutation = useMutation({
    mutationFn: async (updates: { status?: string; notes?: string }) => {
      const res = await fetch(getApiUrl(`/api/applications/${id}`), {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({
          status: updates.status,
          ...(updates.notes != null && { notes: updates.notes }),
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    },
    onSuccess: (data: Application) => {
      setStatus(data.status);
      setRejectedModalOpen(false);
      setRejectedFeedback("");
      queryClient.invalidateQueries({ queryKey: ["application", id] });
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
  });

  if (isLoading || !app) {
    return (
      <PageContainer title="Application">
        <Text c="dimmed">Loading...</Text>
      </PageContainer>
    );
  }

  const job = app.job;

  return (
    <PageContainer>
      <Stack gap="lg">
        <Card withBorder padding="lg">
          <Title order={5} mb="sm">{job?.title || "—"}</Title>
          {job?.source_url && (
            <Anchor
              href={job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              size="xs"
              c="dimmed"
              mt="xs"
              inline
            >
              <Group gap={4} wrap="nowrap" display="inline-flex">
                {job.source_url}
                <IconExternalLink size={12} />
              </Group>
            </Anchor>
          )}
          <Text size="sm" mt="md">
            Applied: {new Date(app.applied_at).toLocaleDateString()}
            {" · "}
            {STATUS_OPTIONS.find((s) => s.value === status)?.label ?? status.replace("_", " ")}
          </Text>
          {status === "rejected" && app.notes && (
            <Text size="sm" c="dimmed" mt="xs" style={{ whiteSpace: "pre-wrap" }}>
              Feedback: {app.notes}
            </Text>
          )}
          <Group gap="xs" mt="md">
            {STATUS_OPTIONS.map(({ value, label }) => {
              const isCurrent = status === value;
              const canTransition =
                !isCurrent && ALLOWED_NEXT_STATUS[status]?.includes(value);
              return (
                <Button
                  key={value}
                  size="xs"
                  variant={isCurrent ? "filled" : "light"}
                  disabled={!canTransition}
                  onClick={() => {
                    if (!canTransition) return;
                    if (value === "rejected") {
                      setRejectedModalOpen(true);
                      return;
                    }
                    setStatus(value);
                    updateMutation.mutate({ status: value });
                  }}
                  loading={updateMutation.isPending}
                >
                  {label}
                </Button>
              );
            })}
          </Group>
        </Card>

        <Modal
          title="Overall interview feedback"
          opened={rejectedModalOpen}
          onClose={() => {
            setRejectedModalOpen(false);
            setRejectedFeedback("");
          }}
        >
          <Stack gap="md">
            <Text size="sm" c="dimmed">
              Add feedback before marking as Rejected. This note is required.
            </Text>
            <Textarea
              placeholder="e.g. No response after final round, feedback was..."
              value={rejectedFeedback}
              onChange={(e) => setRejectedFeedback(e.currentTarget.value)}
              minRows={3}
              autoFocus
            />
            <Group justify="flex-end" gap="xs">
              <Button
                variant="subtle"
                onClick={() => {
                  setRejectedModalOpen(false);
                  setRejectedFeedback("");
                }}
              >
                Cancel
              </Button>
              <Button
                disabled={!rejectedFeedback.trim()}
                loading={updateMutation.isPending}
                onClick={() => {
                  updateMutation.mutate({
                    status: "rejected",
                    notes: rejectedFeedback.trim(),
                  });
                }}
              >
                Confirm Rejected
              </Button>
            </Group>
          </Stack>
        </Modal>

        <Card withBorder padding="lg">
          <Text fw={600} mb="sm">Interview sessions</Text>
          {app.interview_sessions.length === 0 ? (
            <Text size="sm" c="dimmed">
              {status === "applied" || status === "in_progress"
                ? "No sessions yet. Add one below."
                : "No sessions."}
            </Text>
          ) : (
            <Stack gap="sm">
              {app.interview_sessions.map((s) => (
                <Stack key={s.id} gap={2}>
                  <Group justify="space-between">
                    <Text size="sm" fw={500}>{s.name}</Text>
                    <Text size="xs" c="dimmed">
                      {s.scheduled_at
                        ? new Date(s.scheduled_at).toLocaleString()
                        : "—"}
                    </Text>
                  </Group>
                  {s.notes && (
                    <Text size="xs" c="dimmed" style={{ whiteSpace: "pre-wrap" }}>
                      {s.notes}
                    </Text>
                  )}
                </Stack>
              ))}
            </Stack>
          )}
          {(status === "applied" || status === "in_progress") && (
            <AddSessionForm applicationId={id} />
          )}
        </Card>
      </Stack>
    </PageContainer>
  );
}

function toDatetimeLocal(d: Date): string {
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function AddSessionForm({ applicationId }: { applicationId: number }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [scheduledAt, setScheduledAt] = useState<Date | null>(null);
  const [notes, setNotes] = useState("");
  const minDatetime = new Date(new Date().setHours(0, 0, 0, 0));

  const mutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(
        getApiUrl(`/api/applications/${applicationId}/sessions`),
        {
          method: "POST",
          headers: { "Content-Type": "application/json", ...getAuthHeaders() },
          body: JSON.stringify({
            name: name || "Interview",
            scheduled_at: scheduledAt?.toISOString() ?? null,
            sort_order: 0,
            notes: notes.trim() || null,
          }),
        }
      );
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["application", applicationId] });
      queryClient.invalidateQueries({ queryKey: ["upcoming-interviews"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
      setName("");
      setScheduledAt(null);
      setNotes("");
    },
  });

  return (
    <Stack gap="sm" mt="md">
      <Text size="sm" fw={500}>Add session</Text>
      <Group align="flex-end">
        <TextInput
          placeholder="e.g. HR Interview, Technical round 1"
          value={name}
          onChange={(e) => setName(e.currentTarget.value)}
          style={{ minWidth: 200 }}
        />
        <Input
          component="input"
          type="datetime-local"
          size="sm"
          value={scheduledAt ? toDatetimeLocal(scheduledAt) : ""}
          min={toDatetimeLocal(minDatetime)}
          onChange={(e) => {
            const v = e.currentTarget.value;
            setScheduledAt(v ? new Date(v) : null);
          }}
          style={{ width: 200 }}
        />
        <Button onClick={() => mutation.mutate()} loading={mutation.isPending}>
          Add
        </Button>
      </Group>
      <Textarea
        placeholder="Notes (optional)"
        value={notes}
        onChange={(e) => setNotes(e.currentTarget.value)}
        minRows={2}
        size="sm"
      />
    </Stack>
  );
}
