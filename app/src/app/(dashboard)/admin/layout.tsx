"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    if (!user?.is_admin) {
      router.replace("/dashboard");
    }
  }, [loading, user, router]);

  if (loading || !user?.is_admin) {
    return null;
  }

  return <>{children}</>;
}
