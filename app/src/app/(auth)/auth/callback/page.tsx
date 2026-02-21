"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Center, Loader, Text } from "@mantine/core";
import { setStoredToken } from "@/lib/auth";
import { useAuth } from "@/contexts/AuthContext";

export default function AuthCallbackPage() {
  const router = useRouter();
  const { setToken, refetchUser } = useAuth();

  useEffect(() => {
    const hash = typeof window !== "undefined" ? window.location.hash : "";
    const params = new URLSearchParams(hash.replace(/^#/, ""));
    const token = params.get("token");
    if (token) {
      setStoredToken(token);
      setToken(token);
      refetchUser().then(() => router.replace("/dashboard"));
    } else {
      router.replace("/login");
    }
  }, [setToken, refetchUser, router]);

  return (
    <Center h="100vh">
      <Loader />
      <Text ml="md">Signing you in...</Text>
    </Center>
  );
}

