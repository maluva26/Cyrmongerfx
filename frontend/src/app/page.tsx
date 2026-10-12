"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function Home() {
  const { status } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (status === "authenticated") router.replace("/dashboard");
    if (status === "anonymous") router.replace("/login");
  }, [router, status]);

  return (
    <main className="grid min-h-[60vh] place-items-center px-4">
      <p className="text-sm text-gray-600" aria-live="polite">
        {status === "loading" ? "Checking your session..." : "Opening your workspace..."}
      </p>
    </main>
  );
}
