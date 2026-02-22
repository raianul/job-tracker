"use client";

import { Button, Card, Stack, Text } from "@mantine/core";
import { getApiUrl } from "@/lib/api";
import { setStoredToken } from "@/lib/auth";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function LoginForm() {
  const { setToken, refetchUser } = useAuth();
  const router = useRouter();
  const [devLoading, setDevLoading] = useState(false);

  const handleDevLogin = async () => {
    setDevLoading(true);
    try {
      const res = await fetch(getApiUrl("/api/auth/dev-login"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: "dev@example.com" }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setStoredToken(data.access_token);
      setToken(data.access_token);
      await refetchUser();
      router.replace("/dashboard");
    } catch {
      setDevLoading(false);
    }
  };

  return (
    <Card withBorder shadow="md" p={30} mt={30} radius="md" maw={400} mx="auto">
      <Text size="lg" fw={600} mb="md">
        Sign in to Job Tracker
      </Text>
      <Stack gap="md">
        <Button
          component="a"
          href={getApiUrl("/api/auth/google")}
          variant="filled"
          fullWidth
        >
          Continue with Google
        </Button>
        <Button
          component="a"
          href={getApiUrl("/api/auth/linkedin")}
          variant="light"
          fullWidth
        >
          Continue with LinkedIn
        </Button>
        {process.env.NEXT_PUBLIC_DEV_LOGIN_ENABLED === "true" && (
          <Button
            variant="subtle"
            fullWidth
            onClick={handleDevLogin}
            loading={devLoading}
          >
            Dev login (no OAuth)
          </Button>
        )}
      </Stack>
    </Card>
  );
}
