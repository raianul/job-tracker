"use client";

import { Button, Card, Group, Stack, Text, Textarea, TextInput } from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { getApiUrl } from "../../../../lib/api";
import { getAuthHeaders } from "../../../../lib/auth";
import { PageContainer } from "@/components/PageContainer/PageContainer";

export default function NewApplicationPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [step, setStep] = useState(1);
  const [url, setUrl] = useState("");
  const [fetched, setFetched] = useState<{
    title: string | null;
    company: string | null;
    description: string | null;
    source_domain: string | null;
    fetch_error?: string | null;
  } | null>(null);
  const [appliedAt, setAppliedAt] = useState<Date | null>(new Date());
  const [formTitle, setFormTitle] = useState("");
  const [formCompany, setFormCompany] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [loadingFetch, setLoadingFetch] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);

  const fetchJob = async () => {
    if (!url.trim()) return;
    setLoadingFetch(true);
    setFetchError(null);
    try {
      const res = await fetch(getApiUrl("/api/jobs/fetch"), {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail || data?.fetch_error || "Failed to fetch");
      setFetched(data);
      setFormTitle(data.title ?? "");
      setFormCompany(data.company ?? "");
      setFormDescription(data.description ?? "");
      setStep(2);
    } catch (e) {
      setFetchError(e instanceof Error ? e.message : "Failed to fetch");
    } finally {
      setLoadingFetch(false);
    }
  };

  const createMutation = useMutation({
    mutationFn: async () => {
      setCreateError(null);
      const res = await fetch(getApiUrl("/api/applications"), {
        method: "POST",
        headers: { "Content-Type": "application/json", ...getAuthHeaders() },
        body: JSON.stringify({
          source_url: url,
          applied_at: appliedAt?.toISOString().slice(0, 10),
          status: "applied",
          ...(fetched && {
            title: formTitle.trim() || null,
            company: formCompany.trim() || null,
            description: formDescription.trim() || null,
            source_domain: fetched.source_domain,
          }),
        }),
      });
      const text = await res.text();
      if (!res.ok) {
        let message = text;
        try {
          const json = JSON.parse(text);
          if (json.detail) message = typeof json.detail === "string" ? json.detail : json.detail.join?.(" ") ?? text;
        } catch {
          /* use text as message */
        }
        throw new Error(message);
      }
      return text ? JSON.parse(text) : null;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
      queryClient.invalidateQueries({ queryKey: ["upcoming-interviews"] });
      router.push("/applications");
    },
    onError: (err: Error) => {
      setCreateError(err.message);
    },
  });

  return (
    <PageContainer title="Add application">
      <Card withBorder maw={500}>
        {step === 1 && (
          <Stack gap="md">
            <Text size="sm" c="dimmed">
              Step 1: Paste the job posting URL. We’ll try to extract title and company.
            </Text>
            <TextInput
              label="Job posting URL"
              placeholder="https://..."
              value={url}
              onChange={(e) => setUrl(e.currentTarget.value)}
            />
            {fetchError && (
              <Text size="sm" c="red">
                {fetchError}
              </Text>
            )}
            <Button onClick={fetchJob} loading={loadingFetch}>
              Fetch and continue
            </Button>
          </Stack>
        )}
        {step === 2 && (
          <Stack gap="md">
            <Text size="sm" c="dimmed">
              Step 2: When did you apply?
            </Text>
            {fetched && (
              <>
                {fetched.fetch_error ? (
                  <>
                    <Text size="sm" c="orange.7" mb="xs">
                      {fetched.fetch_error}
                    </Text>
                    <Text size="sm" fw={500} c="dimmed" mb="xs">
                      Add details manually:
                    </Text>
                    <TextInput
                      label="Job title"
                      placeholder="e.g. Senior Front-end Developer"
                      value={formTitle}
                      onChange={(e) => setFormTitle(e.currentTarget.value)}
                      required
                    />
                    <TextInput
                      label="Company"
                      placeholder="e.g. Perfect Vision"
                      value={formCompany}
                      onChange={(e) => setFormCompany(e.currentTarget.value)}
                    />
                    <Textarea
                      label="Description"
                      placeholder="Paste or type job description (optional)"
                      value={formDescription}
                      onChange={(e) => setFormDescription(e.currentTarget.value)}
                      minRows={3}
                    />
                  </>
                ) : (
                  <Card withBorder padding="sm" bg="gray.0">
                    <Text fw={600}>{fetched.title || "—"}</Text>
                    <Text size="sm" c="dimmed">
                      {fetched.company || "—"}
                      {fetched.source_domain && ` · ${fetched.source_domain}`}
                    </Text>
                  </Card>
                )}
              </>
            )}
            <DateInput
              label="Applied date"
              value={appliedAt}
              onChange={setAppliedAt}
              valueFormat="YYYY-MM-DD"
            />
            {createError && (
              <Text size="sm" c="red">
                {createError}
              </Text>
            )}
            <Group>
              <Button variant="subtle" onClick={() => setStep(1)}>
                Back
              </Button>
              <Button
                onClick={() => createMutation.mutate()}
                loading={createMutation.isPending}
                disabled={
                  !appliedAt ||
                  (!!fetched?.fetch_error && !formTitle.trim())
                }
              >
                Add application
              </Button>
            </Group>
          </Stack>
        )}
      </Card>
    </PageContainer>
  );
}
